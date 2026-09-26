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

# Custom styling for clean, elevated dashboard cards with enhanced padding and spacing
st.markdown("""
<style>
    /* Card container padding and visual separation */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e0e4ec;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    }
    /* Section headers */
    h3 {
        margin-top: 0.25rem !important;
        margin-bottom: 1rem !important;
        font-weight: 600;
    }
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
    }
    /* Tab headers */
    button[data-baseweb="tab"] {
        font-size: 1.05rem;
        font-weight: 500;
        padding: 0.75rem 1.25rem;
    }
</style>
""", unsafe_allow_html=True)

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


# ── Module initialisation (cached) ────────────────────────────────────────────
@st.cache_resource
def load_components():
    extractor = SkillExtractor("data/skill_dictionary.csv")
    matcher = JobMatcher("data/job_roles.csv")
    return extractor, matcher


skill_extractor, job_matcher = load_components()

# ── Tabbed Interface ──────────────────────────────────────────────────────────
tab_upload, tab_match, tab_skills, tab_roadmap, tab_report = st.tabs([
    "📤 Upload & Role",
    "🎯 Match Overview",
    "🔍 Skill Analysis",
    "📚 Roadmap",
    "📄 Report"
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: 📤 Upload & Role
# ═══════════════════════════════════════════════════════════════════════════════
with tab_upload:
    with st.container(border=True):
        st.subheader("📤 Resume Upload & Validation")
        uploaded_file = st.file_uploader(
            "Upload your resume in PDF or DOCX format",
            type=["pdf", "docx"],
            help="Maximum file size: 5 MB"
        )

        if uploaded_file is not None:
            # ── File Validation ────────────────────────────────────────────────
            MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

            # Extension check
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

            # Metrics display
            col_meta1, col_meta2, col_meta3 = st.columns(3)
            with col_meta1:
                st.metric("File Name", uploaded_file.name)
            with col_meta2:
                st.metric("File Format", file_ext.upper().replace(".", ""))
            with col_meta3:
                st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")

            # Check if this file is already parsed and stored in session state
            current_file_signature = f"{uploaded_file.name}_{uploaded_file.size}"
            if st.session_state.get("file_signature") != current_file_signature:
                with st.spinner("Analyzing resume skills and computing role match scores…"):
                    # Extract & Clean
                    raw_text = parse_resume(uploaded_file)
                    cleaned_resume = clean_text(raw_text)

                    # Extract Skills
                    skill_data = skill_extractor.extract_skills(cleaned_resume)
                    extracted_skills = skill_data["all_skills"]
                    categorized = skill_data["categorized_skills"]

                    # Compute Scores
                    rankings = job_matcher.compute_match_scores(cleaned_resume, extracted_skills)

                    # Save in session_state
                    st.session_state["file_signature"] = current_file_signature
                    st.session_state["raw_text"] = raw_text
                    st.session_state["cleaned_resume"] = cleaned_resume
                    st.session_state["extracted_skills"] = extracted_skills
                    st.session_state["categorized_skills"] = categorized
                    st.session_state["rankings"] = rankings
                    # Reset generated AI feedback when new file uploaded
                    st.session_state["ai_feedback_text"] = None

    # Role Selection (only if file analysis is ready in session_state)
    if "rankings" in st.session_state and st.session_state["rankings"]:
        rankings = st.session_state["rankings"]
        job_roles_list = [r["job_role"] for r in rankings]

        with st.container(border=True):
            st.subheader("🎯 Target Role Selection")
            default_role_idx = 0
            current_selected = st.session_state.get("selected_role_name")
            if current_selected in job_roles_list:
                default_role_idx = job_roles_list.index(current_selected)

            selected_role_name = st.selectbox(
                "Select Target Job Role to Analyze:",
                job_roles_list,
                index=default_role_idx,
                key="selected_role_selectbox"
            )
            st.session_state["selected_role_name"] = selected_role_name

            # Compute and cache selected role analysis
            extracted_skills = st.session_state["extracted_skills"]
            target_info = next(r for r in rankings if r["job_role"] == selected_role_name)
            gap_analysis = analyze_skill_gaps(extracted_skills, target_info["required_skills"])
            roadmap = generate_learning_roadmap(gap_analysis["missing_skills"])

            st.session_state["target_info"] = target_info
            st.session_state["gap_analysis"] = gap_analysis
            st.session_state["roadmap"] = roadmap

            st.success(
                f"✅ **Analysis Ready for {selected_role_name}!** Switch between the tabs above "
                "to view your Match Overview, Skill Analysis, Roadmap, and Report."
            )
    else:
        with st.container(border=True):
            st.info("👆 Please upload a resume PDF or DOCX file above to begin analysis.")
            st.markdown("""
            **What this tool does:**
            - 📄 Parses PDF and DOCX resumes in memory (never stored on disk)
            - 🧠 Extracts and categorises technical skills from your resume
            - 📊 Scores compatibility against 8 job roles using semantic similarity + core skill weighting
            - 🏆 Recommends your Top 3 best-matching roles
            - 🔍 Identifies skill gaps for your chosen target role
            - 🗺️ Generates a dynamic 4-week learning roadmap
            - 📥 Exports the full analysis as a downloadable report
            """)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: 🎯 Match Overview
# ═══════════════════════════════════════════════════════════════════════════════
with tab_match:
    if "rankings" not in st.session_state or "target_info" not in st.session_state:
        st.info("👈 Please upload a resume in the **📤 Upload & Role** tab first.")
    else:
        target_info = st.session_state["target_info"]
        selected_role_name = st.session_state["selected_role_name"]
        rankings = st.session_state["rankings"]

        col_m1, col_m2 = st.columns([1, 1], gap="medium")

        with col_m1:
            # Card: Target Role Match
            with st.container(border=True):
                st.subheader("🎯 Target Role Match")

                # Gauge chart for match score
                gauge_fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=target_info["match_score"],
                    number={"suffix": "%", "font": {"size": 38, "family": "Arial, sans-serif"}},
                    title={"text": f"<b>{selected_role_name}</b>", "font": {"size": 16}},
                    gauge={
                        "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#888"},
                        "bar": {"color": "#1f77b4"},
                        "steps": [
                            {"range": [0, 40], "color": "#ffebee"},
                            {"range": [40, 70], "color": "#fff8e1"},
                            {"range": [70, 100], "color": "#e8f5e9"},
                        ],
                        "threshold": {
                            "line": {"color": "#d32f2f", "width": 4},
                            "thickness": 0.8,
                            "value": target_info["match_score"],
                        },
                    },
                ))
                gauge_fig.update_layout(height=290, margin=dict(t=50, b=10, l=25, r=25))
                st.plotly_chart(gauge_fig, use_container_width=True)

                st.caption(
                    f"Weighted Core Skill Match: **{target_info['skill_overlap_score']}%** · "
                    f"Contextual Relevance: **{target_info['tfidf_score']}%**"
                )

        with col_m2:
            # Card: Top 3 Recommended Roles
            with st.container(border=True):
                st.subheader("🏆 Top 3 Recommended Roles")
                top3 = rankings[:3]
                medals = ["🥇", "🥈", "🥉"]
                for medal, role in zip(medals, top3):
                    st.metric(
                        label=f"{medal} {role['job_role']}",
                        value=f"{role['match_score']}%",
                        help=(
                            f"Skill match: {role['skill_overlap_score']}% | "
                            f"Context: {role['tfidf_score']}%"
                        ),
                    )

        # Card: All Role Compatibility Scores (Bar Chart)
        with st.container(border=True):
            st.subheader("📊 All Role Compatibility Scores")
            df_rankings = pd.DataFrame(rankings)
            
            fig = px.bar(
                df_rankings,
                x="match_score",
                y="job_role",
                orientation="h",
                labels={"match_score": "Score (%)", "job_role": "Role"},
                color="match_score",
                color_continuous_scale="Blues",
                text="match_score",
            )
            fig.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
                marker_line_width=1,
                marker_line_color="#1f77b4"
            )
            # Increase spacing between bars, enlarge role labels, and normalize score scale [0, 100]
            fig.update_layout(
                yaxis={
                    "categoryorder": "total ascending",
                    "tickfont": {"size": 13, "family": "Arial, sans-serif"},
                    "title": ""
                },
                xaxis={
                    "range": [0, 100],
                    "dtick": 20,
                    "tickfont": {"size": 12},
                    "title": "Match Score (%)"
                },
                bargap=0.35,
                height=420,
                margin=dict(l=20, r=40, t=30, b=40)
            )
            st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: 🔍 Skill Analysis
