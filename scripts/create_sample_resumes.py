"""
scripts/create_sample_resumes.py
=================================
Generates three synthetic, PII-free DOCX sample resumes for use in
manual testing and the test_cases.csv evaluation matrix.

Run from the repo root:
    python scripts/create_sample_resumes.py

Requires: python-docx (already in requirements.txt)
"""

import os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


def add_heading(doc, text, level=1):
    para = doc.add_heading(text, level=level)
    return para


def add_section(doc, title, items):
    add_heading(doc, title, level=2)
    for item in items:
        p = doc.add_paragraph(item, style="List Bullet")


def add_paragraph(doc, text):
    doc.add_paragraph(text)


# ─────────────────────────────────────────────────────────────────────────────
# Resume A — Data Analyst
# ─────────────────────────────────────────────────────────────────────────────
def create_data_analyst_resume(path):
    doc = Document()

    add_heading(doc, "Data Analyst — Sample Resume (PII Removed)", level=1)
    add_paragraph(doc, "Objective: Analytical professional with 3+ years of experience turning raw data into actionable insights using Python, SQL, and data visualisation tools.")

    add_section(doc, "Technical Skills", [
        "Languages & Libraries: Python, SQL, R, Pandas, NumPy, Statistics",
        "Visualisation: Power BI, Tableau, Excel (Pivot Tables, VLOOKUP, Charts)",
        "Databases: SQL Server, PostgreSQL, MySQL",
        "Tools: Git, Jupyter Notebook, Google Sheets",
    ])

    add_section(doc, "Work Experience", [
        "Data Analyst Intern (12 months) — E-commerce firm",
        "  • Built automated SQL queries to extract and summarise weekly KPI reports",
        "  • Created Power BI dashboards tracking conversion rates, reducing manual reporting by 60%",
        "  • Used Pandas and NumPy for data cleaning and exploratory data analysis (EDA) on 2M+ row datasets",
        "  • Applied statistical hypothesis testing (t-tests, chi-squared) to validate A/B experiments",
        "  • Developed Tableau workbooks for executive stakeholder presentations",
    ])

    add_section(doc, "Projects", [
        "Sales Forecasting Dashboard — Python (Pandas, Statistics), Power BI, SQL",
        "Customer Churn Analysis — Python, scikit-learn logistic regression, Tableau",
        "Excel Financial Model — Excel advanced formulas, pivot tables, conditional formatting",
    ])

    add_section(doc, "Education", [
        "Bachelor of Science — Data Science (3.8 GPA)",
        "Relevant coursework: Statistics, Database Management, Data Visualisation, Machine Learning Foundations",
    ])

    add_section(doc, "Certifications", [
        "Microsoft Power BI Data Analyst Associate (PL-300)",
        "Google Data Analytics Professional Certificate",
        "Tableau Desktop Specialist",
    ])

    doc.save(path)
    print(f"[OK] Created: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# Resume B — Machine Learning Engineer
# ─────────────────────────────────────────────────────────────────────────────
def create_ml_engineer_resume(path):
    doc = Document()

    add_heading(doc, "Machine Learning Engineer — Sample Resume (PII Removed)", level=1)
    add_paragraph(doc, "Objective: ML engineer with expertise in building, training, and deploying production-grade machine learning models using Python, PyTorch, scikit-learn, MLflow, and Docker.")

    add_section(doc, "Technical Skills", [
        "Languages: Python, SQL, Linux (Bash scripting)",
        "ML Frameworks: PyTorch, scikit-learn, TensorFlow, Keras, Deep Learning",
        "MLOps & Deployment: MLflow (experiment tracking, model registry), Docker, FastAPI, Git",
        "Data Processing: Pandas, NumPy, Apache Spark (basic)",
        "Cloud: AWS (SageMaker, S3, EC2)",
    ])

    add_section(doc, "Work Experience", [
        "Junior ML Engineer (18 months) — Tech startup",
        "  • Trained and evaluated scikit-learn classification and regression models for fraud detection",
        "  • Implemented MLflow tracking across all model runs; registered best model to MLflow Model Registry",
        "  • Containerised ML inference services using Docker and served predictions via FastAPI REST API",
        "  • Rebuilt training pipeline using PyTorch for a deep learning image classification task",
        "  • Managed all experiments in Git with CI pipeline to auto-trigger retraining on data drift",
    ])

    add_section(doc, "Projects", [
        "Sentiment Classifier — Python, PyTorch, scikit-learn, MLflow, Docker, FastAPI",
        "Tabular Fraud Detector — Python, scikit-learn (RandomForest, XGBoost), Pandas, NumPy",
        "End-to-End ML Pipeline — Docker Compose, FastAPI, MLflow, PostgreSQL, AWS S3",
    ])

    add_section(doc, "Education", [
        "Bachelor of Engineering — Computer Science",
        "Relevant coursework: Machine Learning, Deep Learning, Distributed Systems, Linear Algebra",
    ])

    add_section(doc, "Certifications", [
        "AWS Certified Machine Learning Specialty",
        "DeepLearning.AI TensorFlow Developer Certificate",
        "Databricks Certified Associate Developer for Apache Spark",
    ])

    doc.save(path)
    print(f"[OK] Created: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# Resume C — NLP Engineer
# ─────────────────────────────────────────────────────────────────────────────
def create_nlp_engineer_resume(path):
    doc = Document()

    add_heading(doc, "NLP Engineer — Sample Resume (PII Removed)", level=1)
    add_paragraph(doc, "Objective: NLP specialist with hands-on experience building language understanding systems using Transformers, Hugging Face, spaCy, BERT, and large language models (LLM).")

    add_section(doc, "Technical Skills", [
        "Languages: Python, SQL",
        "NLP Frameworks: Hugging Face Transformers, spaCy, NLTK, BERT, GPT, scikit-learn",
        "Deep Learning: PyTorch, TensorFlow, Keras",
        "Data: Pandas, NumPy",
        "MLOps & Tools: Git, Docker, MLflow, FastAPI",
        "Research areas: NLP, Named Entity Recognition, Text Classification, RAG, LLM prompting",
    ])

    add_section(doc, "Work Experience", [
        "NLP Research Engineer (2 years) — AI Research Lab",
        "  • Fine-tuned BERT and RoBERTa on domain-specific text classification using Hugging Face Transformers",
        "  • Built production NLP pipelines with spaCy for Named Entity Recognition (NER) and dependency parsing",
        "  • Developed a Retrieval-Augmented Generation (RAG) Q&A system using LLM APIs and vector databases",
        "  • Evaluated GPT-based summarisation models; reduced hallucination rate by 23% with prompt engineering",
        "  • Packaged NLP microservices using Docker and FastAPI; tracked experiments in MLflow",
    ])

    add_section(doc, "Projects", [
        "Resume Skill Extractor — Python, spaCy, Transformers, Hugging Face, scikit-learn",
        "Multilingual Sentiment Analyser — BERT multilingual, Hugging Face Datasets, PyTorch",
        "Document Q&A Chatbot — RAG, LLM (GPT API), vector DB, FastAPI, Docker",
        "NER Pipeline for Medical Text — spaCy, custom NER training, scikit-learn evaluation",
    ])

    add_section(doc, "Education", [
        "Master of Science — Computational Linguistics / NLP",
        "Thesis: Fine-tuning large language models for low-resource NLP tasks",
        "Relevant coursework: NLP, Deep Learning, Probabilistic Graphical Models, Information Retrieval",
    ])

    add_section(doc, "Certifications", [
        "Hugging Face NLP Course (Certificate of Completion)",
        "DeepLearning.AI Natural Language Processing Specialization",
        "fast.ai Practical Deep Learning for Coders",
    ])

    doc.save(path)
    print(f"[OK] Created: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "sample_resumes")
    os.makedirs(out_dir, exist_ok=True)

    create_data_analyst_resume(os.path.join(out_dir, "resume_data_analyst.docx"))
    create_ml_engineer_resume(os.path.join(out_dir, "resume_ml_engineer.docx"))
    create_nlp_engineer_resume(os.path.join(out_dir, "resume_nlp_engineer.docx"))

    print("\n[OK] All 3 sample resumes created in sample_resumes/")
