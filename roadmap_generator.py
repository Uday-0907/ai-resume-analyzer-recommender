"""
roadmap_generator.py
Skill-gap analysis and 4-week structured learning roadmap generator.
"""

# Skill-specific learning suggestions used to enrich the roadmap entries.
_SKILL_RESOURCES = {
    # Programming
    "python":        ("Python Crash Course (book) + LeetCode easy problems", "Build a CLI tool using Python"),
    "java":          ("MOOC.fi Java Programming course", "Build a small OOP project"),
    "javascript":    ("javascript.info tutorials", "Build an interactive web page"),
    "c++":           ("learncpp.com chapters 1-10", "Solve 10 algorithmic problems on Codeforces"),
    "c#":            ("Microsoft C# Fundamentals path (Learn)", "Build a .NET console application"),
    ".net":          ("Microsoft .NET Tutorial for Beginners", "Create an ASP.NET Core minimal API"),
    "r":             ("R for Data Science (free book, r4ds.had.co.nz)", "EDA notebook on a Kaggle dataset"),
    # Databases
    "sql":           ("Mode SQL Tutorial (free)", "Write 20 practice queries on a sample DB"),
    "nosql":         ("MongoDB University M001 (free)", "Model a document store for a small project"),
    "mongodb":       ("MongoDB University M001 (free)", "Build a CRUD app with PyMongo"),
    "postgresql":    ("PostgreSQL Tutorial (postgresqltutorial.com)", "Design a normalized schema + write joins"),
    "bigquery":      ("Google Cloud BigQuery Sandbox", "Run analytics queries on a public dataset"),
    # Data Science / ML
    "pandas":        ("Pandas official 10-minute tutorial", "Clean and analyse a Kaggle CSV dataset"),
    "numpy":         ("NumPy quickstart tutorial (numpy.org)", "Implement matrix operations from scratch"),
    "statistics":    ("StatQuest YouTube playlist", "Calculate confidence intervals on real data"),
    "ml":            ("fast.ai Part 1 (Practical Deep Learning)", "Train a classifier on Iris/MNIST"),
    "scikit-learn":  ("scikit-learn User Guide Chapters 1-3", "Build and evaluate a regression + classification pipeline"),
    "deep learning": ("DeepLearning.AI Deep Learning Specialization (Coursera)", "Train a feedforward NN from scratch with NumPy"),
    "tensorflow":    ("TensorFlow tutorials (tensorflow.org/tutorials)", "Train an image classifier on CIFAR-10"),
    "keras":         ("Keras documentation getting-started guide", "Implement a CNN for MNIST"),
    "pytorch":       ("PyTorch 60-minute blitz tutorial", "Build a custom Dataset + train a model"),
    "bert":          ("Hugging Face course Chapter 1-3", "Fine-tune BERT on a text classification task"),
    "gpt":           ("OpenAI Cookbook (github.com/openai/openai-cookbook)", "Build a RAG Q&A pipeline"),
    # NLP
    "nlp":           ("spaCy 101 tutorial + NLTK Book Ch. 1-3", "Build a keyword extractor pipeline"),
    "transformers":  ("Hugging Face Transformers course (huggingface.co/course)", "Fine-tune a model on a custom dataset"),
    "hugging face":  ("Hugging Face Datasets + Hub tutorial", "Publish a model card on the Hub"),
    "spacy":         ("spaCy usage guides (spacy.io)", "Build a custom NER pipeline"),
    # Computer Vision
    "opencv":        ("OpenCV-Python tutorials (docs.opencv.org)", "Build a face detection + image-filter app"),
    "cnn":           ("CS231n Stanford lecture notes", "Implement a CNN in PyTorch for image classification"),
    "yolo":          ("Ultralytics YOLOv8 quickstart guide", "Run object detection on a custom image set"),
    # Web / APIs
    "fastapi":       ("FastAPI official tutorial (fastapi.tiangolo.com)", "Build a REST API with authentication"),
    "apis":          ("REST API Design Best Practices (article)", "Consume 2 public APIs and display data"),
    "rest api":      ("REST API Design Best Practices (article)", "Build a CRUD REST API with FastAPI/Flask"),
    "flask":         ("Flask Mega-Tutorial by Miguel Grinberg", "Build and deploy a Flask web app"),
    "django":        ("Django Girls Tutorial (djangogirls.org)", "Build a blog with auth using Django"),
    "react":         ("React official tutorial (react.dev)", "Build a single-page app with hooks"),
    "node.js":       ("Node.js crash course (YouTube)", "Build an Express REST API"),
    # DevOps / Cloud
    "docker":        ("Docker Get-Started tutorial (docs.docker.com)", "Containerise the resume analyzer app"),
    "kubernetes":    ("Kubernetes official interactive tutorial", "Deploy a containerised app on a local cluster"),
    "mlflow":        ("MLflow quickstart (mlflow.org)", "Log, compare, and register model runs for an ML project"),
    "linux":         ("Linux Command Line (William Shotts, free online)", "Complete OverTheWire Bandit levels 0-10"),
    "git":           ("Pro Git (free ebook at git-scm.com)", "Contribute a PR to an open-source project"),
    "airflow":       ("Airflow tutorial: Getting Started (apache.airflow.org)", "Build a simple DAG that runs an ETL pipeline"),
    "spark":         ("Databricks free community edition notebooks", "Run a Spark SQL aggregation on a public dataset"),
    "aws":           ("AWS Cloud Practitioner Essentials (free, AWS Skill Builder)", "Deploy a static site on S3 + CloudFront"),
    "azure":         ("Microsoft Azure Fundamentals (AZ-900) learning path", "Deploy a web app on Azure App Service"),
    "gcp":           ("Google Cloud Skills Boost free tier", "Run a BigQuery analysis + deploy to Cloud Run"),
    # Tools
    "excel":         ("Excel for Beginners (GCFGlobal.org)", "Build a pivot-table dashboard with charts"),
    "power bi":      ("Microsoft Power BI Guided Learning (learn.microsoft.com)", "Build an end-to-end dashboard from a CSV"),
    "tableau":       ("Tableau Public training videos", "Publish an interactive dashboard on Tableau Public"),
    "selenium":      ("Selenium with Python documentation", "Write an automated web-scraping/testing script"),
    # MLOps
    "rag":           ("LangChain RAG tutorial (python.langchain.com)", "Build a document Q&A chatbot using RAG"),
    "llm":           ("Andrej Karpathy makemore series (YouTube)", "Fine-tune or prompt-engineer a model via API"),
}


