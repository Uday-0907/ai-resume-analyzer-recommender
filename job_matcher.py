import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class JobMatcher:
    def __init__(self, job_roles_csv_path: str = "data/job_roles.csv"):
        self.jobs_df = pd.read_csv(job_roles_csv_path)

    def compute_match_scores(self, cleaned_resume_text: str, extracted_skills=None) -> list:
        """
        Computes a match score for each job role by blending two signals:
          1. TF-IDF cosine similarity between the resume text and the role description
             (captures overall contextual/semantic overlap).
          2. Skill-overlap ratio between skills found in the resume and the role's
             required skills (captures concrete, explainable skill coverage).

        Blending avoids two known weaknesses of using either signal alone:
          - Pure TF-IDF similarity against a short role description tends to produce
            compressed, low, hard-to-interpret scores (e.g. single digits).
          - Pure skill-overlap ignores broader resume context (projects, experience
            phrasing) that TF-IDF can pick up on.
        """
        extracted_skills = set(s.lower() for s in (extracted_skills or []))
        corpus = [cleaned_resume_text] + self.jobs_df['description'].tolist()

        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)

        # Compare resume (index 0) with each job description
        cosine_sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        results = []
        for idx, tfidf_score in enumerate(cosine_sims):
            role_name = self.jobs_df.iloc[idx]['job_role']
            required_skills_str = self.jobs_df.iloc[idx]['required_skills']
            req_list = [s.strip().lower() for s in required_skills_str.split(',')]

            req_set = set(req_list)
            matched = extracted_skills.intersection(req_set)
            skill_overlap_ratio = (len(matched) / len(req_set)) if req_set else 0.0

            # Weighted blend: skill overlap is the more explainable, trusted signal,
            # so it carries more weight; TF-IDF adds broader contextual nuance.
            blended_score = (0.7 * skill_overlap_ratio) + (0.3 * float(tfidf_score))

            results.append({
                "job_role": role_name,
                "match_score": round(blended_score * 100, 2),
                "tfidf_score": round(float(tfidf_score) * 100, 2),
                "skill_overlap_score": round(skill_overlap_ratio * 100, 2),
                "required_skills": req_list
            })

        # Rank by blended score descending
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results
