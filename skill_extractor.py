import re
import pandas as pd

class SkillExtractor:
    def __init__(self, skill_csv_path: str = "data/skill_dictionary.csv"):
        self.skills_df = pd.read_csv(skill_csv_path)
        # Sort skills by length descending to match multi-word skills first
        self.skills_df['skill_clean'] = self.skills_df['skill'].str.lower()
        self.skills_df = self.skills_df.sort_values(by='skill_clean', key=lambda x: x.str.len(), ascending=False)

    def extract_skills(self, cleaned_text: str) -> dict:
        """
        Extracts skills present in the text and categorizes them.
        """
        found_skills = set()
        
        for _, row in self.skills_df.iterrows():
            skill = row['skill_clean']
            # Escape regex characters except + and #
            escaped_skill = re.escape(skill)
            pattern = r'(?<![a-zA-Z0-9])' + escaped_skill + r'(?![a-zA-Z0-9])'
            
            if re.search(pattern, cleaned_text):
                found_skills.add(skill)
                
        # Group into categories
        categorized = {}
        matched_rows = self.skills_df[self.skills_df['skill_clean'].isin(found_skills)]
        
        for category, group in matched_rows.groupby('category'):
            categorized[category] = list(group['skill'].unique())
            
        return {
            "all_skills": list(found_skills),
            "categorized_skills": categorized
        }