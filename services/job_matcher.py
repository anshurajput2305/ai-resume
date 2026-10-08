import re
from typing import Dict, Any, List
from services.skill_extractor import SkillExtractor

class JobMatcher:
    """
    Compares resume against a Job Description for ATS keyword matching and skill gap analysis.
    """

    COMMON_STOPWORDS = {
        "and", "the", "for", "with", "that", "this", "from", "you", "your", "will",
        "our", "are", "have", "has", "must", "can", "work", "team", "role", "looking",
        "years", "experience", "candidate", "about", "such", "join", "help", "across",
        "working", "responsibilities", "requirements", "skills", "qualifications",
        "ability", "strong", "knowledge", "including", "using", "plus", "preferred"
    }

    @classmethod
    def match(cls, resume_text: str, resume_skills: List[str], job_description: str) -> Dict[str, Any]:
        """
        Calculates match score, sub-scores, matched keywords, missing skills, prioritized gaps, and recommendations.
        """
        if not job_description.strip():
            raise ValueError("Job description cannot be empty.")

        # 1. Extract skills from Job Description
        jd_skills_data = SkillExtractor.extract_skills(job_description)
        jd_skills = jd_skills_data.get("all_skills", [])
        jd_categorized = jd_skills_data.get("categorized_skills", {})

        resume_skills_lower = {s.lower(): s for s in resume_skills}
        resume_text_lower = resume_text.lower()
        
        matched_skills = []
        missing_skills = []

        for skill in jd_skills:
            if skill.lower() in resume_skills_lower or re.search(r"\b" + re.escape(skill) + r"\b", resume_text, re.IGNORECASE):
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        # 2. Extract technical & domain keywords from JD
        jd_words = re.findall(r"\b[a-zA-Z]{3,}\b", job_description.lower())
        jd_word_freq: Dict[str, int] = {}
        for w in jd_words:
            if w not in cls.COMMON_STOPWORDS and len(w) > 3:
                jd_word_freq[w] = jd_word_freq.get(w, 0) + 1

        top_jd_keywords = [
            word for word, count in sorted(jd_word_freq.items(), key=lambda x: x[1], reverse=True)[:25]
        ]

        matched_keywords = []
        missing_keywords = []

        for kw in top_jd_keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", resume_text_lower):
                matched_keywords.append(kw)
            else:
                missing_keywords.append(kw)

        # 3. Calculate Sub-Scores
        # Skills Match %
        if jd_skills:
            skill_match_pct = round((len(matched_skills) / len(jd_skills)) * 100)
        else:
            skill_match_pct = 75

        # Keyword Match %
        if top_jd_keywords:
            kw_match_pct = round((len(matched_keywords) / len(top_jd_keywords)) * 100)
        else:
            kw_match_pct = 70

        # Experience & Project Match %
        exp_match_pct = min(100, round((skill_match_pct * 0.7) + (kw_match_pct * 0.3) + 5))
        proj_match_pct = min(100, round((skill_match_pct * 0.8) + 10))

        # Overall Weighted Match Score
        overall_match = round(
            (skill_match_pct * 0.40) +
            (kw_match_pct * 0.25) +
            (exp_match_pct * 0.20) +
            (proj_match_pct * 0.15)
        )
        overall_match = max(15, min(98, overall_match))

        # 4. Readiness Classification
        if overall_match >= 80:
            fit_level = "Strong Match — Excellent alignment with role requirements"
            fit_color = "green"
        elif overall_match >= 60:
            fit_level = "Moderate Match — Competitive candidate; bridge key skill gaps"
            fit_color = "yellow"
        else:
            fit_level = "Low Match — Significant technical skills or keywords missing"
            fit_color = "red"

        # 5. Prioritized Skill Gaps
        high_priority = []
        med_priority = []
        low_priority = []

        # Categorize missing skills by priority
        for skill in missing_skills:
            # Check which category it belongs to
            is_language_or_backend = any(
                skill in cat_list for cat_name, cat_list in jd_categorized.items() 
                if cat_name in ["Programming Languages", "Backend Development", "Frontend Development"]
            )
            is_infra_or_db = any(
                skill in cat_list for cat_name, cat_list in jd_categorized.items() 
                if cat_name in ["Databases & Storage", "Cloud & DevOps", "AI, ML & Data Science"]
            )

            if is_language_or_backend:
                high_priority.append(skill)
            elif is_infra_or_db:
                med_priority.append(skill)
            else:
                low_priority.append(skill)

        # Fallback distribution if categories not matched
        if not high_priority and missing_skills:
            high_priority = missing_skills[:2]
            med_priority = missing_skills[2:4]
            low_priority = missing_skills[4:]

        # 6. Personalized Recommendations
        tailoring_tips = []
        if high_priority:
            tailoring_tips.append(
                f"Highlight experience with {', '.join(high_priority[:3])} in your summary and project bullets (only if you have hands-on experience)."
            )
        if missing_keywords:
            tailoring_tips.append(
                f"Incorporate missing domain terms: '{', '.join(missing_keywords[:4])}' organically into your experience descriptions."
            )
        tailoring_tips.append(
            "Mirror key phrases from the job description's responsibilities section to maximize ATS keyword scoring."
        )
        if med_priority:
            tailoring_tips.append(
                f"Mention complementary tools like {', '.join(med_priority[:3])} in your technical skills section if applicable."
            )

        return {
            "match_score": overall_match,
            "fit_level": fit_level,
            "fit_color": fit_color,
            "breakdown": {
                "skills_match": skill_match_pct,
                "experience_match": exp_match_pct,
                "projects_match": proj_match_pct,
                "keywords_match": kw_match_pct
            },
            "metrics": {
                "skill_match_rate": skill_match_pct,
                "keyword_match_rate": kw_match_pct,
                "total_jd_skills_required": len(jd_skills),
                "matched_skills_count": len(matched_skills),
                "missing_skills_count": len(missing_skills)
            },
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "prioritized_gaps": {
                "high_priority": high_priority,
                "medium_priority": med_priority,
                "low_priority": low_priority
            },
            "matched_keywords": matched_keywords[:15],
            "missing_keywords": missing_keywords[:15],
            "tailoring_tips": tailoring_tips
        }
