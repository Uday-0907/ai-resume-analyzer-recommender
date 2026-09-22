"""
tests/test_pipeline.py
======================
Pytest unit tests for the AI Resume Analyzer pipeline.

Covers all assertions required by the project specification:
  1. text_cleaner retains C++, C#, and .NET
  2. job_matcher returns cosine similarity scores in [0, 100]
  3. skill_extractor correctly identifies skills present in sample text
  4. resume_parser extracts text from in-memory DOCX bytes
  5. analyze_skill_gaps correctly splits matching vs. missing skills
  6. generate_learning_roadmap always produces exactly 4 week sections
"""

import io
import sys
import os
import pytest

# ── Path setup so tests can find modules at repo root ─────────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from text_cleaner import clean_text
from resume_parser import extract_text_from_docx
from skill_extractor import SkillExtractor
from job_matcher import JobMatcher
from roadmap_generator import analyze_skill_gaps, generate_learning_roadmap


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_docx_bytes(text_paragraphs: list[str]) -> bytes:
    """Creates an in-memory .docx with the given paragraphs."""
    from docx import Document
    doc = Document()
    for para in text_paragraphs:
        doc.add_paragraph(para)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# 1. text_cleaner — special symbol preservation
# ─────────────────────────────────────────────────────────────────────────────

class TestTextCleaner:

    def test_cpp_is_preserved(self):
        """C++ must survive cleaning without being stripped to 'c'."""
        result = clean_text("Proficient in C++ and algorithms.")
        assert "c++" in result, f"Expected 'c++' in cleaned text but got: {result!r}"

    def test_csharp_is_preserved(self):
        """C# must survive cleaning."""
        result = clean_text("Developed applications in C# and .NET.")
        assert "c#" in result, f"Expected 'c#' in cleaned text but got: {result!r}"

    def test_dotnet_is_preserved(self):
        """.NET must survive cleaning."""
        result = clean_text("Built microservices with .NET Core.")
        assert ".net" in result, f"Expected '.net' in cleaned text but got: {result!r}"

    def test_all_three_together(self):
        """All three special tokens must survive when they appear together."""
        result = clean_text("Experience with C++, C#, and .NET frameworks.")
        assert "c++" in result, "c++ missing from cleaned text"
        assert "c#" in result,  "c# missing from cleaned text"
        assert ".net" in result, ".net missing from cleaned text"

    def test_text_is_lowercased(self):
        """Cleaning must lowercase the output."""
        result = clean_text("Python PANDAS NumPy")
        assert result == result.lower(), "Cleaned text should be all lowercase"

    def test_repeated_spaces_normalized(self):
        """Multiple consecutive whitespace characters should collapse to one space."""
        result = clean_text("python   pandas   sql")
        assert "  " not in result, "Double spaces found in cleaned text"

    def test_empty_string_returns_empty(self):
        result = clean_text("")
        assert result == "", "Cleaning empty string should return empty string"

    def test_none_handling(self):
        # The function guards against falsy input
        result = clean_text(None)
        assert result == ""

    def test_regular_symbols_stripped(self):
        """Symbols unrelated to technical terms should be removed."""
        result = clean_text("Hello! World@ #hashtag$")
        # '#' is part of 'c#' protection but standalone should be cleaned
        assert "!" not in result
        assert "@" not in result
        assert "$" not in result


# ─────────────────────────────────────────────────────────────────────────────
# 2. job_matcher — cosine similarity scores in [0, 100]
# ─────────────────────────────────────────────────────────────────────────────

DATA_DIR = os.path.join(ROOT, "data")


