"""
roadmap_generator.py
Skill-gap analysis and dynamic 4-week structured learning roadmap generator.
Each week's content maps directly to the specific missing skills detected.
"""

# Skill-specific learning suggestions used to enrich the roadmap entries.
_SKILL_RESOURCES = {
    # Programming
    "python":        ("Python Crash Course (book) + LeetCode easy problems", "Build a CLI tool or data pipeline in Python"),
    "java":          ("MOOC.fi Java Programming course", "Build an object-oriented REST service"),
    "javascript":    ("javascript.info tutorials", "Build an interactive web dashboard"),
    "typescript":    ("TypeScript Handbook (typescriptlang.org)", "Refactor a JavaScript project with strict type definitions"),
    "c++":           ("learncpp.com chapters 1-10", "Implement high-performance data structures"),
    "c#":            ("Microsoft C# Fundamentals path (Learn)", "Build a .NET console and web application"),
    ".net":          ("Microsoft .NET Tutorial for Beginners", "Create an ASP.NET Core minimal API"),
    "r":             ("R for Data Science (free book, r4ds.had.co.nz)", "EDA notebook and statistical analysis on Kaggle"),
    "scala":         ("Scala Exercises (scala-exercises.org)", "Write functional data processing transformations"),
    "go":            ("Tour of Go (go.dev/tour)", "Build a concurrent web crawler / microservice"),
    "rust":          ("The Rust Programming Language Book", "Build a memory-safe command-line tool"),
    "php":           ("PHP The Right Way (phptherightway.com)", "Build a dynamic web application"),
    "ruby":          ("Ruby in 20 Minutes (ruby-lang.org)", "Build a backend service with Ruby"),
    "react":         ("React official tutorial (react.dev)", "Build a single-page app with hooks and state management"),
    "node.js":       ("Node.js crash course (nodejs.org)", "Build an Express REST API with authentication"),
    "flask":         ("Flask Mega-Tutorial by Miguel Grinberg", "Build and deploy a Flask web service"),
    "django":        ("Django Girls Tutorial (djangogirls.org)", "Build a full-stack database-backed Django app"),
    "fastapi":       ("FastAPI official tutorial (fastapi.tiangolo.com)", "Build an asynchronous REST API with Swagger docs"),
    "apis":          ("REST API Design Best Practices", "Design and consume public REST APIs"),
    "rest api":      ("REST API Design Best Practices", "Build a CRUD REST API with authentication"),
    # Databases
    "sql":           ("Mode SQL Tutorial (free)", "Write complex queries with JOINs, aggregations, and window functions"),
    "nosql":         ("MongoDB University M001 (free)", "Model a flexible document store for real-world data"),
    "mongodb":       ("MongoDB University M001 (free)", "Build a CRUD application with PyMongo or Mongoose"),
    "postgresql":    ("PostgreSQL Tutorial (postgresqltutorial.com)", "Design a normalized relational schema with indexing"),
    "mysql":         ("MySQL Official Tutorial", "Set up a relational database with foreign key constraints"),
    "redis":         ("Redis University (university.redis.com)", "Implement an in-memory caching and session store layer"),
    "bigquery":      ("Google Cloud BigQuery Sandbox", "Run analytical SQL queries on public big data sets"),
    "snowflake":     ("Snowflake Hands-On Essentials", "Set up virtual warehouses and query cloud data tables"),
    "sqlite":        ("SQLite Tutorial (sqlitetutorial.net)", "Embed a local transactional database in a Python application"),
    "oracle":        ("Oracle Database Foundations", "Practice SQL queries and transactional isolation levels"),
    "cassandra":     ("DataStax Cassandra Developer course", "Model time-series or wide-column distributed data"),
    "dynamodb":      ("AWS DynamoDB Developer Guide", "Design single-table NoSQL schemas for high throughput"),
    # Machine Learning / AI
    "ml":            ("fast.ai Part 1 (Practical Deep Learning)", "Train and evaluate a supervised learning classifier"),
    "machine learning": ("Coursera Machine Learning Specialization", "Build end-to-end regression and classification models"),
    "scikit-learn":  ("scikit-learn User Guide Chapters 1-3", "Build a machine learning pipeline with cross-validation"),
    "deep learning": ("DeepLearning.AI Deep Learning Specialization", "Train a neural network with backpropagation from scratch"),
    "tensorflow":    ("TensorFlow tutorials (tensorflow.org/tutorials)", "Train an image classifier on CIFAR-10"),
    "keras":         ("Keras documentation getting-started guide", "Implement a convolutional network for computer vision"),
    "pytorch":       ("PyTorch 60-minute blitz tutorial", "Build custom PyTorch Datasets and train neural models"),
    "bert":          ("Hugging Face course Chapters 1-3", "Fine-tune BERT for text classification and sentiment"),
    "gpt":           ("OpenAI Cookbook (github.com/openai/openai-cookbook)", "Build an interactive generative AI application"),
    "llm":           ("Andrej Karpathy makemore & LLM series", "Prompt-engineer and integrate LLMs via API with function calling"),
    "rag":           ("LangChain / LlamaIndex RAG tutorials", "Build a retrieval-augmented generation document Q&A chatbot"),
    "nlp":           ("spaCy 101 tutorial + NLTK Book", "Build a text preprocessing and keyword extraction pipeline"),
    "transformers":  ("Hugging Face Transformers course", "Fine-tune modern transformer models on custom data"),
    "hugging face":  ("Hugging Face Datasets + Hub tutorial", "Publish models and datasets to the Hugging Face Hub"),
    "spacy":         ("spaCy usage guides (spacy.io)", "Build a named entity recognition (NER) pipeline"),
    "opencv":        ("OpenCV-Python tutorials (docs.opencv.org)", "Build a real-time face detection and image filter app"),
    "cnn":           ("CS231n Stanford lecture notes", "Implement a CNN in PyTorch for image classification"),
    "yolo":          ("Ultralytics YOLOv8 quickstart guide", "Run real-time object detection on custom images"),
    "computer vision": ("DeepLearning.AI CV Specialization", "Train an object detection and segmentation model"),
    "pandas":        ("Pandas official 10-minute tutorial", "Clean and manipulate a multi-table real-world dataset"),
    "numpy":         ("NumPy quickstart tutorial (numpy.org)", "Implement vectorized matrix operations without loops"),
    "statistics":    ("StatQuest YouTube playlist", "Perform hypothesis testing, p-value analysis, and ANOVA"),
    "data analysis": ("Google Data Analytics Certificate materials", "Produce an exploratory data analysis dashboard and report"),
    # Cloud & DevOps
    "aws":           ("AWS Cloud Practitioner Essentials (free)", "Deploy a cloud-native application on AWS S3 and EC2"),
    "azure":         ("Microsoft Azure Fundamentals (AZ-900)", "Deploy a containerized web app to Azure App Service"),
    "gcp":           ("Google Cloud Skills Boost free tier", "Deploy a containerized microservice to Cloud Run"),
    "docker":        ("Docker Get-Started tutorial (docs.docker.com)", "Containerize the application with a multi-stage Dockerfile"),
    "kubernetes":    ("Kubernetes interactive tutorials", "Deploy a containerized app to a local minikube/K8s cluster"),
    "linux":         ("Linux Command Line (William Shotts, free)", "Automate server maintenance with Bash scripting"),
    "airflow":       ("Airflow Getting Started (apache.airflow.org)", "Build an automated DAG for recurring data ingestion"),
    "spark":         ("Databricks free community edition notebooks", "Run distributed data transformations with PySpark"),
    "terraform":     ("HashiCorp Terraform Tutorials", "Write Infrastructure-as-Code to provision cloud resources"),
    "ci/cd":         ("GitHub Actions CI/CD guide", "Build an automated test and deployment pipeline"),
    "github actions": ("GitHub Actions Quickstart", "Automate linting, testing, and Docker builds on pull requests"),
    "jenkins":       ("Jenkins User Documentation", "Configure a continuous integration pipeline"),
    "ansible":       ("Ansible for DevOps guide", "Automate server provisioning with playbooks"),
    "kafka":         ("Apache Kafka Quickstart", "Build a producer-consumer event streaming pipeline"),
    # Tools
    "git":           ("Pro Git (free ebook at git-scm.com)", "Contribute a feature branch with clean rebase and PR"),
    "github":        ("GitHub Skills tutorials", "Manage issues, pull requests, and GitHub Projects board"),
    "gitlab":        ("GitLab CI/CD guide", "Set up repository pipelines and merge request approvals"),
    "excel":         ("Excel for Data Analysis (GCFGlobal)", "Build pivot tables, VLOOKUP/XLOOKUP, and summary dashboards"),
    "power bi":      ("Microsoft Power BI Guided Learning", "Model relational data and build interactive KPI dashboards"),
    "tableau":       ("Tableau Public training videos", "Publish an interactive analytical story on Tableau Public"),
    "jira":          ("Atlassian Agile Coach guide", "Manage sprints, user stories, and Kanban workflows"),
    "postman":       ("Postman Student Expert course", "Create automated API test collections with environments"),
    "selenium":      ("Selenium with Python documentation", "Write an automated browser test suite for web forms"),
    "junit":         ("JUnit 5 User Guide", "Write unit and parameterized tests for software components"),
    "mlflow":        ("MLflow quickstart (mlflow.org)", "Log parameters, metrics, and register ML model artifacts"),
    "figma":         ("Figma for UI/UX Design tutorials", "Design wireframes and interactive prototypes"),
    "vscode":        ("VS Code official documentation", "Configure debugging, linting, and container extensions"),
}


