import os
import math
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer
    # Suppress verbose warnings during inference
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    _ST_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
except Exception:
    _ST_MODEL = None


# Core/must-have skills per role
CORE_SKILLS_MAP = {
    "Data Analyst": {"python", "sql", "excel", "pandas", "statistics"},
    "Machine Learning Engineer": {"python", "ml", "scikit-learn", "numpy", "pandas"},
    "AI Engineer": {"python", "deep learning", "llm", "rag", "pytorch"},
    "NLP Engineer": {"python", "nlp", "transformers", "hugging face", "bert"},
    "Computer Vision Engineer": {"python", "opencv", "cnn", "yolo", "pytorch", "deep learning"},
    "Data Engineer": {"python", "sql", "spark", "airflow", "aws", "postgresql"},
    "Full Stack Developer": {"python", "javascript", "react", "node.js", "sql"},
    "Cloud & DevOps Engineer": {"aws", "azure", "docker", "kubernetes", "linux"},
}

# Related skills taxonomy for partial matching credit
RELATED_SKILLS_MAP = {
    "sql": {"postgresql", "mysql", "sqlite", "oracle", "snowflake", "bigquery", "nosql"},
    "postgresql": {"sql", "mysql", "sqlite", "databases"},
    "deep learning": {"pytorch", "tensorflow", "keras", "cnn"},
    "pytorch": {"deep learning", "tensorflow", "keras"},
    "tensorflow": {"deep learning", "pytorch", "keras"},
    "ml": {"machine learning", "scikit-learn", "deep learning"},
    "machine learning": {"ml", "scikit-learn", "deep learning"},
    "nlp": {"transformers", "spacy", "bert", "gpt", "hugging face"},
    "transformers": {"nlp", "hugging face", "bert", "gpt"},
    "hugging face": {"transformers", "nlp", "bert"},
    "bert": {"nlp", "transformers", "llm"},
    "gpt": {"llm", "nlp", "rag"},
    "llm": {"rag", "gpt", "deep learning"},
    "rag": {"llm", "apis", "python"},
    "excel": {"power bi", "tableau", "statistics"},
    "power bi": {"tableau", "excel", "data analysis"},
    "tableau": {"power bi", "excel", "data analysis"},
    "apis": {"fastapi", "flask", "rest api"},
    "rest api": {"fastapi", "flask", "apis"},
    "fastapi": {"rest api", "apis", "flask"},
    "flask": {"django", "fastapi", "rest api"},
    "react": {"javascript", "typescript", "node.js"},
    "node.js": {"javascript", "typescript", "react"},
    "javascript": {"typescript", "react", "node.js"},
    "docker": {"kubernetes", "linux"},
    "kubernetes": {"docker", "cloud", "aws", "azure"},
    "aws": {"azure", "gcp", "cloud"},
    "azure": {"aws", "gcp", "cloud"},
    "gcp": {"aws", "azure", "cloud"},
    "spark": {"airflow", "python", "sql", "bigquery"},
    "airflow": {"spark", "python"},
}


class JobMatcher:
    def __init__(self, job_roles_csv_path: str = "data/job_roles.csv"):
        self.jobs_df = pd.read_csv(job_roles_csv_path)
        self.st_model = _ST_MODEL

    def _get_skill_credit(self, req_skill: str, extracted_skills: set) -> float:
        """
        Determines skill credit:
          1.0 for exact keyword match
          0.6 for semantically related / taxonomy match
          0.0 otherwise
        """
        if req_skill in extracted_skills:
            return 1.0

        # Check known domain taxonomy
        related = RELATED_SKILLS_MAP.get(req_skill, set())
        if related.intersection(extracted_skills):
            return 0.6

        # Check embedding similarity if SentenceTransformer is available
        if self.st_model and extracted_skills:
            try:
                cand_list = list(extracted_skills)
                req_emb = self.st_model.encode([req_skill])
                cand_embs = self.st_model.encode(cand_list)
                sims = cosine_similarity(req_emb, cand_embs)[0]
                max_sim = float(np.max(sims))
                if max_sim >= 0.65:
                    return 0.6
            except Exception:
                pass

        return 0.0

    def compute_match_scores(self, cleaned_resume_text: str, extracted_skills=None) -> list:
        """
        Computes match score for each job role by weighting core skills higher
        than nice-to-have skills, incorporating semantic similarity for related skills,
        and blending with contextual text similarity.
        """
        extracted_skills = set(s.lower().strip() for s in (extracted_skills or []))
        
        # Contextual similarity (Sentence Transformers or TF-IDF fallback)
        context_scores = []
        if self.st_model and cleaned_resume_text.strip():
            try:
                corpus = [cleaned_resume_text] + self.jobs_df['description'].tolist()
                corpus_embs = self.st_model.encode(corpus)
                sims = cosine_similarity(corpus_embs[0:1], corpus_embs[1:]).flatten()
                context_scores = [max(0.0, min(1.0, float(s))) for s in sims]
            except Exception:
                context_scores = []

        if not context_scores:
            corpus = [cleaned_resume_text] + self.jobs_df['description'].tolist()
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(corpus)
            sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            context_scores = [max(0.0, min(1.0, float(s))) for s in sims]

        results = []
        for idx, context_sim in enumerate(context_scores):
            role_name = self.jobs_df.iloc[idx]['job_role']
            required_skills_str = self.jobs_df.iloc[idx]['required_skills']
            req_list = [s.strip().lower() for s in required_skills_str.split(',')]

            # Identify core skills
            role_core = CORE_SKILLS_MAP.get(role_name)
            if role_core is None:
                half_idx = math.ceil(len(req_list) / 2)
                role_core = set(req_list[:half_idx])

            total_weight = 0.0
            earned_weight = 0.0

            for s in req_list:
                weight = 2.5 if s in role_core else 1.0
                total_weight += weight
                credit = self._get_skill_credit(s, extracted_skills)
                earned_weight += weight * credit

            weighted_skill_ratio = (earned_weight / total_weight) if total_weight > 0 else 0.0
            weighted_skill_score = weighted_skill_ratio * 100.0

            # Context similarity percentage
            context_pct = context_sim * 100.0

            # Blended score: 80% weighted skill match + 20% contextual relevance
            # This ensures candidates with core skills receive a strong score (e.g. 65-85%)
            # without artificial score compression.
            if extracted_skills:
                blended_score = (0.80 * weighted_skill_score) + (0.20 * context_pct)
            else:
                blended_score = context_pct * 0.5  # minimal if no skills found

            blended_score = max(0.0, min(100.0, blended_score))

            results.append({
                "job_role": role_name,
                "match_score": round(blended_score, 2),
                "tfidf_score": round(context_pct, 2),
                "skill_overlap_score": round(weighted_skill_score, 2),
                "required_skills": req_list
            })

        # Rank by match score descending
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results
