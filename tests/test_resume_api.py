from fastapi.testclient import TestClient
from src.main import app
from src.database.session import SessionLocal
from src.models.student import Student
from src.models.resume import Resume
from src.models.analysis import ResumeAnalysis

client = TestClient(app)


def test_analyze_resume_endpoint():
    """
    Integration test validating that POST /resume/analyze:
    1. Rejects request if student does not exist.
    2. Accepts request with valid student_id, runs Gemini evaluation.
    3. Persists records in resumes and resume_analyses tables.
    4. Cascades deletions on student cleanup.
    """
    db = SessionLocal()
    test_email = "endpoint_candidate@example.com"
    try:
        # Clean up database state
        existing = db.query(Student).filter(Student.email == test_email).first()
        if existing:
            db.delete(existing)
            db.commit()

        # 1. Test student validation failure (passing non-existent ID)
        bad_payload = {
            "student_id": 99999,
            "resume_text": "Python engineer looking for a backend role."
        }
        err_response = client.post("/resume/analyze", json=bad_payload)
        assert err_response.status_code == 404
        assert "does not exist" in err_response.json()["detail"]

        # 2. Setup correct state: Create valid student
        student = Student(
            name="Endpoint Candidate",
            email=test_email,
            course="AI Engineering"
        )
        db.add(student)
        db.commit()
        db.refresh(student)

        # 3. Test successful flow
        resume_text = (
            "Jane Doe\n"
            "Python Backend Engineer\n"
            "Experience:\n"
            "- 2 years writing FastAPI applications.\n"
            "- Managed databases with PostgreSQL.\n"
            "Skills: Python, FastAPI, PostgreSQL"
        )
        payload = {
            "student_id": student.id,
            "resume_text": resume_text
        }

        # Mock the external Gemini API call to prevent rate limit (429) exhaustion
        from unittest.mock import patch, AsyncMock
        from src.schemas.resume import ResumeAgentResponse

        mock_agent_response = ResumeAgentResponse(
            resume_score=85,
            strengths=["Core technical proficiency in FastAPI and Python."],
            weaknesses=["Missing containerization experience (Docker)."],
            skills_found=["Python", "FastAPI", "PostgreSQL"],
            missing_skills=["Docker", "Kubernetes"],
            recommendations=["Add a Docker configuration to your Python projects."]
        )

        with patch("src.services.gemini_service.GeminiService.generate_structured_content", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_agent_response
            response = client.post("/resume/analyze", json=payload)

        if response.status_code != 200:
            print("\nAPI ERROR DETAIL:", response.json())
        assert response.status_code == 200
        
        data = response.json()
        assert "resume_id" in data
        assert "analysis_id" in data
        assert data["resume_score"] >= 0
        assert len(data["strengths"]) >= 0

        # 4. Verify database records are persisted
        resume_id = data["resume_id"]
        analysis_id = data["analysis_id"]

        db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
        assert db_resume is not None
        assert db_resume.student_id == student.id
        assert db_resume.raw_text == resume_text

        db_analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.id == analysis_id).first()
        assert db_analysis is not None
        assert db_analysis.resume_id == resume_id
        assert db_analysis.score == data["resume_score"]

        # 5. Clean up student (verify cascade deletion of resume + analysis)
        db.delete(student)
        db.commit()

        # Confirm cascades removed all downstream data
        assert db.query(Resume).filter(Resume.id == resume_id).first() is None
        assert db.query(ResumeAnalysis).filter(ResumeAnalysis.id == analysis_id).first() is None

    finally:
        db.close()

