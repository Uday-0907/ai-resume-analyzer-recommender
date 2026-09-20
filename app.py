import streamlit as st
import pandas as pd
import plotly.express as px

from text_cleaner import clean_text
from resume_parser import parse_resume
from skill_extractor import SkillExtractor
from job_matcher import JobMatcher
from roadmap_generator import analyze_skill_gaps, generate_learning_roadmap

st.set_page_config(
    page_title="AI Resume Analyzer & Job Recommender",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Analyzer & Job Recommendation System")
st.caption("Educational resume analysis tool focused on skills and project matching.")

# Responsible AI Notice (Module 12)
st.info(
    "🔒 **Responsible AI Statement:** This tool strictly evaluates technical skills and experience. "
    "Personal attributes (gender, age, race, photos, etc.) are excluded from scoring."
)

# Sidebar Inputs
st.sidebar.header("1. Upload Resume")
uploaded_file = st.sidebar.file_uploader("Upload PDF or DOCX file", type=["pdf", "docx"])

# Initialize modules
@st.cache_resource
def load_components():
    extractor = SkillExtractor("data/skill_dictionary.csv")
    matcher = JobMatcher("data/job_roles.csv")
    return extractor, matcher

skill_extractor, job_matcher = load_components()

if uploaded_file is not None:
    # File Validation (Module 1)
    if uploaded_file.size > 5 * 1024 * 1024:
        st.error("File size exceeds 5MB limit.")
        st.stop()
        
    st.sidebar.success(f"File loaded: {uploaded_file.name}")

    # Process File
    raw_text = parse_resume(uploaded_file)
    cleaned_resume = clean_text(raw_text)
    
    # Extract Skills
    skill_data = skill_extractor.extract_skills(cleaned_resume)
    extracted_skills = skill_data["all_skills"]
    categorized = skill_data["categorized_skills"]
    
    # Calculate Recommendations
    rankings = job_matcher.compute_match_scores(cleaned_resume)
    job_roles_list = [r["job_role"] for r in rankings]
    
    st.sidebar.header("2. Target Role Selection")
    selected_role_name = st.sidebar.selectbox("Select Target Job Role:", job_roles_list)
    
    # Selected Role Data
    target_info = next(r for r in rankings if r["job_role"] == selected_role_name)
    gap_analysis = analyze_skill_gaps(extracted_skills, target_info["required_skills"])
    roadmap = generate_learning_roadmap(gap_analysis["missing_skills"])
    
    # UI Layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎯 Target Role Match")
        st.metric(
            label=f"Match Score for {selected_role_name}",
            value=f"{target_info['match_score']}%"
        )
        
        st.write("**Extracted Skills by Category:**")
        if categorized:
            for cat, s_list in categorized.items():
                st.write(f"- **{cat.title()}**: {', '.join(s_list)}")
        else:
            st.write("No matching skills found from dictionary.")

        st.subheader("🔍 Skill-Gap Analysis")
        st.write("✅ **Skills Found:**", ", ".join(gap_analysis["matching_skills"]) if gap_analysis["matching_skills"] else "None")
        st.write("❌ **Missing Skills:**", ", ".join(gap_analysis["missing_skills"]) if gap_analysis["missing_skills"] else "None")

    with col2:
        st.subheader("📊 Recommended Job Roles")
        df_rankings = pd.DataFrame(rankings)
        fig = px.bar(
            df_rankings, 
            x="match_score", 
            y="job_role", 
            orientation="h",
            title="Role Compatibility Score (%)",
            labels={"match_score": "Score (%)", "job_role": "Role"},
            color="match_score",
            color_continuous_scale="Blues"
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    
    st.subheader("🗺️ Learning Roadmap for Missing Skills")
    for step in roadmap:
        st.markdown(f"- {step}")

    # Section for Report Download
    st.markdown("---")
    report_content = f"""AI RESUME ANALYSIS REPORT
Target Role: {selected_role_name}
Match Score: {target_info['match_score']}%

Detected Skills: {', '.join(extracted_skills)}
Matching Skills: {', '.join(gap_analysis['matching_skills'])}
Missing Skills: {', '.join(gap_analysis['missing_skills'])}

RECOMMENDED LEARNING ROADMAP:
""" + "\n".join(roadmap)

    st.download_button(
        label="📥 Download Analysis Report",
        data=report_content,
        file_name="resume_analysis_report.txt",
        mime="text/plain"
    )

else:
    st.info("👈 Please upload a resume PDF or DOCX file to start the analysis.")