from fastapi.testclient import TestClient
from src.main import app
from src.database.session import SessionLocal
from src.models.student import Student
from src.models.job_description import JobDescription

client = TestClient(app)


def test_analyze_jd_endpoint():
    """
    Integration test validating that POST /job-descriptions/analyze:
    1. Rejects request if student does not exist.
    2. Accepts request with valid student_id, runs Gemini evaluation.
    3. Persists records in job_descriptions table including JSON extracted_data.
    4. Cascades deletions on student cleanup.
    """
    db = SessionLocal()
    test_email = "jd_candidate@example.com"
    try:
        # Clean up database state
        existing = db.query(Student).filter(Student.email == test_email).first()
        if existing:
            db.delete(existing)
            db.commit()

        # 1. Test student validation failure (passing non-existent ID)
        bad_payload = {
            "student_id": 99999,
            "job_description": "We are looking for a Python Software Engineer."
        }
        err_response = client.post("/job-descriptions/analyze", json=bad_payload)
        assert err_response.status_code == 404
        assert "does not exist" in err_response.json()["detail"]

        # 2. Setup correct state: Create valid student
        student = Student(
            name="JD Candidate",
            email=test_email,
            course="AI Engineering"
        )
        db.add(student)
        db.commit()
        db.refresh(student)

        # 3. Test successful flow
        jd_text = (
            "We are seeking an experienced AI Software Engineer to join our team at Innovate Corp.\n"
            "Requirements:\n"
            "- 3+ years experience with Python and TensorFlow.\n"
            "- Strong understanding of REST APIs and Docker.\n"
            "- Nice to have: Experience with PostgreSQL and AWS.\n"
            "- Education: Bachelor's degree in Computer Science.\n"
            "Responsibilities: Designing, training, and deploying neural networks."
        )
        payload = {
            "student_id": student.id,
            "job_description": jd_text
        }

        # Mock the external Gemini API call to prevent rate limit (429) exhaustion
        from unittest.mock import patch, AsyncMock
        from src.schemas.job_description import JobDescriptionAgentResponse

        mock_agent_response = JobDescriptionAgentResponse(
            job_title="AI Software Engineer",
            company_name="Innovate Corp",
            required_skills=["python", "tensorflow", "apis", "docker"],
            preferred_skills=["postgresql", "aws"],
            experience_required="3+ years",
            education_requirements=["bachelor's degree in computer science"],
            responsibilities=["designing, training, and deploying neural networks"]
        )

        with patch("src.services.gemini_service.GeminiService.generate_structured_content", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_agent_response
            response = client.post("/job-descriptions/analyze", json=payload)

        assert response.status_code == 200

        data = response.json()
        assert "jd_id" in data
        assert "job_title" in data
        assert "company_name" in data
        assert "required_skills" in data
        assert "preferred_skills" in data
        assert "experience_required" in data
        assert "education_requirements" in data
        assert "responsibilities" in data

        assert isinstance(data["required_skills"], list)
        assert len(data["required_skills"]) > 0

        # 4. Verify database records are persisted
        jd_id = data["jd_id"]
        db_jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        assert db_jd is not None
        assert db_jd.student_id == student.id
        assert db_jd.title == data["job_title"]
        assert db_jd.company == data["company_name"]
        assert db_jd.jd_text == jd_text
        
        # Verify JSON extraction structure
        assert isinstance(db_jd.extracted_data, dict)
        assert "required_skills" in db_jd.extracted_data
        assert "preferred_skills" in db_jd.extracted_data

        # 5. Clean up student (verify cascade deletion of JD)
        db.delete(student)
        db.commit()

        # Confirm cascades removed the JD record
        assert db.query(JobDescription).filter(JobDescription.id == jd_id).first() is None

    finally:
        db.close()
