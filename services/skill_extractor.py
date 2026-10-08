import re
from typing import Dict, List, Any, Set

class SkillExtractor:
    """
    Categorized skill extraction engine with boundary-safe matching.
    """

    TAXONOMY: Dict[str, List[Dict[str, Any]]] = {
        "programming_languages": [
            {"name": "Python", "pattern": r"\bpython\b"},
            {"name": "JavaScript", "pattern": r"\b(?:javascript|js|es6|ecmascript)\b"},
            {"name": "TypeScript", "pattern": r"\b(?:typescript|ts)\b"},
            {"name": "Java", "pattern": r"\bjava\b(?!\s*script)"},
            {"name": "C++", "pattern": r"\bc\+\+\b"},
            {"name": "C#", "pattern": r"\bc\#|\bc\s*sharp\b"},
            {"name": "C", "pattern": r"(?<!\w)c(?!\w|\+|\#)"},
            {"name": "Go / Golang", "pattern": r"\b(?:golang|go\s+language)\b|(?<=\s)go(?=\s*,|\s*\n|\s*\))"},
            {"name": "Rust", "pattern": r"\brust\b"},
            {"name": "PHP", "pattern": r"\bphp\b"},
            {"name": "Ruby", "pattern": r"\bruby\b(?!\s*on\s*rails)"},
            {"name": "Swift", "pattern": r"\bswift\b"},
            {"name": "Kotlin", "pattern": r"\bkotlin\b"},
            {"name": "Dart", "pattern": r"\bdart\b"},
            {"name": "Scala", "pattern": r"\bscala\b"},
            {"name": "R", "pattern": r"(?<!\w)r(?!\w|\+)(?=\s+programming|\s+language|\s*,|\s*\))"},
            {"name": "SQL", "pattern": r"\bsql\b"},
            {"name": "Shell / Bash", "pattern": r"\b(?:bash|shell\s*scripting|powershell|zsh)\b"}
        ],
        "frontend": [
            {"name": "React.js", "pattern": r"\breact(?:\.?js)?\b"},
            {"name": "Next.js", "pattern": r"\bnext(?:\.?js)?\b"},
            {"name": "Vue.js", "pattern": r"\bvue(?:\.?js)?\b"},
            {"name": "Angular", "pattern": r"\bangular(?:\.?js)?\b"},
            {"name": "Svelte", "pattern": r"\bsvelte\b"},
            {"name": "HTML5", "pattern": r"\bhtml5?\b"},
            {"name": "CSS3", "pattern": r"\bcss3?\b"},
            {"name": "Tailwind CSS", "pattern": r"\btailwind(?:\s*css)?\b"},
            {"name": "Bootstrap", "pattern": r"\bbootstrap\b"},
            {"name": "Redux", "pattern": r"\bredux\b|redux\s*toolkit"},
            {"name": "Sass / SCSS", "pattern": r"\b(?:sass|scss)\b"},
            {"name": "Vite", "pattern": r"\bvite\b"},
            {"name": "Webpack", "pattern": r"\bwebpack\b"},
            {"name": "jQuery", "pattern": r"\bjquery\b"},
            {"name": "Zustand", "pattern": r"\bzustand\b"}
        ],
        "backend": [
            {"name": "Node.js", "pattern": r"\bnode(?:\.?js)?\b"},
            {"name": "Express.js", "pattern": r"\bexpress(?:\.?js)?\b"},
            {"name": "FastAPI", "pattern": r"\bfastapi\b"},
            {"name": "Django", "pattern": r"\bdjango\b"},
            {"name": "Flask", "pattern": r"\bflask\b"},
            {"name": "Spring Boot", "pattern": r"\bspring(?:\s*boot)?\b"},
            {"name": "Ruby on Rails", "pattern": r"\b(?:rails|ruby\s*on\s*rails)\b"},
            {"name": "ASP.NET", "pattern": r"\basp\.net(?:\s*core)?\b"},
            {"name": "NestJS", "pattern": r"\bnest(?:\.?js)?\b"},
            {"name": "RESTful APIs", "pattern": r"\brest(?:ful)?\s*api(?:s)?\b"},
            {"name": "GraphQL", "pattern": r"\bgraphql\b"},
            {"name": "Microservices", "pattern": r"\bmicroservices?\b"},
            {"name": "gRPC", "pattern": r"\bgrpc\b"},
            {"name": "WebSockets", "pattern": r"\bwebsockets?\b"}
        ],
        "database": [
            {"name": "PostgreSQL", "pattern": r"\b(?:postgres|postgresql)\b"},
            {"name": "MySQL", "pattern": r"\bmysql\b"},
            {"name": "MongoDB", "pattern": r"\bmongodb|mongo\b"},
            {"name": "Redis", "pattern": r"\bredis\b"},
            {"name": "SQLite", "pattern": r"\bsqlite\b"},
            {"name": "Oracle DB", "pattern": r"\boracle(?:\s*db|\s*database)?\b"},
            {"name": "Cassandra", "pattern": r"\bcassandra\b"},
            {"name": "DynamoDB", "pattern": r"\bdynamodb\b"},
            {"name": "Firebase", "pattern": r"\bfirebase\b"},
            {"name": "Supabase", "pattern": r"\bsupabase\b"},
            {"name": "Elasticsearch", "pattern": r"\belasticsearch\b"},
            {"name": "Prisma ORM", "pattern": r"\bprisma\b"}
        ],
        "cloud_devops": [
            {"name": "AWS", "pattern": r"\baws\b|amazon\s*web\s*services"},
            {"name": "Azure", "pattern": r"\bazure\b|microsoft\s*azure"},
            {"name": "Google Cloud (GCP)", "pattern": r"\b(?:gcp|google\s*cloud)\b"},
            {"name": "Docker", "pattern": r"\bdocker\b"},
            {"name": "Kubernetes", "pattern": r"\b(?:k8s|kubernetes)\b"},
            {"name": "CI/CD", "pattern": r"\bci[\/\-]cd\b|continuous\s*integration"},
            {"name": "GitHub Actions", "pattern": r"\bgithub\s*actions\b"},
            {"name": "Jenkins", "pattern": r"\bjenkins\b"},
            {"name": "Terraform", "pattern": r"\bterraform\b"},
            {"name": "Linux", "pattern": r"\blinux\b|ubuntu|debian|centos"},
            {"name": "Nginx", "pattern": r"\bnginx\b"},
            {"name": "Ansible", "pattern": r"\bansible\b"}
        ],
        "ai_data_science": [
            {"name": "Machine Learning", "pattern": r"\bmachine\s*learning|\bml\b"},
            {"name": "Deep Learning", "pattern": r"\bdeep\s*learning\b"},
            {"name": "PyTorch", "pattern": r"\bpytorch\b"},
            {"name": "TensorFlow", "pattern": r"\btensorflow\b|keras"},
            {"name": "Scikit-Learn", "pattern": r"\bscikit[\-_]learn|sklearn\b"},
            {"name": "Pandas", "pattern": r"\bpandas\b"},
            {"name": "NumPy", "pattern": r"\bnumpy\b"},
            {"name": "NLP", "pattern": r"\bnlp\b|natural\s*language\s*processing"},
            {"name": "Large Language Models (LLMs)", "pattern": r"\b(?:llm|llms|generative\s*ai|langchain|transformers|openai|huggingface)\b"},
            {"name": "Computer Vision / OpenCV", "pattern": r"\b(?:computer\s*vision|opencv)\b"},
            {"name": "Data Analysis", "pattern": r"\bdata\s*analysis|data\s*analytics\b"},
            {"name": "Power BI", "pattern": r"\bpower\s*bi\b"},
            {"name": "Tableau", "pattern": r"\btableau\b"}
        ],
        "mobile": [
            {"name": "Flutter", "pattern": r"\bflutter\b"},
            {"name": "React Native", "pattern": r"\breact\s*native\b"},
            {"name": "Android Dev", "pattern": r"\bandroid\s*(?:development|app|studio)?\b"},
            {"name": "iOS Dev", "pattern": r"\bios\s*(?:development|app)?\b|swiftui"}
        ],
        "tools_testing": [
            {"name": "Git", "pattern": r"\bgit\b(?!\s*hub|\s*lab)"},
            {"name": "GitHub", "pattern": r"\bgithub\b"},
            {"name": "GitLab", "pattern": r"\bgitlab\b"},
            {"name": "Jira", "pattern": r"\bjira\b"},
            {"name": "Postman", "pattern": r"\bpostman\b"},
            {"name": "Jest", "pattern": r"\bjest\b"},
            {"name": "PyTest", "pattern": r"\bpytest\b"},
            {"name": "Selenium", "pattern": r"\bselenium\b"},
            {"name": "Cypress", "pattern": r"\bcypress\b"},
            {"name": "Figma", "pattern": r"\bfigma\b"},
            {"name": "VS Code", "pattern": r"\bvs\s*code|visual\s*studio\s*code\b"}
        ],
        "soft_skills": [
            {"name": "Leadership", "pattern": r"\bleadership|led\s+a\s+team\b"},
            {"name": "Communication", "pattern": r"\bcommunication\s*(?:skills)?\b"},
            {"name": "Problem Solving", "pattern": r"\bproblem\s*solving\b"},
            {"name": "Teamwork & Collaboration", "pattern": r"\b(?:teamwork|collaboration|team\s*player)\b"},
            {"name": "Agile / Scrum", "pattern": r"\b(?:agile|scrum|kanban)\b"},
            {"name": "Critical Thinking", "pattern": r"\bcritical\s*thinking\b"},
            {"name": "Project Management", "pattern": r"\bproject\s*management\b"},
            {"name": "Mentoring", "pattern": r"\bmentoring|mentored\b"}
        ]
    }

    CATEGORY_LABELS = {
        "programming_languages": "Programming Languages",
        "frontend": "Frontend Development",
        "backend": "Backend Development",
        "database": "Databases & Storage",
        "cloud_devops": "Cloud & DevOps",
        "ai_data_science": "AI, ML & Data Science",
        "mobile": "Mobile Development",
        "tools_testing": "Tools & Testing",
        "soft_skills": "Soft Skills"
    }

    @classmethod
    def extract_skills(cls, text: str) -> Dict[str, Any]:
        """
        Extracts skills from raw resume text, returning flat list and categorized map.
        """
        lower_text = " " + text.lower() + " "
        categorized: Dict[str, List[str]] = {}
        all_skills: List[str] = []
        seen: Set[str] = set()

        for cat_key, skill_defs in cls.TAXONOMY.items():
            cat_label = cls.CATEGORY_LABELS.get(cat_key, cat_key)
            matched_in_cat: List[str] = []

            for item in skill_defs:
                name = item["name"]
                pattern = item["pattern"]
                
                if re.search(pattern, lower_text, re.IGNORECASE):
                    if name not in seen:
                        matched_in_cat.append(name)
                        all_skills.append(name)
                        seen.add(name)

            if matched_in_cat:
                categorized[cat_label] = matched_in_cat

        return {
            "total_skills_count": len(all_skills),
            "all_skills": all_skills,
            "categorized_skills": categorized
        }
