def analyze_skill_gaps(extracted_skills: list, target_required_skills: list) -> dict:
    """
    Identifies present and missing skills for a targeted role.
    """
    extracted_set = set(s.lower() for s in extracted_skills)
    required_set = set(s.lower() for s in target_required_skills)
    
    matching_skills = list(extracted_set.intersection(required_set))
    missing_skills = list(required_set - extracted_set)
    
    return {
        "matching_skills": matching_skills,
        "missing_skills": missing_skills
    }

def generate_learning_roadmap(missing_skills: list) -> list:
    """
    Generates a week-by-week learning roadmap based on missing skills.
    """
    if not missing_skills:
        return ["Great job! You possess all core skills required for this role."]
    
    roadmap = []
    for week, skill in enumerate(missing_skills, start=1):
        roadmap.append(f"Week {week}: Master fundamentals & hands-on projects for **{skill.title()}**")
        
    return roadmap