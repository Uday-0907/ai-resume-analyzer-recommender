import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# ── Responsible AI Banner ──────────────────────────────────────────────────────
st.info(
    "🔒 **Responsible AI Statement:** This tool is a guidance aid, not an automatic hiring or "
    "rejection decision. It evaluates **only** job-related skills, education, projects, and "
    "relevant experience. Personal attributes — gender, age, religion, nationality, photographs, "
    "marital status, and disability — are **never** scored. Match scores are estimates to help "
    "you learn, not recruiter decisions, and a missing keyword does not always mean missing "
    "ability. Uploaded resumes are processed **in memory only** and are **not stored** on disk."
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.header("1. Upload Resume")
uploaded_file = st.sidebar.file_uploader("Upload PDF or DOCX file", type=["pdf", "docx"])


# ── Module initialisation (cached) ────────────────────────────────────────────
@st.cache_resource
def load_components():
    extractor = SkillExtractor("data/skill_dictionary.csv")
    matcher = JobMatcher("data/job_roles.csv")
    return extractor, matcher


skill_extractor, job_matcher = load_components()

# ── Main logic ─────────────────────────────────────────────────────────────────
if uploaded_file is not None:

    # ── File Validation ────────────────────────────────────────────────────────
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

    # Extension check (belt-and-suspenders; uploader already filters, but
    # the underlying bytes are what we actually parse).
    allowed_extensions = {".pdf", ".docx"}
    file_ext = "." + uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""
    if file_ext not in allowed_extensions:
        st.error(
            f"❌ **Unsupported file type:** `{file_ext or 'unknown'}`. "
            "Please upload a `.pdf` or `.docx` resume file."
        )
        st.stop()

    # Size check
    if uploaded_file.size > MAX_FILE_SIZE_BYTES:
        st.error(
            f"❌ **File too large:** `{uploaded_file.size / (1024*1024):.1f} MB`. "
            "The maximum allowed size is **5 MB**. Please compress the file and retry."
        )
        st.stop()

    # Show validation metrics in sidebar
    st.sidebar.success(f"✅ File loaded: `{uploaded_file.name}`")
    with st.sidebar.expander("📋 File Metrics", expanded=False):
        st.write(f"**Name:** {uploaded_file.name}")
        st.write(f"**Type:** {file_ext.upper()}")
        st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")

    # ── Text Extraction & Cleaning ─────────────────────────────────────────────
    raw_text = parse_resume(uploaded_file)
    cleaned_resume = clean_text(raw_text)

    # ── Skill Extraction ───────────────────────────────────────────────────────
    skill_data = skill_extractor.extract_skills(cleaned_resume)
    extracted_skills = skill_data["all_skills"]
    categorized = skill_data["categorized_skills"]

    # ── Job Matching ───────────────────────────────────────────────────────────
    rankings = job_matcher.compute_match_scores(cleaned_resume, extracted_skills)
    job_roles_list = [r["job_role"] for r in rankings]

    st.sidebar.header("2. Target Role Selection")
    selected_role_name = st.sidebar.selectbox("Select Target Job Role:", job_roles_list)

    # ── Selected Role Analysis ─────────────────────────────────────────────────
    target_info = next(r for r in rankings if r["job_role"] == selected_role_name)
    gap_analysis = analyze_skill_gaps(extracted_skills, target_info["required_skills"])
    roadmap = generate_learning_roadmap(gap_analysis["missing_skills"])

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — Match Score + Extracted Skills
    # ═══════════════════════════════════════════════════════════════════════════
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 Target Role Match")

        # Gauge chart for match score
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=target_info["match_score"],
            number={"suffix": "%", "font": {"size": 36}},
            title={"text": f"Match Score — {selected_role_name}", "font": {"size": 14}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": "#1f77b4"},
                "steps": [
                    {"range": [0, 40],  "color": "#ffcccc"},
                    {"range": [40, 70], "color": "#fff3cc"},
                    {"range": [70, 100],"color": "#ccffcc"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": target_info["match_score"],
                },
            },
        ))
        gauge_fig.update_layout(height=280, margin=dict(t=50, b=10, l=20, r=20))
        st.plotly_chart(gauge_fig, use_container_width=True)

        st.caption(
            f"Skill overlap: **{target_info['skill_overlap_score']}%** · "
            f"Contextual (TF-IDF) similarity: **{target_info['tfidf_score']}%** "
            "*(blended 70 / 30)*"
        )

        # Extracted skills grouped by category
        st.subheader("🧠 Extracted Skills by Category")
        if categorized:
            for cat, s_list in categorized.items():
                st.markdown(f"**{cat.replace('_', ' ').title()}:** {', '.join(s_list)}")
        else:
            st.warning("No skills matched from the dictionary. Check that the resume text was extracted correctly.")

    with col2:
        # ── Top 3 Recommended Roles ────────────────────────────────────────────
        st.subheader("🏆 Top 3 Recommended Roles")
        top3 = rankings[:3]
        medals = ["🥇", "🥈", "🥉"]
        for medal, role in zip(medals, top3):
            with st.container():
                st.metric(
                    label=f"{medal} {role['job_role']}",
                    value=f"{role['match_score']}%",
                    help=(
                        f"Skill overlap: {role['skill_overlap_score']}% | "
                        f"TF-IDF: {role['tfidf_score']}%"
                    ),
                )

        st.markdown("---")

        # ── Full Role Rankings Bar Chart ───────────────────────────────────────
        st.subheader("📊 All Role Compatibility Scores")
        df_rankings = pd.DataFrame(rankings)
        fig = px.bar(
            df_rankings,
            x="match_score",
            y="job_role",
            orientation="h",
            title="Role Compatibility Score (%)",
            labels={"match_score": "Score (%)", "job_role": "Role"},
            color="match_score",
            color_continuous_scale="Blues",
            text="match_score",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=350)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — Skill-Gap Analysis
    # ═══════════════════════════════════════════════════════════════════════════
    st.subheader("🔍 Skill-Gap Analysis")
    gap_col1, gap_col2 = st.columns(2)

    with gap_col1:
        st.markdown("### ✅ Skills Found")
        if gap_analysis["matching_skills"]:
            for s in sorted(gap_analysis["matching_skills"]):
                st.markdown(f"- {s.title()}")
        else:
            st.write("_None matched for this role._")

    with gap_col2:
        st.markdown("### ❌ Missing Skills")
        if gap_analysis["missing_skills"]:
            for s in sorted(gap_analysis["missing_skills"]):
                st.markdown(f"- {s.title()}")
        else:
            st.success("You have all the core skills for this role!")

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — 4-Week Learning Roadmap
    # ═══════════════════════════════════════════════════════════════════════════
    st.subheader("🗺️ 4-Week Learning Roadmap")
    for line in roadmap:
        if line.startswith("###"):
            st.markdown(line)
        elif line == "":
            st.markdown(" ")
        else:
            st.markdown(line)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 4 — Optional AI Feedback
    # ═══════════════════════════════════════════════════════════════════════════
    ai_feedback_text = None
    if is_ai_feedback_available():
        st.markdown("---")
        st.subheader("🤖 AI-Generated Feedback (optional)")
        if st.button("Generate personalised feedback"):
            with st.spinner("Asking Gemini for feedback…"):
                ai_feedback_text = generate_ai_feedback(
                    target_role=selected_role_name,
                    matching_skills=gap_analysis["matching_skills"],
                    missing_skills=gap_analysis["missing_skills"],
                    match_score=target_info["match_score"],
                )
            if ai_feedback_text:
                st.write(ai_feedback_text)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 5 — Downloadable Analysis Report
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.subheader("📥 Download Analysis Report")

    top3_lines = "\n".join(
        f"  {i+1}. {r['job_role']} — {r['match_score']}%"
        for i, r in enumerate(top3)
    )

    report_content = f"""AI RESUME ANALYSIS REPORT
{"=" * 60}
Generated by: AI Resume Analyzer & Job Recommendation System
Responsible AI: Scores based on skills/projects/experience only.
             Personal demographics are never evaluated.
{"=" * 60}

TARGET ROLE   : {selected_role_name}
MATCH SCORE   : {target_info['match_score']}%
  ↳ Skill overlap     : {target_info['skill_overlap_score']}%
  ↳ TF-IDF similarity : {target_info['tfidf_score']}%

{"─" * 60}
TOP 3 RECOMMENDED ROLES
{"─" * 60}
{top3_lines}

{"─" * 60}
EXTRACTED SKILLS (all categories)
{"─" * 60}
{', '.join(sorted(extracted_skills)) if extracted_skills else 'None detected'}

{"─" * 60}
SKILL-GAP ANALYSIS FOR: {selected_role_name}
{"─" * 60}
Skills Found  : {', '.join(sorted(gap_analysis['matching_skills'])) if gap_analysis['matching_skills'] else 'None'}
Missing Skills: {', '.join(sorted(gap_analysis['missing_skills'])) if gap_analysis['missing_skills'] else 'None'}

{"─" * 60}
4-WEEK LEARNING ROADMAP
{"─" * 60}
""" + "\n".join(
        line.replace("**", "").replace("*", "").replace("###", ">>")
        for line in roadmap
    )

    if ai_feedback_text:
        report_content += f"\n\n{'─' * 60}\nAI-GENERATED FEEDBACK\n{'─' * 60}\n{ai_feedback_text}"

    st.download_button(
        label="📥 Download Analysis Report (.txt)",
        data=report_content,
        file_name=f"resume_analysis_{selected_role_name.replace(' ', '_').lower()}.txt",
        mime="text/plain",
    )

else:
    st.info("👈 Please upload a resume PDF or DOCX file from the sidebar to start the analysis.")
    st.markdown("""
    **What this tool does:**
    - 📄 Parses PDF and DOCX resumes in memory (never stored on disk)
    - 🧠 Extracts and categorises technical skills from your resume
    - 📊 Scores compatibility against 8 job roles using TF-IDF + skill overlap
    - 🏆 Recommends your Top 3 best-matching roles
    - 🔍 Identifies skill gaps for your chosen target role
    - 🗺️ Generates a personalised 4-week learning roadmap
    - 📥 Exports the full analysis as a downloadable report
    """)