import os
import re
import json
import traceback
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from services.resume_parser import ResumeParser
from services.skill_extractor import SkillExtractor
from services.ats_analyzer import ATSAnalyzer
from services.job_matcher import JobMatcher
from services.job_service import JobService
from services.ai_assistant import AIAssistant

app = FastAPI(
    title="GrowPath AI",
    description="AI Resume Analysis, Job Matching & Career Assistant API",
    version="2.0.0"
)

# Enable CORS for flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Serve static frontend files
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")


# =====================================================================
# HTML Navigation Routes
# =====================================================================
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse("<h1>GrowPath AI Frontend Loading...</h1>", status_code=200)

@app.get("/ats", response_class=HTMLResponse)
async def serve_ats():
    ats_file = os.path.join(FRONTEND_DIR, "ats.html")
    if os.path.exists(ats_file):
        with open(ats_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse("<h1>ATS Checker Page</h1>", status_code=200)

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    dash_file = os.path.join(FRONTEND_DIR, "dashboard.html")
    if os.path.exists(dash_file):
        with open(dash_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse("<h1>Dashboard Page</h1>", status_code=200)


# =====================================================================
# 1. RESUME UPLOAD & COMPREHENSIVE PARSE (PDF & DOCX)
# =====================================================================
@app.post("/api/upload_and_parse")
async def upload_and_parse_resume(file: UploadFile = File(...)):
    """
    Validates file (PDF/DOCX), extracts text, contact info, sections,
    categorized skills, deterministic ATS scores, and suggested roles.
    """
    try:
        content = await file.read()
        filename = file.filename or "uploaded_resume.pdf"

        # 1. Parse file structure & text
        parsed_data = ResumeParser.parse_file(content, filename)

        # 2. Extract categorized skills
        extracted_skills = SkillExtractor.extract_skills(parsed_data["raw_text"])

        # 3. Deterministic ATS Analysis
        ats_result = ATSAnalyzer.analyze(parsed_data, extracted_skills)

        # 4. Generate role suggestions
        suggested_roles = AIAssistant.suggest_job_roles(
            parsed_data["raw_text"],
            extracted_skills["all_skills"]
        )

        # 5. Fetch Initial Live Jobs via JSearch
        role_titles = [r["title"] if isinstance(r, dict) else str(r) for r in suggested_roles[:2]]
        live_jobs = JobService.fetch_live_jobs(
            roles=role_titles or ["Software Engineer"],
            skills=extracted_skills["all_skills"],
            country_code="IN",
            limit_per_role=3
        )

        return JSONResponse({
            "success": True,
            "parsed_resume": parsed_data,
            "extracted_skills": extracted_skills,
            "ats_analysis": ats_result,
            "suggested_roles": suggested_roles,
            "live_jobs": live_jobs
        })

    except ValueError as ve:
        return JSONResponse({"success": False, "error": str(ve)}, status_code=400)
    except Exception as e:
        print(f"[GrowPath API] Error parsing resume: {str(e)}")
        traceback.print_exc()
        return JSONResponse({"success": False, "error": f"Failed to process resume: {str(e)}"}, status_code=500)


# =====================================================================
# 2. JOB DESCRIPTION MATCHING & SKILL GAP ANALYSIS
# =====================================================================
@app.post("/api/match_job")
async def match_job_description(payload: Dict[str, Any] = Body(...)):
    """
    Compares resume text & skills against a target Job Description.
    """
    try:
        resume_text = payload.get("resume_text", "").strip()
        job_description = payload.get("job_description", "").strip()
        skills = payload.get("skills", [])

        if not resume_text:
            return JSONResponse({"success": False, "error": "Resume text is required."}, status_code=400)
        if not job_description:
            return JSONResponse({"success": False, "error": "Job description is required."}, status_code=400)

        # If skills list wasn't provided, extract on the fly
        if not skills:
            skills = SkillExtractor.extract_skills(resume_text).get("all_skills", [])

        match_result = JobMatcher.match(resume_text, skills, job_description)

        return JSONResponse({
            "success": True,
            "match_result": match_result
        })

    except ValueError as ve:
        return JSONResponse({"success": False, "error": str(ve)}, status_code=400)
    except Exception as e:
        print(f"[GrowPath API] Error matching JD: {str(e)}")
        traceback.print_exc()
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/upload_jd")
async def upload_job_description(file: UploadFile = File(...)):
    """
    Uploads and extracts plain text from a Job Description file (PDF, DOCX, TXT).
    """
    try:
        content = await file.read()
        filename = file.filename or "job_description.pdf"

        # Validate file size (10 MB)
        if len(content) > 10 * 1024 * 1024:
            return JSONResponse({
                "success": False,
                "error": "Job Description file is too large. Please upload a file smaller than 10 MB."
            }, status_code=400)

        ext = os.path.splitext(filename)[1].lower()
        if ext not in [".pdf", ".docx", ".doc", ".txt"]:
            return JSONResponse({
                "success": False,
                "error": f"Unsupported file format '{ext}'. Please upload a PDF, DOCX, or TXT file."
            }, status_code=400)

        extracted_text = ResumeParser.extract_text(content, filename)

        return JSONResponse({
            "success": True,
            "filename": filename,
            "file_type": ext.lstrip(".").upper(),
            "text": extracted_text,
            "word_count": len(extracted_text.split()),
            "char_count": len(extracted_text)
        })

    except ValueError as ve:
        return JSONResponse({"success": False, "error": str(ve)}, status_code=400)
    except Exception as e:
        print(f"[GrowPath API] Error uploading JD: {str(e)}")
        traceback.print_exc()
        return JSONResponse({"success": False, "error": f"Failed to extract text from document: {str(e)}"}, status_code=500)


# =====================================================================
# 3. LIVE JOB RECOMMENDATIONS (JSEARCH VIA RAPIDAPI)
# =====================================================================
@app.post("/api/recommend_jobs")
async def recommend_jobs_api(payload: Dict[str, Any] = Body(...)):
    """
    Queries live jobs based on roles, skills, and target country via JSearch API.
    """
    try:
        roles = payload.get("roles", ["Software Engineer"])
        skills = payload.get("skills", [])
        country_code = payload.get("country_code", "IN")
        limit = int(payload.get("limit", 4))

        if isinstance(roles, str):
            roles = [roles]

        jobs = JobService.fetch_live_jobs(
            roles=roles,
            skills=skills,
            country_code=country_code,
            limit_per_role=limit
        )

        return JSONResponse({
            "success": True,
            "count": len(jobs),
            "jobs": jobs
        })
    except Exception as e:
        print(f"[GrowPath API] Error in recommend_jobs_api: {type(e).__name__} - {str(e)}")
        return JSONResponse({
            "success": False,
            "error": "Job search service is temporarily unavailable."
        }, status_code=500)



# =====================================================================
# 4. AI RESUME BULLET OPTIMIZER (STAR METHOD)
# =====================================================================
@app.post("/api/improve_bullet")
async def improve_bullet_api(payload: Dict[str, Any] = Body(...)):
    """
    Rewrites a weak resume bullet point into high-impact STAR metrics.
    """
    try:
        bullet_text = payload.get("bullet_text", "").strip()
        target_role = payload.get("target_role", "Software Engineer").strip()

        if not bullet_text:
            return JSONResponse({"success": False, "error": "Bullet point text is required."}, status_code=400)

        result = AIAssistant.improve_bullet_point(bullet_text, target_role)
        return JSONResponse({"success": True, "improvement": result})

    except ValueError as ve:
        return JSONResponse({"success": False, "error": str(ve)}, status_code=400)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


# =====================================================================
# 5. AI INTERVIEW PREPARATION GENERATOR
# =====================================================================
@app.post("/api/interview_prep")
async def interview_prep_api(payload: Dict[str, Any] = Body(...)):
    """
    Generates customized Technical, Behavioral (STAR), and Project Deep-Dive questions & answers.
    """
    try:
        resume_text = payload.get("resume_text", "").strip()
        target_role = payload.get("target_role", "Software Engineer").strip()
        skills = payload.get("skills", [])

        if not resume_text:
            return JSONResponse({"success": False, "error": "Resume text is required for interview prep."}, status_code=400)

        prep_data = AIAssistant.generate_interview_prep(resume_text, target_role, skills)
        return JSONResponse({"success": True, "prep": prep_data})

    except ValueError as ve:
        return JSONResponse({"success": False, "error": str(ve)}, status_code=400)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


# =====================================================================
# 6. AI 4-WEEK SKILL LEARNING ROADMAP
# =====================================================================
@app.post("/api/learning_roadmap")
async def learning_roadmap_api(payload: Dict[str, Any] = Body(...)):
    """
    Generates a 4-week structured skill development roadmap for missing skills.
    """
    try:
        missing_skills = payload.get("missing_skills", [])
        target_role = payload.get("target_role", "Software Engineer").strip()
        job_description = payload.get("job_description", "")

        if not missing_skills:
            return JSONResponse({"success": False, "error": "List of missing skills is required."}, status_code=400)

        roadmap = AIAssistant.generate_learning_roadmap(missing_skills, target_role, job_description)
        return JSONResponse({"success": True, "roadmap": roadmap})

    except ValueError as ve:
        return JSONResponse({"success": False, "error": str(ve)}, status_code=400)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


# =====================================================================
# 7. BACKWARD COMPATIBILITY ENDPOINTS (Preserve Existing Functionality)
# =====================================================================
@app.post("/calculate_ats_score")
async def legacy_calculate_ats_score(request: dict):
    """
    Legacy ATS score calculation endpoint for backward compatibility with existing frontends.
    """
    try:
        resume_text = request.get("resume_text", "").strip()
        job_description = request.get("job_description", "").strip()

        if not resume_text or not job_description:
            return {"error": "Both resume text and job description are required"}

        # Extract skills
        skills_data = SkillExtractor.extract_skills(resume_text)
        skills_list = skills_data.get("all_skills", [])

        # Match with Job Description
        match_result = JobMatcher.match(resume_text, skills_list, job_description)

        # Build comprehensive structure
        ats_analysis = {
            "ats_score": match_result["match_score"],
            "keyword_matches": match_result["matched_keywords"] + match_result["matched_skills"],
            "missing_keywords": match_result["missing_keywords"] + match_result["missing_skills"],
            "skills_gap": match_result["missing_skills"],
            "recommendations": match_result["tailoring_tips"],
            "summary": f"ATS Compatibility Score: {match_result['match_score']}%. {match_result['fit_level']}."
        }

        return {
            "success": True,
            "analysis": ats_analysis
        }

    except Exception as e:
        print(f"[GrowPath API] Error in legacy calculate_ats_score: {str(e)}")
        traceback.print_exc()
        return {"error": str(e)}


@app.post("/recommend_jobs")
async def legacy_recommend_jobs(file: UploadFile = File(...)):
    """
    Legacy resume upload and job recommendation endpoint for backward compatibility.
    """
    try:
        content = await file.read()
        filename = file.filename or "resume.pdf"

        # Parse file
        parsed_data = ResumeParser.parse_file(content, filename)
        text = parsed_data["raw_text"]

        # Extract skills
        skills_data = SkillExtractor.extract_skills(text)
        found_skills = skills_data["all_skills"]

        # Generate suggested roles
        suggested_roles = AIAssistant.suggest_job_roles(text, found_skills)
        role_titles = [r["title"] if isinstance(r, dict) else str(r) for r in suggested_roles[:2]]

        # Fetch live jobs
        live_jobs = JobService.fetch_live_jobs(
            roles=role_titles or ["Software Engineer"],
            skills=found_skills,
            country_code="IN",
            limit_per_role=3
        )

        return {
            "extracted_skills": found_skills,
            "model_output": {"job_roles": suggested_roles},
            "live_jobs": live_jobs,
            "resume_text": text
        }

    except Exception as e:
        print(f"[GrowPath API] Error in legacy recommend_jobs: {str(e)}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

