import os
import re
import json
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

class AIAssistant:
    """
    AI Career Assistant powered exclusively by Google Gemini.
    """

    # Supported Gemini models in priority order
    GEMINI_MODELS = [
        "gemini-3.5-flash",
        "gemini-3-flash-preview",
        "gemini-flash-latest"
    ]

    @classmethod
    def _get_api_key(cls) -> str:
        key = os.getenv("GEMINI_API_KEY", "").strip()
        if not key:
            raise ValueError(
                "Google Gemini API Key is missing. Please configure 'GEMINI_API_KEY=your_key_here' in your .env file."
            )
        return key

    @classmethod
    def _call_gemini(cls, system_prompt: str, user_prompt: str, expect_json: bool = True) -> str:
        key = cls._get_api_key()

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": f"{system_prompt}\n\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2048,
                **({"responseMimeType": "application/json"} if expect_json else {})
            }
        }

        last_error = None

        # Try models in priority order
        for model in cls.GEMINI_MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            try:
                resp = requests.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=20
                )

                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        output_text = "".join(p.get("text", "") for p in parts)
                        if output_text.strip():
                            return output_text
                elif resp.status_code in [404, 503, 429]:
                    # Try next model in list
                    last_error = f"Model {model} returned status {resp.status_code}"
                    continue
                else:
                    err_msg = "Gemini API request failed"
                    try:
                        err_msg = resp.json().get("error", {}).get("message", err_msg)
                    except Exception:
                        pass
                    raise RuntimeError(f"Gemini API error ({resp.status_code}): {err_msg}")

            except requests.exceptions.Timeout:
                last_error = f"Request timeout on model {model}"
                continue
            except requests.exceptions.RequestException as req_err:
                last_error = str(req_err)
                continue

        raise RuntimeError(f"Google Gemini service is temporarily unavailable. ({last_error or 'No response'})")

    @classmethod
    def _parse_json_safely(cls, raw_response: str) -> Any:
        cleaned = re.sub(r"^```(?:json)?|```$", "", raw_response.strip(), flags=re.MULTILINE).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise ValueError(f"Could not parse Gemini output as structured JSON.")

    @classmethod
    def suggest_job_roles(cls, resume_text: str, skills: List[str]) -> List[Dict[str, Any]]:
        """
        Uses Google Gemini to analyze resume content & skills and suggest matching career roles.
        """
        system_prompt = (
            "You are an expert tech career advisor powered by Google Gemini. "
            "Analyze the candidate's skills and resume to suggest 6 to 8 tailored job roles. "
            "Return structured JSON matching: {\"roles\": [{\"title\": \"...\", \"match_score\": 90, \"rationale\": \"...\"}]}"
        )
        user_prompt = (
            f"Candidate Skills: {', '.join(skills[:15])}\n\n"
            f"Resume Excerpt:\n{resume_text[:2000]}\n\n"
            "Generate 6 to 8 realistic role recommendations."
        )

        try:
            raw = cls._call_gemini(system_prompt, user_prompt, expect_json=True)
            data = cls._parse_json_safely(raw)
            if isinstance(data, dict) and "roles" in data:
                return data["roles"]
            elif isinstance(data, list):
                return data
            return []
        except Exception:
            # Deterministic fallback roles based on skill taxonomy
            fallback_roles = []
            skills_lower = [s.lower() for s in skills]
            if any(s in skills_lower for s in ["react.js", "next.js", "frontend development", "html5", "css3"]):
                fallback_roles.append({"title": "Frontend Developer", "match_score": 88, "rationale": "Strong expertise in modern frontend frameworks and UI development."})
            if any(s in skills_lower for s in ["python", "node.js", "fastapi", "django", "spring boot", "backend development"]):
                fallback_roles.append({"title": "Backend Software Engineer", "match_score": 87, "rationale": "Demonstrated background in server-side architecture, APIs, and databases."})
            if any(s in skills_lower for s in ["python", "machine learning", "deep learning", "pytorch", "pandas"]):
                fallback_roles.append({"title": "AI / Machine Learning Engineer", "match_score": 85, "rationale": "Hands-on experience with ML algorithms, modeling, and data pipelines."})
            if any(s in skills_lower for s in ["aws", "docker", "kubernetes", "ci/cd", "cloud & devops"]):
                fallback_roles.append({"title": "DevOps & Cloud Engineer", "match_score": 84, "rationale": "Proficiency in containerization, CI/CD automation, and cloud deployments."})
            if not fallback_roles:
                fallback_roles.append({"title": "Software Development Engineer", "match_score": 82, "rationale": "Solid programming foundation and software engineering skills."})
            return fallback_roles

    @classmethod
    def improve_bullet_point(cls, bullet_text: str, target_role: str = "Software Engineer") -> Dict[str, Any]:
        """
        Uses Google Gemini to rewrite a resume bullet point using the STAR framework.
        """
        system_prompt = (
            "You are a professional resume writer and career coach powered by Google Gemini. "
            "Rewrite the candidate's resume bullet point to make it high-impact, quantified, and ATS-optimized "
            "using the STAR framework (Situation, Task, Action, Result). "
            "Rules:\n"
            "1. Use strong active power verbs.\n"
            "2. Make phrasing concise and impactful.\n"
            "3. Preserve all factual information; do NOT invent fake achievements.\n"
            "4. Add metrics and scale indicators only where contextually appropriate.\n"
            "Return JSON matching:\n"
            "{\n"
            "  \"original\": \"...\",\n"
            "  \"improved_bullet\": \"... (top recommendation)\",\n"
            "  \"improved_options\": [\n"
            "    {\"style\": \"Impact & Scale\", \"text\": \"...\"},\n"
            "    {\"style\": \"Leadership & Execution\", \"text\": \"...\"},\n"
            "    {\"style\": \"Concise Technical\", \"text\": \"...\"}\n"
            "  ],\n"
            "  \"action_verb_used\": \"...\",\n"
            "  \"quantifiable_metric_added\": \"...\",\n"
            "  \"skills_used\": [\"...\"],\n"
            "  \"key_changes\": \"...\"\n"
            "}"
        )
        user_prompt = (
            f"Target Role: {target_role}\n"
            f"Original Bullet Point:\n\"{bullet_text}\"\n\n"
            "Rewrite this bullet into 3 distinct high-impact variations."
        )

        raw = cls._call_gemini(system_prompt, user_prompt, expect_json=True)
        parsed = cls._parse_json_safely(raw)
        
        # Ensure improved_bullet is present
        if "improved_bullet" not in parsed and "improved_options" in parsed and parsed["improved_options"]:
            parsed["improved_bullet"] = parsed["improved_options"][0].get("text", "")
            
        return parsed

    @classmethod
    def generate_interview_prep(
        cls,
        resume_text: str,
        target_role: str,
        skills: List[str]
    ) -> Dict[str, Any]:
        """
        Uses Google Gemini to generate custom Technical, Project Deep-Dive, Behavioral (STAR), and HR interview questions.
        """
        system_prompt = (
            "You are a principal technical hiring manager powered exclusively by Google Gemini. "
            "Analyze the candidate's resume and target role to create a customized, realistic interview preparation packet.\n"
            "Rules:\n"
            "1. Technical Questions must directly probe the candidate's actual technologies, libraries, and frameworks.\n"
            "2. Project Deep-Dive Questions must probe specific architecture choices and challenges from the projects in the resume.\n"
            "3. Behavioral Questions must use the STAR method (Situation, Task, Action, Result).\n"
            "4. HR Questions must cover role-specific motivation and teamwork.\n"
            "5. Do NOT invent technologies, tools, or projects not present in the candidate's resume.\n"
            "Return JSON matching this exact structure:\n"
            "{\n"
            "  \"role_title\": \"...\",\n"
            "  \"technical_questions\": [\n"
            "    {\"question\": \"...\", \"difficulty\": \"Medium\", \"ideal_concepts\": \"...\", \"sample_answer\": \"...\"}\n"
            "  ],\n"
            "  \"project_deep_dive_questions\": [\n"
            "    {\"question\": \"...\", \"difficulty\": \"Hard\", \"trap_to_avoid\": \"...\", \"tips\": \"...\", \"sample_answer\": \"...\"}\n"
            "  ],\n"
            "  \"behavioral_questions\": [\n"
            "    {\"question\": \"...\", \"difficulty\": \"Medium\", \"star_framework\": \"...\", \"sample_answer\": \"...\"}\n"
            "  ],\n"
            "  \"hr_questions\": [\n"
            "    {\"question\": \"...\", \"difficulty\": \"Easy\", \"key_talking_point\": \"...\", \"sample_answer\": \"...\"}\n"
            "  ]\n"
            "}"
        )
        user_prompt = (
            f"Target Role: {target_role}\n"
            f"Candidate Skills: {', '.join(skills[:12]) if skills else 'Extracted from resume'}\n\n"
            f"Resume Context:\n{resume_text[:2800]}\n\n"
            "Generate customized interview questions tailored strictly to this candidate's resume and target role."
        )

        raw = cls._call_gemini(system_prompt, user_prompt, expect_json=True)
        parsed = cls._parse_json_safely(raw)
        
        # Alias keys for multi-format compatibility
        parsed["technical"] = parsed.get("technical_questions", [])
        parsed["project_questions"] = parsed.get("project_deep_dive_questions", [])
        parsed["project"] = parsed.get("project_deep_dive_questions", [])
        parsed["behavioral"] = parsed.get("behavioral_questions", [])
        parsed["hr"] = parsed.get("hr_questions", [])
        
        return parsed

    @classmethod
    def generate_learning_roadmap(
        cls,
        missing_skills: List[str],
        target_role: str,
        job_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Uses Google Gemini to generate a structured 4-week skill development roadmap.
        """
        system_prompt = (
            "You are a senior career mentor powered by Google Gemini. "
            "Create a structured 4-week accelerated learning and portfolio roadmap "
            "to help the candidate master missing skills required for their target role.\n"
            "Return JSON matching:\n"
            "{\n"
            "  \"target_role\": \"...\",\n"
            "  \"missing_skills\": [\"...\"],\n"
            "  \"weeks\": [\n"
            "    {\n"
            "      \"week_number\": 1,\n"
            "      \"title\": \"...\",\n"
            "      \"topics\": [\"...\"],\n"
            "      \"focus_skills\": \"...\",\n"
            "      \"learning_goals\": \"...\",\n"
            "      \"practical_tasks\": [\"...\"],\n"
            "      \"hands_on_project\": \"...\",\n"
            "      \"recommended_resources\": \"...\"\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        user_prompt = (
            f"Target Role: {target_role}\n"
            f"Missing Skills to Bridge: {', '.join(missing_skills[:8])}\n"
            f"{'Target Job Description excerpt: ' + job_description[:1000] if job_description else ''}\n\n"
            "Generate a practical, week-by-week roadmap with concrete hands-on projects."
        )

        raw = cls._call_gemini(system_prompt, user_prompt, expect_json=True)
        return cls._parse_json_safely(raw)