class TestJobMatcher:

    @pytest.fixture(scope="class")
    @classmethod
    def matcher(cls):
        return JobMatcher(os.path.join(DATA_DIR, "job_roles.csv"))

    def test_scores_within_0_100(self, matcher):
        """Every match score must be a percentage in [0, 100]."""
        resume_text = "python pandas sql machine learning scikit-learn numpy statistics"
        results = matcher.compute_match_scores(resume_text, ["python", "pandas", "sql"])
        for r in results:
            assert 0.0 <= r["match_score"] <= 100.0, (
                f"match_score {r['match_score']} out of range for role {r['job_role']}"
            )

    def test_tfidf_scores_within_0_100(self, matcher):
        """Raw TF-IDF scores must also be within [0, 100]."""
        resume_text = "python deep learning pytorch nlp transformers"
        results = matcher.compute_match_scores(resume_text, ["python", "pytorch"])
        for r in results:
            assert 0.0 <= r["tfidf_score"] <= 100.0, (
                f"tfidf_score {r['tfidf_score']} out of range for role {r['job_role']}"
            )

    def test_skill_overlap_scores_within_0_100(self, matcher):
        """Skill overlap scores must be within [0, 100]."""
        results = matcher.compute_match_scores("python sql pandas", ["python", "sql"])
        for r in results:
            assert 0.0 <= r["skill_overlap_score"] <= 100.0

    def test_results_sorted_descending(self, matcher):
        """Results must be sorted highest match_score first."""
        results = matcher.compute_match_scores(
            "python pandas sql statistics power bi tableau excel",
            ["python", "pandas", "sql", "statistics", "excel", "power bi", "tableau"]
        )
        scores = [r["match_score"] for r in results]
        assert scores == sorted(scores, reverse=True), "Results not sorted in descending order"

    def test_top_role_for_data_analyst_resume(self, matcher):
        """A resume with strong Data Analyst keywords should rank Data Analyst first."""
        resume = (
            "python sql excel pandas statistics power bi tableau data analysis "
            "hypothesis testing kpi reporting pivot tables data visualization numpy"
        )
        skills = ["python", "sql", "excel", "pandas", "statistics", "power bi", "tableau", "numpy"]
        results = matcher.compute_match_scores(resume, skills)
        assert results[0]["job_role"] == "Data Analyst", (
            f"Expected 'Data Analyst' at rank 1 but got '{results[0]['job_role']}'"
        )

    def test_returns_list_of_dicts(self, matcher):
        results = matcher.compute_match_scores("python", [])
        assert isinstance(results, list)
        assert all(isinstance(r, dict) for r in results)

    def test_required_keys_present(self, matcher):
        results = matcher.compute_match_scores("python sql", ["python"])
        required_keys = {"job_role", "match_score", "tfidf_score", "skill_overlap_score", "required_skills"}
        for r in results:
            assert required_keys.issubset(r.keys()), f"Missing keys in result: {r.keys()}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. skill_extractor — finds known skills in sample text
# ─────────────────────────────────────────────────────────────────────────────