# ═══════════════════════════════════════════════════════════════════════════════
with tab_skills:
    if "gap_analysis" not in st.session_state or "categorized_skills" not in st.session_state:
        st.info("👈 Please upload a resume in the **📤 Upload & Role** tab first.")
    else:
        gap_analysis = st.session_state["gap_analysis"]
        categorized = st.session_state["categorized_skills"]
        selected_role_name = st.session_state["selected_role_name"]

        # Card: Skill-Gap Analysis
        with st.container(border=True):
            st.subheader(f"🔍 Skill-Gap Analysis for {selected_role_name}")
            gap_col1, gap_col2 = st.columns(2, gap="medium")

            with gap_col1:
                st.markdown("### ✅ Skills Found")
                if gap_analysis["matching_skills"]:
                    for s in sorted(gap_analysis["matching_skills"]):
                        st.markdown(f"- **{s.title()}**")
                else:
                    st.write("_None matched for this role._")

            with gap_col2:
                st.markdown("### ❌ Missing Skills")
                if gap_analysis["missing_skills"]:
                    for s in sorted(gap_analysis["missing_skills"]):
                        st.markdown(f"- **{s.title()}**")
                else:
                    st.success("🎉 You possess all required skills for this role!")

        # Card: Extracted Skills by Category (Clean & Deduplicated)
        with st.container(border=True):
            st.subheader("🧠 Extracted Skills by Category")
            if categorized:
                # Group by clean standardized categories
                for cat, s_list in sorted(categorized.items()):
                    cat_label = "ML" if cat.lower() == "ml" else cat.replace('_', ' ').title()
                    # Clean formatted skills list without duplicates
                    formatted_skills = []
                    for s in s_list:
                        s_clean = s.strip()
                        if s_clean.lower() in {"sql", "aws", "gcp", "ml", "nlp", "apis", "ci/cd", "llm", "rag", "cnn", "yolo", "bert", "gpt", "ui/ux"}:
                            formatted_skills.append(s_clean.upper())
                        else:
                            formatted_skills.append(s_clean.title())

                    st.markdown(f"**{cat_label}:** {', '.join(formatted_skills)}")
            else:
                st.warning("No skills matched from the dictionary. Check that the resume text was extracted correctly.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: 📚 Roadmap
# ═══════════════════════════════════════════════════════════════════════════════
with tab_roadmap:
    if "roadmap" not in st.session_state:
        st.info("👈 Please upload a resume in the **📤 Upload & Role** tab first.")
    else:
        roadmap = st.session_state["roadmap"]
        selected_role_name = st.session_state["selected_role_name"]

        # Card: Dynamic 4-Week Learning Roadmap
        with st.container(border=True):
            st.subheader(f"🗺️ 4-Week Learning Roadmap for {selected_role_name}")
            st.caption("Dynamically tailored to bridge your exact detected skill gaps.")
            
            for line in roadmap:
                if line.startswith("###"):
                    st.markdown(line)
                elif line == "":
                    st.markdown(" ")
                else:
                    st.markdown(line)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5: 📄 Report
# ═══════════════════════════════════════════════════════════════════════════════
with tab_report:
    if "rankings" not in st.session_state or "target_info" not in st.session_state:
        st.info("👈 Please upload a resume in the **📤 Upload & Role** tab first.")
    else:
        target_info = st.session_state["target_info"]
        selected_role_name = st.session_state["selected_role_name"]
        gap_analysis = st.session_state["gap_analysis"]
        roadmap = st.session_state["roadmap"]
        extracted_skills = st.session_state["extracted_skills"]
        rankings = st.session_state["rankings"]
        top3 = rankings[:3]

        # Card: AI-Generated Feedback
        if is_ai_feedback_available():
            with st.container(border=True):
                st.subheader("🤖 AI-Generated Feedback (optional)")
                if st.button("Generate personalised feedback"):
                    with st.spinner("Asking Gemini for personalized feedback…"):
                        ai_text = generate_ai_feedback(
                            target_role=selected_role_name,
                            matching_skills=gap_analysis["matching_skills"],
                            missing_skills=gap_analysis["missing_skills"],
                            match_score=target_info["match_score"],
                        )
                        st.session_state["ai_feedback_text"] = ai_text

                if st.session_state.get("ai_feedback_text"):
                    st.markdown("### Personalized Recommendations")
                    st.write(st.session_state["ai_feedback_text"])

        # Card: Download Analysis Report
        with st.container(border=True):
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
  ↳ Weighted skill match : {target_info['skill_overlap_score']}%
  ↳ Contextual relevance : {target_info['tfidf_score']}%

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

            if st.session_state.get("ai_feedback_text"):
                report_content += f"\n\n{'─' * 60}\nAI-GENERATED FEEDBACK\n{'─' * 60}\n{st.session_state['ai_feedback_text']}"

            st.download_button(
                label="📥 Download Analysis Report (.txt)",
                data=report_content,
                file_name=f"resume_analysis_{selected_role_name.replace(' ', '_').lower()}.txt",
                mime="text/plain",
            )