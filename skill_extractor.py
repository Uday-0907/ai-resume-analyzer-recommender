import re
import pandas as pd


class SkillExtractor:
    def __init__(self, skill_csv_path: str = "data/skill_dictionary.csv"):
        self.skills_df = pd.read_csv(skill_csv_path)
        # Ensure clean strings
        self.skills_df['skill'] = self.skills_df['skill'].astype(str).str.strip()
        self.skills_df['category'] = self.skills_df['category'].astype(str).str.strip().str.lower()
        self.skills_df['skill_clean'] = self.skills_df['skill'].str.lower()
        
        # Sort skills by length descending to match multi-word skills first
        self.skills_df = self.skills_df.sort_values(
            by='skill_clean', key=lambda x: x.str.len(), ascending=False
        )

    def extract_skills(self, cleaned_text: str) -> dict:
        """
        Extracts skills present in the text and categorizes them.
        Returns clean, deduplicated skill lists per category.
        """
        if not cleaned_text:
            return {"all_skills": [], "categorized_skills": {}}

        found_skills = set()
        
        for _, row in self.skills_df.iterrows():
            skill = row['skill_clean']
            # Escape regex characters except + and #
            escaped_skill = re.escape(skill)
            pattern = r'(?<![a-zA-Z0-9])' + escaped_skill + r'(?![a-zA-Z0-9])'
            
            if re.search(pattern, cleaned_text):
                found_skills.add(skill)
                
        # Group into categories with clean deduplicated lists
        categorized = {}
        matched_rows = self.skills_df[self.skills_df['skill_clean'].isin(found_skills)]
        
        for category, group in matched_rows.groupby('category'):
            cat_key = str(category).strip()
            # Clean unique skills
            skills_in_cat = []
            seen = set()
            for s in group['skill_clean']:
                s_str = s.strip()
                if s_str and s_str not in seen:
                    seen.add(s_str)
                    skills_in_cat.append(s_str)
            if skills_in_cat:
                categorized[cat_key] = sorted(skills_in_cat)
            
        return {
            "all_skills": sorted(list(found_skills)),
            "categorized_skills": categorized
        }