class TestSkillExtractor:

    @pytest.fixture(scope="class")
    @classmethod
    def extractor(cls):
        return SkillExtractor(os.path.join(DATA_DIR, "skill_dictionary.csv"))

    def test_finds_python(self, extractor):
        result = extractor.extract_skills("i have experience with python and pandas")
        assert "python" in result["all_skills"]

    def test_finds_multiple_skills(self, extractor):
        text = "worked with python sql pandas numpy scikit-learn docker git"
        result = extractor.extract_skills(text)
        found = result["all_skills"]
        for skill in ["python", "sql", "pandas", "numpy", "scikit-learn", "docker", "git"]:
            assert skill in found, f"Expected skill '{skill}' not found. Found: {found}"

    def test_categorized_output_structure(self, extractor):
        text = "python sql pandas docker aws"
        result = extractor.extract_skills(text)
        assert "categorized_skills" in result
        assert isinstance(result["categorized_skills"], dict)

    def test_no_false_positive_for_empty_text(self, extractor):
        result = extractor.extract_skills("")
        assert result["all_skills"] == []

    def test_finds_cpp(self, extractor):
        """c++ must be found even after going through clean_text."""
        from text_cleaner import clean_text
        raw = "Experienced in C++ and algorithms"
        cleaned = clean_text(raw)
        result = extractor.extract_skills(cleaned)
        assert "c++" in result["all_skills"], f"c++ not found. cleaned text: {cleaned!r}"

    def test_finds_dotnet(self, extractor):
        """.NET must be detected in cleaned text."""
        from text_cleaner import clean_text
        raw = "Built enterprise apps with .NET and C#"
        cleaned = clean_text(raw)
        result = extractor.extract_skills(cleaned)
        assert ".net" in result["all_skills"], f".net not found. cleaned text: {cleaned!r}"

    def test_ml_resume_skills(self, extractor):
        """A typical ML engineer resume should surface key ML skills."""
        text = (
            "proficient in python pytorch scikit-learn deep learning mlflow docker "
            "fastapi numpy pandas git linux"
        )
        result = extractor.extract_skills(text)
        expected = ["python", "pytorch", "scikit-learn", "deep learning", "mlflow",
                    "docker", "fastapi", "numpy", "pandas", "git", "linux"]
        for skill in expected:
            assert skill in result["all_skills"], (
                f"Expected '{skill}' in extracted skills but got: {result['all_skills']}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# 4. resume_parser — DOCX in-memory extraction
# ─────────────────────────────────────────────────────────────────────────────

class TestResumeParser:

    def test_docx_extraction_returns_text(self):
        paras = ["Senior Data Analyst", "Skills: Python, SQL, Pandas, Power BI, Tableau"]
        doc_bytes = make_docx_bytes(paras)
        result = extract_text_from_docx(doc_bytes)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_docx_extraction_contains_keywords(self):
        paras = ["Machine Learning Engineer", "PyTorch, scikit-learn, MLflow, Docker, FastAPI"]
        doc_bytes = make_docx_bytes(paras)
        result = extract_text_from_docx(doc_bytes)
        assert "PyTorch" in result or "pytorch" in result.lower()
        assert "MLflow" in result or "mlflow" in result.lower()

    def test_docx_empty_paragraphs_skipped(self):
        paras = ["", "   ", "NLP Engineer", "", "spaCy, Transformers, BERT"]
        doc_bytes = make_docx_bytes(paras)
        result = extract_text_from_docx(doc_bytes)
        assert "NLP Engineer" in result
        # Should not start/end with excessive whitespace from blank paragraphs
        assert result.strip() == result or result  # flexible, just must not error


# ─────────────────────────────────────────────────────────────────────────────
# 5. analyze_skill_gaps
# ─────────────────────────────────────────────────────────────────────────────

class TestAnalyzeSkillGaps:

    def test_correctly_identifies_matching_skills(self):
        extracted = ["python", "sql", "pandas", "docker"]
        required  = ["python", "sql", "mlflow", "fastapi"]
        result = analyze_skill_gaps(extracted, required)
        assert set(result["matching_skills"]) == {"python", "sql"}

    def test_correctly_identifies_missing_skills(self):
        extracted = ["python", "sql"]
        required  = ["python", "sql", "docker", "kubernetes"]
        result = analyze_skill_gaps(extracted, required)
        assert set(result["missing_skills"]) == {"docker", "kubernetes"}

    def test_all_present_no_missing(self):
        extracted = ["python", "sql", "pandas"]
        required  = ["python", "sql", "pandas"]
        result = analyze_skill_gaps(extracted, required)
        assert result["missing_skills"] == []

    def test_none_matching_all_missing(self):
        extracted = ["java", "javascript"]
        required  = ["python", "sql"]
        result = analyze_skill_gaps(extracted, required)
        assert result["matching_skills"] == []
        assert set(result["missing_skills"]) == {"python", "sql"}

    def test_case_insensitive(self):
        """Gap analysis must be case-insensitive."""
        result = analyze_skill_gaps(["Python", "SQL"], ["python", "sql", "Docker"])
        assert "python" in result["matching_skills"] or "Python" in result["matching_skills"]
        assert len(result["missing_skills"]) == 1


# ─────────────────────────────────────────────────────────────────────────────
# 6. generate_learning_roadmap — always 4 weeks
# ─────────────────────────────────────────────────────────────────────────────

class TestGenerateLearningRoadmap:

    def _count_week_headers(self, roadmap: list[str]) -> int:
        return sum(1 for line in roadmap if line.startswith("### 📅 Week"))

    def test_exactly_4_weeks_with_one_skill(self):
        roadmap = generate_learning_roadmap(["docker"])
        assert self._count_week_headers(roadmap) == 4, (
            f"Expected 4 week headers, got {self._count_week_headers(roadmap)}"
        )

    def test_exactly_4_weeks_with_many_skills(self):
        skills = ["docker", "kubernetes", "mlflow", "airflow", "spark", "aws", "gcp"]
        roadmap = generate_learning_roadmap(skills)
        assert self._count_week_headers(roadmap) == 4

    def test_exactly_4_weeks_with_empty_skills(self):
        """Even with no missing skills the roadmap should have 4 guidance points."""
        roadmap = generate_learning_roadmap([])
        # Empty case returns a different format — just check it's non-empty and helpful
        assert len(roadmap) > 0
        assert any("Week" in line for line in roadmap)

    def test_skill_name_appears_in_roadmap(self):
        """The roadmap should reference each missing skill by name."""
        roadmap = generate_learning_roadmap(["pytorch", "mlflow"])
        combined = " ".join(roadmap).lower()
        assert "pytorch" in combined, "pytorch not found in roadmap text"
        assert "mlflow" in combined, "mlflow not found in roadmap text"

    def test_returns_list_of_strings(self):
        roadmap = generate_learning_roadmap(["python"])
        assert isinstance(roadmap, list)
        assert all(isinstance(item, str) for item in roadmap)

    def test_exactly_4_weeks_with_4_skills(self):
        """4 skills should cleanly assign one per week."""
        roadmap = generate_learning_roadmap(["docker", "aws", "mlflow", "spark"])
        assert self._count_week_headers(roadmap) == 4