def _get_resource(skill: str) -> tuple[str, str]:
    """Returns (learn_resource, project_idea) for a given skill key."""
    key = skill.strip().lower()
    return _SKILL_RESOURCES.get(
        key,
        (
            f"Search '{skill} beginner to intermediate tutorial' on YouTube / Coursera",
            f"Build a practical hands-on mini-project demonstrating core capabilities of {skill}",
        ),
    )


def analyze_skill_gaps(extracted_skills: list, target_required_skills: list) -> dict:
    """
    Identifies skills the candidate already has and skills that are missing
    for the target role.
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
    Generates a dynamic 4-week learning roadmap derived directly from
    the candidate's detected missing skills.
    
    Rules:
    - Always produces exactly 4 week sections.
    - Each week maps directly to the detected missing skills (Foundations -> Applied Tooling
      -> Advanced Integration -> End-to-End Capstone Portfolio).
    - If 1-3 skills are missing, deep-dives into those specific skills progressively
      across each week instead of generic filler.
    - If no skills are missing, provides a 4-week advanced mastery and showcase plan.
    """
    if not missing_skills:
        return [
            "🎉 **Great news!** You already possess all core skills required for this role.",
            "**Suggested next steps to maximize your job prospects:**",
            "- **Week 1:** Deepen expertise — study advanced system architecture and official docs for your core stack.",
            "- **Week 2:** Open Source Contribution — contribute a pull request or bug fix to a recognized repo.",
            "- **Week 3:** Advanced Portfolio Project — architect a full-scale project combining all your top skills.",
            "- **Week 4:** Interview & Resume Polish — tailor project bullet points, quantify impact, and conduct mock interviews.",
        ]

    clean_missing = [s.strip().lower() for s in missing_skills if s.strip()]
    num_skills = len(clean_missing)

    roadmap: list[str] = []

    # Dynamic 4-week curriculum based on missing skill count
    if num_skills == 1:
        skill = clean_missing[0]
        s_title = skill.title()
        res, proj = _get_resource(skill)
        
        roadmap.append(f"### 📅 Week 1: {s_title} Core Fundamentals & Environment Setup")
        roadmap.append(f"*Build conceptual foundations, setup toolchains, and complete core tutorials for {s_title}.*")
        roadmap.append(f"- **{s_title} Basics** — 📖 *Learn:* {res} | 🛠️ *Build:* Complete introductory exercises and syntax drills.")
        roadmap.append("")

        roadmap.append(f"### 📅 Week 2: Applied Hands-On Practice with {s_title}")
        roadmap.append(f"*Deep-dive into core APIs, best practices, and idiomatic patterns for {s_title}.*")
        roadmap.append(f"- **{s_title} in Practice** — 📖 *Learn:* Explore documentation and design patterns for {skill}. | 🛠️ *Build:* {proj}")
        roadmap.append("")

        roadmap.append(f"### 📅 Week 3: Advanced Features & Ecosystem Integration for {s_title}")
        roadmap.append(f"*Tackle complex real-world use cases, performance optimization, and testing for {s_title}.*")
        roadmap.append(f"- **{s_title} Advanced** — 📖 *Learn:* Study production-grade architectures utilizing {skill}. | 🛠️ *Build:* Implement error handling, unit tests, and performance benchmarks.")
        roadmap.append("")

        roadmap.append(f"### 📅 Week 4: Capstone Portfolio Project & Deployment")
        roadmap.append(f"*Package your work into a showcase GitHub repository with documentation and live demo.*")
        roadmap.append(f"- **{s_title} Capstone** — 📖 *Learn:* Write a comprehensive README, architecture diagram, and setup guide. | 🛠️ *Build:* Publish your completed {s_title} project and highlight it on your resume.")
        roadmap.append("")

    elif num_skills == 2:
        s1, s2 = clean_missing[0], clean_missing[1]
        t1, t2 = s1.title(), s2.title()
        res1, proj1 = _get_resource(s1)
        res2, proj2 = _get_resource(s2)

        roadmap.append(f"### 📅 Week 1: {t1} Fundamentals & Core Syntax")
        roadmap.append(f"*Establish a solid foundation in {t1} with guided tutorials and basic implementations.*")
        roadmap.append(f"- **{t1}** — 📖 *Learn:* {res1} | 🛠️ *Build:* {proj1}")
        roadmap.append("")

        roadmap.append(f"### 📅 Week 2: {t2} Fundamentals & Tooling")
        roadmap.append(f"*Establish a solid foundation in {t2} through targeted exercises and environment setup.*")
        roadmap.append(f"- **{t2}** — 📖 *Learn:* {res2} | 🛠️ *Build:* {proj2}")
        roadmap.append("")

        roadmap.append(f"### 📅 Week 3: Integrating {t1} and {t2}")
        roadmap.append(f"*Combine {t1} and {t2} in an applied pipeline to solve realistic technical problems.*")
        roadmap.append(f"- **{t1} + {t2} Synergy** — 📖 *Learn:* Study architectural patterns combining {s1} with {s2}. | 🛠️ *Build:* Build an intermediate project integrating {t1} and {t2}.")
        roadmap.append("")

        roadmap.append(f"### 📅 Week 4: End-to-End Capstone Project & Resume Alignment")
        roadmap.append(f"*Deploy a polished portfolio project demonstrating both {t1} and {t2} in production.*")
        roadmap.append(f"- **Portfolio Capstone** — 📖 *Learn:* Structure GitHub repository with CI/CD and documentation. | 🛠️ *Build:* Finalize an end-to-end project leveraging both {t1} and {t2}, ready for recruiter review.")
        roadmap.append("")

    elif num_skills == 3:
        s1, s2, s3 = clean_missing[0], clean_missing[1], clean_missing[2]
        t1, t2, t3 = s1.title(), s2.title()
        res1, proj1 = _get_resource(s1)
        res2, proj2 = _get_resource(s2)
        res3, proj3 = _get_resource(s3)

        roadmap.append(f"### 📅 Week 1: Foundation Focus — {t1}")
        roadmap.append(f"*Master core concepts and fundamental toolchains for {t1}.*")
        roadmap.append(f"- **{t1}** — 📖 *Learn:* {res1} | 🛠️ *Build:* {proj1}")
        roadmap.append("")

        roadmap.append(f"### 📅 Week 2: Applied Tooling — {t2}")
        roadmap.append(f"*Tackle applied workflows and practical implementations with {t2}.*")
        roadmap.append(f"- **{t2}** — 📖 *Learn:* {res2} | 🛠️ *Build:* {proj2}")
        roadmap.append("")

        roadmap.append(f"### 📅 Week 3: Advanced Competency — {s3.title()}")
        roadmap.append(f"*Gain proficiency in {s3.title()} and study integration with your existing stack.*")
        roadmap.append(f"- **{s3.title()}** — 📖 *Learn:* {res3} | 🛠️ *Build:* {proj3}")
        roadmap.append("")

        roadmap.append(f"### 📅 Week 4: Full-Stack Integration & Capstone Showcase")
        roadmap.append(f"*Unify {t1}, {t2}, and {s3.title()} in an end-to-end portfolio application.*")
        roadmap.append(f"- **Portfolio Project** — 📖 *Learn:* Production deployment, logging, and documentation. | 🛠️ *Build:* Build a capstone combining {t1}, {t2}, and {s3.title()} to showcase in job applications.")
        roadmap.append("")

    else:
        # 4 or more missing skills: distribute dynamically across 4 structured themes
        buckets: list[list[str]] = [[] for _ in range(4)]
        for i, skill in enumerate(clean_missing):
            buckets[i % 4].append(skill)

        themes = [
            ("Foundations & Core Setup", "Master syntax, installation, and theoretical foundations for this week's skills:"),
            ("Applied Tooling & Practice", "Implement hands-on exercises and practical workflows for this week's skills:"),
            ("Advanced Implementation & Scaling", "Deep-dive into advanced APIs, error handling, and architecture for this week's skills:"),
            ("End-to-End Integration & Capstone", "Synthesize all newly acquired skills into a unified portfolio project:"),
        ]

        for week_idx, (theme, instruction) in enumerate(themes):
            week_num = week_idx + 1
            week_skills = buckets[week_idx]
            skill_names = ", ".join(s.title() for s in week_skills)

            roadmap.append(f"### 📅 Week {week_num}: {theme} ({skill_names})")
            roadmap.append(f"*{instruction}*")

            for skill in week_skills:
                resource, project = _get_resource(skill)
                roadmap.append(
                    f"- **{skill.title()}** — 📖 *Learn:* {resource} | "
                    f"🛠️ *Build:* {project}"
                )
            roadmap.append("")

    return roadmap