def _get_resource(skill: str) -> tuple[str, str]:
    """Returns (learn_resource, project_idea) for a given skill key."""
    key = skill.strip().lower()
    return _SKILL_RESOURCES.get(
        key,
        (
            f"Search '{skill} beginner tutorial' on YouTube / Coursera",
            f"Build a small portfolio project that demonstrably uses {skill}",
        ),
    )


# Week themes — the roadmap always has exactly 4 weeks.
_WEEK_THEMES = [
    ("Foundations & Core Concepts",
     "Understand the theory and complete at least one structured tutorial for each skill below."),
    ("Hands-On Practice & Tool Mastery",
     "Move from tutorials to practice: follow along with exercises and replicate examples."),
    ("Project-Based Learning",
     "Apply each skill inside a mini-project (personal GitHub repo counts). Focus on output."),
    ("Integration, Polish & Portfolio",
     "Combine learned skills in one end-to-end project. Write a README, deploy/share it."),
]


def analyze_skill_gaps(extracted_skills: list, target_required_skills: list) -> dict:
    """
    Identifies skills the candidate already has and skills that are missing
    for the target role.

    Returns:
        dict with keys 'matching_skills' and 'missing_skills' (both lists of lowercase strings).
    """
    extracted_set = set(s.lower().strip() for s in extracted_skills)
    required_set = set(s.lower().strip() for s in target_required_skills)

    matching_skills = sorted(extracted_set.intersection(required_set))
    missing_skills = sorted(required_set - extracted_set)

    return {
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
    }


def generate_learning_roadmap(missing_skills: list) -> list[str]:
    """
    Generates a structured 4-week learning roadmap for the missing skills.

    Rules:
    - Always returns exactly 4 week sections regardless of how many skills are missing.
    - Skills are distributed across weeks; weeks without assigned skills carry
      a "consolidation / review" entry so the 4-week structure is always complete.
    - Each skill entry includes a concrete resource and a hands-on project idea.

    Returns:
        List of markdown-formatted strings, one line per roadmap item.
    """
    if not missing_skills:
        return [
            "🎉 **Great news!** You already possess all core skills required for this role.",
            "**Suggested next steps:**",
            "- **Week 1:** Deepen expertise — read advanced docs / research papers for your existing skills.",
            "- **Week 2:** Contribute to an open-source project that uses your stack.",
            "- **Week 3:** Build a showcase portfolio project combining multiple skills.",
            "- **Week 4:** Polish your resume, write case studies, and publish to GitHub/LinkedIn.",
        ]

    # Distribute missing skills across 4 buckets (round-robin so earlier weeks
    # aren't over-loaded and later weeks aren't empty).
    buckets: list[list[str]] = [[] for _ in range(4)]
    for i, skill in enumerate(missing_skills):
        buckets[i % 4].append(skill)

    roadmap: list[str] = []

    for week_idx, (theme, instruction) in enumerate(_WEEK_THEMES):
        week_num = week_idx + 1
        week_skills = buckets[week_idx]

        roadmap.append(f"### 📅 Week {week_num}: {theme}")
        roadmap.append(f"*{instruction}*")

        if week_skills:
            for skill in week_skills:
                resource, project = _get_resource(skill)
                roadmap.append(
                    f"- **{skill.title()}** — 📖 *Learn:* {resource} | "
                    f"🛠️ *Build:* {project}"
                )
        else:
            # No new skills assigned this week — use for consolidation.
            roadmap.append(
                "- 🔄 *Consolidation week* — review and reinforce the skills "
                "from previous weeks. Revisit weak areas, fix bugs in your "
                "project, and write documentation."
            )

        roadmap.append("")  # blank separator between weeks

    return roadmap