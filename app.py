import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

from text_cleaner import clean_text
from resume_parser import parse_resume
from skill_extractor import SkillExtractor
from job_matcher import JobMatcher
from roadmap_generator import analyze_skill_gaps, generate_learning_roadmap
from ai_feedback import is_ai_feedback_available, generate_ai_feedback

load_dotenv()

st.set_page_config(
    page_title="AI Resume Analyzer & Job Recommender",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Analyzer & Job Recommendation System")
st.caption("Educational resume analysis tool focused on skills and project matching.")

# Responsible AI Notice (Module 12)
st.info(
    "🔒 **Responsible AI Statement:** This tool is a guidance aid, not an automatic hiring or "
    "rejection decision. It evaluates only job-related skills, education, projects, and relevant "
    "experience. Personal attributes — gender, age, religion, nationality, photographs, marital "
    "status, and disability — are never scored. Match scores are estimates to help you learn, "
    "not recruiter decisions, and a missing keyword does not always mean missing ability. "
    "Uploaded resumes are processed in memory only and are not stored."
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
    
    # Calculate Recommendations (blends skill overlap + TF-IDF similarity)
    rankings = job_matcher.compute_match_scores(cleaned_resume, extracted_skills)
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
        st.caption(
            f"Skill overlap: {target_info['skill_overlap_score']}% · "
            f"Contextual similarity: {target_info['tfidf_score']}% "
            "(blended 70/30 into the score above)"
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

    # Optional Advanced Feature (PDF Section 13): LLM-generated feedback.
    # Hidden entirely if no GEMINI_API_KEY is set — the app never requires it.
    ai_feedback_text = None
    if is_ai_feedback_available():
        st.markdown("---")
        st.subheader("🤖 AI-Generated Feedback (optional)")
        if st.button("Generate personalized feedback"):
            with st.spinner("Asking Gemini for feedback..."):
                ai_feedback_text = generate_ai_feedback(
                    target_role=selected_role_name,
                    matching_skills=gap_analysis["matching_skills"],
                    missing_skills=gap_analysis["missing_skills"],
                    match_score=target_info["match_score"],
                )
            if ai_feedback_text:
                st.write(ai_feedback_text)

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

    if ai_feedback_text:
        report_content += f"\n\nAI-GENERATED FEEDBACK:\n{ai_feedback_text}"

    st.download_button(
        label="📥 Download Analysis Report",
        data=report_content,
        file_name="resume_analysis_report.txt",
        mime="text/plain"
    )

else:
    st.info("👈 Please upload a resume PDF or DOCX file to start the analysis.")