from fastapi.testclient import TestClient
from unittest.mock import patch
from app import app

client = TestClient(app)

def test_recommend_jobs():
    fake_jobs = [
        {
            "title": "Python Developer",
            "company": "Example Tech",
            "location": "India",
            "url": "https://example.com/job"
        }
    ]

    payload = {
        "roles": ["Python Developer"],
        "skills": ["Python", "FastAPI"],
        "country_code": "IN",
        "limit": 1
    }

    with patch(
        "app.JobService.fetch_live_jobs",
        return_value=fake_jobs
    ) as mock_fetch:

        response = client.post("/api/recommend_jobs", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["count"] == 1
    assert len(data["jobs"]) == 1
    assert data["jobs"][0]["title"] == "Python Developer"

    mock_fetch.assert_called_once_with(
        roles=["Python Developer"],
        skills=["Python", "FastAPI"],
        country_code="IN",
        limit_per_role=1
    )

def test_home_page():
    response = client.get("/")
    assert response.status_code == 200


def test_ats_page():
    response = client.get("/ats")
    assert response.status_code == 200


def test_dashboard_page():
    response = client.get("/dashboard")
    assert response.status_code == 200


def test_match_job():
    payload = {
        "resume_text": """
        Python developer with experience in FastAPI,
        JavaScript, HTML, CSS, MongoDB and Git.
        """,
        "job_description": """
        Looking for a Python developer with experience
        in FastAPI, REST APIs, JavaScript and Git.
        """
    }

    response = client.post("/api/match_job", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data is not None

def test_upload_jd_invalid_file_type():
    response = client.post(
        "/api/upload_jd",
        files={
            "file": (
                "test.txt",
                b"This is a test job description.",
                "text/plain"
            )
        }
    )

    # We are checking that the endpoint handles the request
    # instead of crashing.
    assert response.status_code in [200, 400, 422]