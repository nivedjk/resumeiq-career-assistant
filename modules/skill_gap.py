skills_list = [

    # Programming Languages
    "python", "java", "c", "c++", "c#", "javascript", "typescript",
    "php", "ruby", "go", "rust", "kotlin", "swift", "scala",
    "r", "matlab", "perl", "dart", "shell scripting", "bash",

    # Web Development
    "html", "css", "bootstrap", "tailwind css", "react", "reactjs",
    "angular", "vue", "nodejs", "expressjs", "nextjs", "jquery",
    "ajax", "rest api", "graphql", "websocket",

    # Databases
    "sql", "mysql", "postgresql", "mongodb", "oracle", "sqlite",
    "redis", "cassandra", "dynamodb", "firebase", "mariadb",
    "neo4j", "elasticsearch",

    # Data Science
    "data analysis", "data visualization", "data mining",
    "statistics", "predictive analytics", "business analytics",
    "exploratory data analysis", "eda", "feature engineering",
    "hypothesis testing", "a/b testing",

    # Python Libraries
    "pandas", "numpy", "matplotlib", "seaborn",
    "scikit-learn", "scipy", "plotly", "statsmodels",
    "beautifulsoup", "selenium", "requests",

    # Machine Learning
    "machine learning", "supervised learning",
    "unsupervised learning", "reinforcement learning",
    "classification", "regression", "clustering",
    "decision trees", "random forest",
    "xgboost", "lightgbm", "catboost",
    "support vector machine", "svm",
    "knn", "naive bayes",

    # Deep Learning
    "deep learning", "artificial neural networks",
    "cnn", "convolutional neural network",
    "rnn", "lstm", "gru",
    "transformers", "attention mechanism",

    # AI / GenAI
    "artificial intelligence",
    "generative ai",
    "large language models",
    "llm",
    "prompt engineering",
    "rag",
    "langchain",
    "llamaindex",
    "huggingface",
    "ollama",
    "openai",
    "chatgpt",
    "vector database",
    "embedding",
    "fine tuning",

    # NLP
    "natural language processing",
    "nlp",
    "text classification",
    "sentiment analysis",
    "named entity recognition",
    "tokenization",
    "spacy",
    "nltk",

    # Computer Vision
    "computer vision",
    "opencv",
    "image processing",
    "object detection",
    "yolo",
    "image classification",

    # Cloud
    "aws",
    "azure",
    "google cloud",
    "gcp",
    "ec2",
    "s3",
    "lambda",
    "cloud computing",

    # DevOps
    "docker",
    "kubernetes",
    "jenkins",
    "terraform",
    "ansible",
    "gitlab ci",
    "github actions",
    "ci/cd",

    # Operating Systems
    "linux",
    "ubuntu",
    "unix",
    "windows server",

    # Version Control
    "git",
    "github",
    "gitlab",
    "bitbucket",

    # Big Data
    "hadoop",
    "spark",
    "pyspark",
    "hive",
    "kafka",
    "airflow",

    # BI Tools
    "power bi",
    "tableau",
    "qlikview",
    "looker",
    "google data studio",

    # Testing
    "unit testing",
    "pytest",
    "selenium testing",
    "automation testing",
    "junit",

    # Mobile Development
    "android",
    "flutter",
    "react native",
    "ios development",

    # Cyber Security
    "cybersecurity",
    "penetration testing",
    "ethical hacking",
    "network security",
    "owasp",

    # Networking
    "tcp/ip",
    "dns",
    "vpn",
    "routing",
    "switching",

    # ERP / CRM
    "sap",
    "salesforce",
    "crm",
    "erp",

    # Project Management
    "agile",
    "scrum",
    "kanban",
    "jira",
    "confluence",

    # Data Engineering
    "etl",
    "data warehousing",
    "data pipeline",
    "snowflake",
    "databricks",

    # Software Engineering
    "oop",
    "object oriented programming",
    "design patterns",
    "microservices",
    "system design",
    "api development",

    # Finance / Analytics
    "financial analysis",
    "forecasting",
    "risk analysis",

    # Soft Skills
    "communication",
    "leadership",
    "problem solving",
    "critical thinking",
    "teamwork",
    "time management",
    "presentation skills",
    "analytical thinking",
    "adaptability",
    "decision making",

    # Tools
    "excel",
    "word",
    "powerpoint",
    "google sheets",
    "notion",
    "postman",
    "figma",
    "canva",

    # Emerging Tech
    "blockchain",
    "internet of things",
    "iot",
    "augmented reality",
    "virtual reality",
    "robotics",
    "edge computing",

    # Data Structures & Algorithms
    "data structures",
    "algorithms",
    "competitive programming",
    "dynamic programming",
    "graph algorithms",

    # Placement-Focused Skills
    "dbms",
    "operating systems",
    "computer networks",
    "oops",
    "software engineering",
    "aptitude",
    "problem solving"
]

def extract_skills(text):

    text = text.lower()

    found = []

    for skill in skills_list:
        if skill in text:
            found.append(skill)

    return found


def missing_skills(resume_skills, jd_skills):

    return list(
        set(jd_skills) - set(resume_skills)
    )