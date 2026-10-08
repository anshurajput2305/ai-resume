import re
from typing import Dict, Any, List
from services.skill_extractor import SkillExtractor

class ATSAnalyzer:
    """
    Deterministic, comprehensive ATS and Resume Evaluation Engine.
    """

    ACTION_VERBS = [
        "accelerated", "accomplished", "achieved", "acquired", "adapted", "administered",
        "advanced", "advised", "analyzed", "architected", "authored", "automated",
        "built", "championed", "collaborated", "constructed", "coordinated", "created",
        "decreased", "delivered", "deployed", "designed", "developed", "devised",
        "directed", "doubled", "drove", "engineered", "enhanced", "established",
        "executed", "expanded", "expedited", "fabricated", "formulated", "founded",
        "generated", "guided", "implemented", "improved", "increased", "initiated",
        "innovated", "installed", "instituted", "integrated", "introduced", "invented",
        "launched", "led", "managed", "maximized", "mentored", "migrated", "minimized",
        "modernized", "monitored", "negotiated", "optimized", "orchestrated", "organized",
        "overhauled", "oversaw", "partnered", "pioneered", "planned", "programmed",
        "published", "re-engineered", "reduced", "refactored", "resolved", "restructured",
        "revamped", "saved", "scaled", "secured", "simplified", "spearheaded",
        "standardized", "streamlined", "strengthened", "structured", "supervised",
        "surpassed", "trained", "transformed", "unified", "upgraded", "validated"
    ]

    WEAK_PHRASES = [
        r"\bresponsible for\b",
        r"\bworked on\b",
        r"\bduties included\b",
        r"\bhelped with\b",
        r"\bparticipated in\b",
        r"\bassisted with\b",
        r"\btasked with\b",
        r"\bhandled\b",
        r"\binvolved in\b"
    ]

    METRIC_PATTERNS = [
        r"\b\d+%\b",                                        # 45%, 100%
        r"\$\s*\d+(?:[,\.]\d+)?\s*(?:k|m|b|million|billion|thousand)?\b",  # $50k, $1.2M
        r"\b\d+\s*(?:x|times|fold)\b",                     # 3x, 10x, 2-fold
        r"\b\d+(?:,\d{3})+\b",                             # 10,000, 500,000
        r"\b(?:\d+\+?|\d+\.\d+)\s*(?:ms|sec|seconds|minutes|hours|days|weeks|months|years)\b",  # 200ms, 2 years
        r"\b(?:\d+\+?|\d+\.\d+)\s*(?:users|customers|clients|requests|qps|endpoints|engineers|developers|members|students)\b"  # 10k users, 5 engineers
    ]

    @classmethod
    def analyze(cls, parsed_resume: Dict[str, Any], extracted_skills: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs full deterministic ATS and Resume scoring breakdown.
        """
        raw_text = parsed_resume.get("raw_text", "")
        contact_info = parsed_resume.get("contact_info", {})
        sections = parsed_resume.get("sections", {})
        word_count = parsed_resume.get("word_count", 0)
        skills_list = extracted_skills.get("all_skills", [])
        categorized_skills = extracted_skills.get("categorized_skills", {})

        checks: List[Dict[str, Any]] = []
        recommendations: List[str] = []

        # ---------------------------------------------------------------------
        # 1. Contact Info Scoring (Weight: 15%)
        # ---------------------------------------------------------------------
        contact_score = 0
        if contact_info.get("email"):
            contact_score += 30
            checks.append({"name": "Professional Email", "status": "pass", "message": f"Found email: {contact_info['email']}"})
        else:
            checks.append({"name": "Professional Email", "status": "fail", "message": "No valid email address detected."})
            recommendations.append("Add a clear email address at the top of your resume.")

        if contact_info.get("phone"):
            contact_score += 25
            checks.append({"name": "Phone Number", "status": "pass", "message": f"Found phone: {contact_info['phone']}"})
        else:
            checks.append({"name": "Phone Number", "status": "warning", "message": "Phone number was not clearly recognized."})
            recommendations.append("Include a standardized phone number with country code.")

        if contact_info.get("linkedin"):
            contact_score += 25
            checks.append({"name": "LinkedIn Profile", "status": "pass", "message": "LinkedIn profile link found."})
        else:
            checks.append({"name": "LinkedIn Profile", "status": "warning", "message": "LinkedIn URL is missing."})
            recommendations.append("Add your LinkedIn profile URL (e.g., linkedin.com/in/yourname).")

        if contact_info.get("github") or contact_info.get("portfolio"):
            contact_score += 20
            checks.append({"name": "GitHub / Portfolio", "status": "pass", "message": "GitHub or portfolio link detected."})
        else:
            checks.append({"name": "GitHub / Portfolio", "status": "warning", "message": "No GitHub or portfolio URL detected."})
            recommendations.append("Include links to your GitHub profile or personal portfolio website.")

        contact_score = min(100, contact_score)

        # ---------------------------------------------------------------------
        # 2. Section Structure Scoring (Weight: 20%)
        # ---------------------------------------------------------------------
        sec_score = 0
        detected_secs = [k for k, v in sections.items() if v.get("detected")]
        
        # Key essential sections
        essential_sections = ["experience", "education", "skills", "projects"]
        for sec in essential_sections:
            if sections.get(sec, {}).get("detected"):
                sec_score += 20
                checks.append({"name": f"{sec.capitalize()} Section", "status": "pass", "message": f"Standard '{sec.capitalize()}' section found."})
            else:
                checks.append({"name": f"{sec.capitalize()} Section", "status": "fail", "message": f"Missing standard '{sec.capitalize()}' section header."})
                recommendations.append(f"Add a distinct section header for '{sec.capitalize()}'.")

        # Bonus sections (summary, certifications, achievements)
        bonus_sections = ["summary", "certifications", "achievements"]
        bonus_detected = [s for s in bonus_sections if sections.get(s, {}).get("detected")]
        sec_score += min(20, len(bonus_detected) * 10)
        
        if not sections.get("summary", {}).get("detected"):
            checks.append({"name": "Professional Summary", "status": "warning", "message": "Professional summary or career objective not detected."})
            recommendations.append("Add a 2-3 sentence Professional Summary highlighting your top expertise and career goals.")

        sec_score = min(100, sec_score)

        # ---------------------------------------------------------------------
        # 3. Skills Depth & Diversity Scoring (Weight: 20%)
        # ---------------------------------------------------------------------
        skill_count = len(skills_list)
        cat_count = len(categorized_skills)

        if skill_count >= 12 and cat_count >= 3:
            skills_score = 95
            checks.append({"name": "Technical Skills Depth", "status": "pass", "message": f"Strong skill variety: {skill_count} skills across {cat_count} categories."})
        elif skill_count >= 7 and cat_count >= 2:
            skills_score = 80
            checks.append({"name": "Technical Skills Depth", "status": "pass", "message": f"Good skill foundation: {skill_count} skills across {cat_count} categories."})
        elif skill_count >= 3:
            skills_score = 60
            checks.append({"name": "Technical Skills Depth", "status": "warning", "message": f"Moderate skills detected ({skill_count}). Consider expanding your skill inventory."})
            recommendations.append("Enrich your technical skills section with tools, databases, and frameworks you have used.")
        else:
            skills_score = 40
            checks.append({"name": "Technical Skills Depth", "status": "fail", "message": f"Low skill count detected ({skill_count}). ATS systems look for clear keyword matches."})
            recommendations.append("Explicitly list programming languages, frameworks, databases, and tools in a dedicated Skills section.")

        # ---------------------------------------------------------------------
        # 4. Action Verbs & Weak Phrasing (Weight: 15%)
        # ---------------------------------------------------------------------
        lower_text = raw_text.lower()
        found_action_verbs = []
        for verb in cls.ACTION_VERBS:
            if re.search(r"\b" + verb + r"\b", lower_text):
                found_action_verbs.append(verb)

        found_weak_phrases = []
        for wp in cls.WEAK_PHRASES:
            if re.search(wp, lower_text):
                matched = wp.replace(r"\b", "")
                found_weak_phrases.append(matched)

        action_score = 50
        action_score += min(40, len(found_action_verbs) * 5)
        action_score -= min(30, len(found_weak_phrases) * 10)
        action_score = max(20, min(100, action_score))

        if len(found_action_verbs) >= 6:
            checks.append({"name": "Impact Action Verbs", "status": "pass", "message": f"Used strong action verbs ({', '.join(found_action_verbs[:5])}...)."})
        else:
            checks.append({"name": "Impact Action Verbs", "status": "warning", "message": f"Only {len(found_action_verbs)} action verbs detected. Begin bullet points with strong verbs like 'Architected', 'Spearheaded', 'Optimized'."})
            recommendations.append("Start every bullet point in your experience and projects with power action verbs.")

        if found_weak_phrases:
            checks.append({"name": "Weak / Passive Phrases", "status": "warning", "message": f"Found passive phrases ({', '.join(found_weak_phrases)}). Replace with direct impact statements."})
            recommendations.append(f"Replace passive phrasing ('{found_weak_phrases[0]}') with direct active verbs.")
        else:
            checks.append({"name": "Weak / Passive Phrases", "status": "pass", "message": "No generic passive phrasing like 'responsible for' detected."})

        # ---------------------------------------------------------------------
        # 5. Quantifiable Achievements & Impact (Weight: 15%)
        # ---------------------------------------------------------------------
        metric_matches = []
        for pat in cls.METRIC_PATTERNS:
            found = re.findall(pat, raw_text, re.IGNORECASE)
            metric_matches.extend(found)

        unique_metrics = list(set(metric_matches))
        metrics_count = len(unique_metrics)

        if metrics_count >= 5:
            impact_score = 95
            checks.append({"name": "Quantifiable Metrics", "status": "pass", "message": f"Outstanding quantifiable impact ({metrics_count} metrics/numbers found)."})
        elif metrics_count >= 2:
            impact_score = 75
            checks.append({"name": "Quantifiable Metrics", "status": "pass", "message": f"Found {metrics_count} measurable achievements."})
        elif metrics_count == 1:
            impact_score = 55
            checks.append({"name": "Quantifiable Metrics", "status": "warning", "message": "Found only 1 measurable metric. Recruiters look for metrics (% increase, $ saved, latency reduction, user scale)."})
            recommendations.append("Quantify your achievements: include numbers, percentages, efficiency improvements, or scale.")
        else:
            impact_score = 35
            checks.append({"name": "Quantifiable Metrics", "status": "fail", "message": "No measurable metrics (percentages, numbers, scale) detected in bullet points."})
            recommendations.append("Add measurable outcomes to your bullet points (e.g. 'Improved API response time by 35%', 'Scaled service to 50k users').")

        # ---------------------------------------------------------------------
        # 6. Formatting & Readability (Weight: 15%)
        # ---------------------------------------------------------------------
        format_score = 90
        
        # Length check
        if 350 <= word_count <= 900:
            checks.append({"name": "Resume Length", "status": "pass", "message": f"Ideal length ({word_count} words, approx 1-2 pages)."})
        elif 250 <= word_count < 350:
            format_score -= 15
            checks.append({"name": "Resume Length", "status": "warning", "message": f"Slightly brief ({word_count} words). Add more details on project architecture and responsibilities."})
            recommendations.append("Expand on your project architectures, tech choices, and personal contributions.")
        elif word_count > 1200:
            format_score -= 20
            checks.append({"name": "Resume Length", "status": "warning", "message": f"Long resume ({word_count} words). Aim for a crisp 1-2 page layout."})
            recommendations.append("Condense older or less relevant details to keep your resume concise.")
        else:
            format_score -= 30
            checks.append({"name": "Resume Length", "status": "fail", "message": f"Very short resume content ({word_count} words)."})

        # Special character / Glyph clutter check
        non_ascii_symbols = re.findall(r"[^\x00-\x7F\u2022\u2013\u2014\u2018\u2019\u201C\u201D]", raw_text)
        if len(non_ascii_symbols) > 40:
            format_score -= 15
            checks.append({"name": "Special Symbols & Glyphs", "status": "warning", "message": "High number of custom graphic symbols/emojis. ATS parsers can misread them."})
            recommendations.append("Stick to standard bullet points (•, -) and avoid decorative non-standard icons.")
        else:
            checks.append({"name": "Special Symbols & Glyphs", "status": "pass", "message": "Clean ATS-friendly bullet and text characters."})

        format_score = max(30, min(100, format_score))

        # ---------------------------------------------------------------------
        # Keyword Coverage / Density (Weight: 15%)
        # ---------------------------------------------------------------------
        # Check keyword density & stuffing
        words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", raw_text)]
        word_freq: Dict[str, int] = {}
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1
        
        stuffing_detected = False
        stuffed_word = ""
        for w, freq in word_freq.items():
            if len(w) > 4 and freq > max(8, word_count * 0.05):
                stuffing_detected = True
                stuffed_word = w
                break

        keywords_score = 80
        if stuffing_detected:
            keywords_score -= 25
            checks.append({"name": "Keyword Stuffing Check", "status": "warning", "message": f"Word '{stuffed_word}' is repeated unusually often ({word_freq[stuffed_word]} times). Avoid artificial keyword stuffing."})
            recommendations.append(f"Vary your vocabulary instead of repeating '{stuffed_word}' excessively.")
        else:
            checks.append({"name": "Keyword Stuffing Check", "status": "pass", "message": "Balanced keyword distribution without unnatural repetition."})

        if skill_count >= 8:
            keywords_score += 15
        keywords_score = min(100, keywords_score)

        # ---------------------------------------------------------------------
        # Overall Weighted Score Calculation
        # ---------------------------------------------------------------------
        # Weights:
        # ATS Compatibility: 25% (Contact: 10% + Structure: 15%)
        # Skills: 20%
        # Experience & Impact: 20% (Metrics: 10% + Verbs: 10%)
        # Projects: 15% (if projects detected and detailed)
        # Formatting: 10%
        # Keywords: 10%

        ats_compat_score = round((contact_score * 0.4) + (sec_score * 0.6))
        exp_impact_score = round((impact_score * 0.5) + (action_score * 0.5))
        
        projects_detected = sections.get("projects", {}).get("detected", False)
        projects_score = 85 if (projects_detected and skill_count >= 5) else (65 if projects_detected else 40)

        overall_score = round(
            (ats_compat_score * 0.25) +
            (skills_score * 0.20) +
            (exp_impact_score * 0.20) +
            (projects_score * 0.15) +
            (keywords_score * 0.10) +
            (format_score * 0.10)
        )

        overall_score = max(10, min(99, overall_score))

        # Overall Status Badge
        if overall_score >= 85:
            verdict = "Excellent - Highly ATS Optimized & Ready to Apply"
            badge_color = "green"
        elif overall_score >= 70:
            verdict = "Good - Competitive Resume with Minor Polish Needed"
            badge_color = "emerald"
        elif overall_score >= 55:
            verdict = "Fair - Needs Keyword & Impact Improvements"
            badge_color = "yellow"
        else:
            verdict = "Needs Work - Major Sections & Quantifiable Results Missing"
            badge_color = "red"

        return {
            "overall_score": overall_score,
            "verdict": verdict,
            "badge_color": badge_color,
            "breakdown": {
                "ats_compatibility": ats_compat_score,
                "skills_score": skills_score,
                "experience_impact": exp_impact_score,
                "projects_score": projects_score,
                "keywords_score": keywords_score,
                "formatting_score": format_score
            },
            "stats": {
                "word_count": word_count,
                "total_skills_detected": skill_count,
                "action_verbs_count": len(found_action_verbs),
                "metrics_detected_count": metrics_count,
                "detected_sections_count": len(detected_secs),
                "action_verbs_list": found_action_verbs[:10],
                "quantifiable_examples": unique_metrics[:8]
            },
            "checks": checks,
            "recommendations": recommendations[:6]
        }
