import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class JobMatcher:
    def __init__(self, job_roles_csv_path: str = "data/job_roles.csv"):
        self.jobs_df = pd.read_csv(job_roles_csv_path)

    def compute_match_scores(self, cleaned_resume_text: str) -> list:
        """
        Computes TF-IDF cosine similarity between resume text and job roles.
        """
        corpus = [cleaned_resume_text] + self.jobs_df['description'].tolist()
        
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # Compare resume (index 0) with each job description
        cosine_sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        results = []
        for idx, score in enumerate(cosine_sims):
            role_name = self.jobs_df.iloc[idx]['job_role']
            required_skills_str = self.jobs_df.iloc[idx]['required_skills']
            req_list = [s.strip().lower() for s in required_skills_str.split(',')]
            
            results.append({
                "job_role": role_name,
                "match_score": round(float(score) * 100, 2),
                "required_skills": req_list
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results