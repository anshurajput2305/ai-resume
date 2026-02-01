from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PyPDF2 import PdfReader
from dotenv import load_dotenv
load_dotenv()
import os
import traceback
import json
import re
import requests


app = FastAPI()

# === Configure APIs ===
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PPLX_URL = "https://api.perplexity.ai/chat/completions"

THEIRSTACK_API_KEY =os.getenv("THEIRSTACK_API_KEY")
# === Skills List ===
skills = ["Python", "Java", "C++", "JavaScript", "React", "Django", "Flask"]

# === Paths ===
BASE_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# === Serve static files ===
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# === Serve HTML at "/" ===
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    html_path = os.path.join(FRONTEND_DIR, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)


# <------------------------ TheirStack ---------------------------->
def fetch_jobs_from_theirstack(role, skills, limit=3):
    url = "https://api.theirstack.com/v1/jobs/search"
    headers = {
        "Authorization": f"Bearer {THEIRSTACK_API_KEY}",
        "Content-Type": "application/json"
    }

    clean_role = re.sub(r"[^a-zA-Z\s]", "", role).strip()

    payload = {
        "page": 0,
        "limit": limit,
        "job_title_or": [clean_role],
        "job_country_code_or": ["IN"],
        "posted_at_max_age_days": 15,
    }

    if skills:
        payload["job_technology_slug_or"] = [s.lower() for s in skills]

    try:
        print(f"🔍 Fetching jobs for role: {clean_role}")
        resp = requests.post(url, json=payload, headers=headers)
        print("📤 Sent payload:", payload)
        print("📡 Response code:", resp.status_code)

        resp.raise_for_status()
        data = resp.json()
        print("----------------------", data)

        jobs = []
        for j in data.get("data", []):
            jobs.append({
                "title": j.get("job_title"),
                "company": (
                    j.get("company", {}).get("name")
                    if isinstance(j.get("company"), dict)
                    else j.get("company")
                ),
                "link": j.get("final_url") or j.get("url"),
                "location": j.get("location"),
                "salary": j.get("salary_string")
            })

        print(f"✅ Found {len(jobs)} jobs from TheirStack")
        return jobs

    except requests.exceptions.HTTPError as e:
        print("❌ TheirStack HTTP Error:", e.response.text)
        return []
    except Exception as e:
        print("❌ TheirStack API error:")
        traceback.print_exc()
        return []


# === ATS Score calculation route ===
@app.post("/calculate_ats_score")
async def calculate_ats_score(request: dict):
    try:
        resume_text = request.get("resume_text", "").strip()
        job_description = request.get("job_description", "").strip()
        
        if not resume_text or not job_description:
            return {"error": "Both resume text and job description are required"}
        
        # Create prompt for ATS scoring
        prompt = f"""
You are an ATS (Applicant Tracking System) expert. Analyze the resume against the job description and provide a detailed ATS compatibility score.

Resume Text:
{resume_text}

Job Description:
{job_description}

Please provide:
1. Overall ATS Score (0-100)
2. Keyword Match Analysis
3. Skills Gap Analysis
4. Specific Recommendations for improvement
5. Missing Keywords that should be added

Return your analysis in JSON format with the following structure:
{{
    "ats_score": <number>,
    "keyword_matches": ["list of matched keywords"],
    "missing_keywords": ["list of missing important keywords"],
    "skills_gap": ["list of missing skills"],
    "recommendations": ["list of specific recommendations"],
    "summary": "brief summary of the analysis"
}}
"""

        # Call Perplexity API for ATS analysis
        try:
            payload = {
                "model": "sonar-pro",
                "messages": [
                    {"role": "system", "content": "You are an expert ATS analyzer. Provide detailed, actionable feedback."},
                    {"role": "user", "content": prompt}
                ]
            }

            headers = {
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }

            response = requests.post(PPLX_URL, json=payload, headers=headers)
            response.raise_for_status()

            model_output = response.json()["choices"][0]["message"]["content"]
            
            # Clean JSON response
            model_output = re.sub(r"^```json|```$", "", model_output, flags=re.IGNORECASE).strip()
            
            try:
                ats_analysis = json.loads(model_output)
            except:
                # Fallback if JSON parsing fails
                ats_analysis = {
                    "ats_score": 75,
                    "keyword_matches": ["extracted from analysis"],
                    "missing_keywords": ["needs improvement"],
                    "skills_gap": ["various skills"],
                    "recommendations": ["improve keyword density", "add missing skills"],
                    "summary": "Analysis completed but formatting needs adjustment",
                    "raw_output": model_output
                }

            return {
                "success": True,
                "analysis": ats_analysis
            }

        except Exception as e:
            print("❌ ATS Analysis API error:")
            traceback.print_exc()
            return {"error": f"ATS analysis failed: {str(e)}"}

    except Exception as e:
        print("❌ ATS Score calculation error:")
        traceback.print_exc()
        return {"error": str(e)}


# === Resume upload route ===
@app.post("/recommend_jobs")
async def recommend_jobs(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # Extract text
        text = ""
        reader = PdfReader(temp_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        os.remove(temp_path)

        if not text.strip():
            return {"error": "⚠️ No text found in PDF!"}

        print("✅ Extracted text:", text[:300])

        # Detect skills
        found_skills = [s for s in skills if s.lower() in text.lower()]
        print("✅ Found skills:", found_skills)

        # === Create prompt ===
        prompt = f"""
You are a career recommendation assistant.
Analyze this resume text and detected skills: {found_skills}.
Suggest 12–15 job roles that match the candidate.
Return JSON only.
Resume text: {text}
"""

        # === CALL PERPLEXITY (SONAR PRO) ===
        try:
            payload = {
                "model": "sonar-pro",
                "messages": [
                    {"role": "system", "content": "You are a career recommendation engine."},
                    {"role": "user", "content": prompt}
                ]
            }

            headers = {
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }

            response = requests.post(PPLX_URL, json=payload, headers=headers)

            print("📦 Raw Perplexity Response:", response.text)

            response.raise_for_status()

            model_output = response.json()["choices"][0]["message"]["content"]

            # remove json fences
            model_output = re.sub(r"^```json|```$", "", model_output, flags=re.IGNORECASE).strip()

            try:
                parsed_output = json.loads(model_output)
            except:
                parsed_output = {"raw_output": model_output}

        except Exception as e:
            print("❌ Perplexity API error:")
            traceback.print_exc()
            return {"error": f"Perplexity failed: {str(e)}"}

        # --- Extract job roles ---
        job_roles = []
        if isinstance(parsed_output, dict):
            job_roles = (
                parsed_output.get("job_roles")
                or parsed_output.get("suggested_roles")
                or parsed_output.get("recommended_roles")
                or []
            )
        elif isinstance(parsed_output, list):
            job_roles = parsed_output

        # --- Fetch TheirStack jobs ---
        live_jobs = []
        if job_roles:
            for role in job_roles[:2]:
                role_name = role["title"] if isinstance(role, dict) else role
                jobs = fetch_jobs_from_theirstack(role_name, found_skills)
                live_jobs.extend(jobs)

        return {
            "extracted_skills": found_skills,
            "model_output": parsed_output,
            "live_jobs": live_jobs,
            "resume_text": text
        }

    except Exception as e:
        print("❌ Unexpected error:")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)
