# AI Resume Analyzer & Job Recommendation System

An NLP-based Streamlit app that compares a resume against a set of job roles,
scores the match, highlights missing skills, and generates a simple
week-by-week learning roadmap.

## Features

- Upload a resume as PDF or DOCX
- Automatic text extraction and cleaning (keeps technical symbols like C++, C#, .NET)
- Skill extraction against a controlled skill dictionary, grouped by category
- Match scoring against multiple job roles, blending:
  - **Skill overlap** — matched skills ÷ required skills for the role
  - **TF-IDF cosine similarity** — contextual similarity between resume and role description
- Top-role ranking with an interactive chart
- Skill-gap analysis (found vs. missing skills) for the selected target role
- Auto-generated learning roadmap for missing skills
- Downloadable text report of the full analysis

## Project Structure

```
ai_resume_analyzer/
|-- app.py                  # Streamlit UI and orchestration
|-- resume_parser.py        # PDF / DOCX text extraction
|-- text_cleaner.py         # Text normalization
|-- skill_extractor.py      # Skill dictionary matching
|-- job_matcher.py          # TF-IDF + skill-overlap scoring
|-- roadmap_generator.py    # Skill-gap analysis and roadmap generation
|-- ai_feedback.py          # Optional Gemini-powered resume feedback
|-- requirements.txt
|-- README.md
|-- .env                    # Optional: GEMINI_API_KEY for AI feedback feature
|-- .gitignore
|
|-- data/
|   |-- job_roles.csv           # Job roles + required skills + description
|   |-- skill_dictionary.csv    # Controlled list of recognized skills
|
|-- sample_resumes/         # Sample resumes for manual testing (PII removed)
|-- reports/                # Downloaded analysis reports land here (gitignored)
|-- tests/
|   |-- test_cases.csv      # Manual test sheet: resume -> expected top role
```

## Setup

1. Clone the repository and move into the project folder:
   ```bash
   git clone <your-repo-url>
   cd ai_resume_analyzer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

5. Open the URL Streamlit prints (usually `http://localhost:8501`), upload a
   PDF or DOCX resume from `sample_resumes/`, pick a target role, and review
   the results.

## How the Match Score Works

For each job role:

```
match_score = 0.7 * skill_overlap_ratio + 0.3 * tfidf_cosine_similarity
```

- `skill_overlap_ratio` = (skills found in resume ∩ role's required skills) ÷ (role's required skills)
- `tfidf_cosine_similarity` = cosine similarity between the resume text and the role's description, both vectorized with TF-IDF

Skill overlap is weighted more heavily because it is directly explainable
("you're missing Docker and MLflow"), while TF-IDF adds broader contextual
signal from how the resume is written.

## Optional Advanced Feature: AI-Generated Feedback

The PDF's "Optional Advanced Features" section mentions LLM-generated resume
feedback. This is implemented in `ai_feedback.py` using **Gemini** (Google's
model), and it is fully optional:

- With no key set, the app works exactly as before — the AI feedback section
  simply doesn't appear.
- To enable it:
  1. Get a free API key from Google AI Studio: https://aistudio.google.com/apikey
  2. Open `.env` and set `GEMINI_API_KEY=your-key-here`
  3. Restart the app. A "🤖 AI-Generated Feedback (optional)" section with a
     "Generate personalized feedback" button will appear below the roadmap.

The prompt sent to Gemini is a **controlled prompt**: it only ever receives
the target role, the matched/missing skill lists, and the match score — never
the raw resume text or any personal information — and it's explicitly
instructed not to reference personal attributes or guarantee outcomes, in
line with the Responsible AI rules below.

## Responsible AI Notes

- This tool is guidance only — it does not make hiring or rejection decisions.
- It scores only job-related skills, education, projects, and experience.
- It never scores gender, age, religion, nationality, photographs, marital
  status, or disability.
- Uploaded resumes are processed in memory and are not stored on disk.
- A missing keyword does not always mean missing ability — scores are estimates.

## Testing

See `tests/test_cases.csv` for the manual test sheet used to check that
expected top roles match actual top roles across different resume styles.

## Known Limitations

- Skill detection relies on exact/near-exact string matching against
  `skill_dictionary.csv` — synonyms or unlisted skills won't be detected
  unless the dictionary is extended.
- TF-IDF similarity is sensitive to resume length and wording; it is a
  secondary signal to skill overlap, not a standalone judgment of fit.
- The job-role dataset is a small, manually curated starter set (5 roles) —
  intended to be extended for production use.
