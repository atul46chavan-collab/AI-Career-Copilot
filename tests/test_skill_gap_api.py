from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from src.main import app
from src.database.session import SessionLocal
from src.models.student import Student
from src.models.resume import Resume
from src.models.analysis import ResumeAnalysis
from src.models.job_description import JobDescription
from src.schemas.skill_gap import SkillGapAgentResponse

client = TestClient(app)


def test_analyze_skill_gap_endpoint():
    """
    Integration test validating that POST /skill-gaps/analyze:
    1. Rejects request with 404 if either resume analysis or job description does not exist.
    2. Performs case-insensitive set comparisons and computes matching/missing skills.
    3. Calculates correct gap score based on matching required skills.
    4. Integrates Gemini mocks to verify return values and formats.
    5. Verifies student deletion clean-up logic.
    """
    db = SessionLocal()
    test_email = "skillgap_candidate@example.com"
    try:
        # Clean up database state
        existing = db.query(Student).filter(Student.email == test_email).first()
        if existing:
            db.delete(existing)
            db.commit()

        # 1. Test 404: IDs do not exist
        payload_missing = {
            "resume_analysis_id": 99999,
            "job_description_id": 88888
        }
        res_err = client.post("/skill-gaps/analyze", json=payload_missing)
        assert res_err.status_code == 404
        assert "Resume analysis with ID" in res_err.json()["detail"]

        # 2. Setup correct state: Create valid student
        student = Student(
            name="Skill Gap Candidate",
            email=test_email,
            course="AI Engineering"
        )
        db.add(student)
        db.commit()
        db.refresh(student)

        # Create Resume
        resume = Resume(
            student_id=student.id,
            filename="my_resume.txt",
            file_path="db://resume",
            raw_text="Developer with Python, FastAPI, and PostgreSQL experience."
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        # Create Resume Analysis
        analysis = ResumeAnalysis(
            resume_id=resume.id,
            jd_id=None,
            strengths=["Strong backend core"],
            weaknesses=["Lacks Cloud"],
            suggestions=["Learn Docker"],
            skills_extracted={
                "found": ["Python", "FastAPI", "PostgreSQL"],
                "missing": ["Docker", "Kubernetes"]
            },
            score=85
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        # 3. Test 404: Resume analysis exists but JD does not
        payload_half_missing = {
            "resume_analysis_id": analysis.id,
            "job_description_id": 88888
        }
        res_half_err = client.post("/skill-gaps/analyze", json=payload_half_missing)
        assert res_half_err.status_code == 404
        assert "Job description with ID" in res_half_err.json()["detail"]

        # Create Job Description
        jd = JobDescription(
            student_id=student.id,
            title="Backend Dev",
            company="Innovate Corp",
            jd_text="Requirements: python, docker. Nice to have: postgresql, aws.",
            extracted_data={
                "required_skills": ["python", "docker"],
                "preferred_skills": ["postgresql", "aws"],
                "experience_required": "2+ years",
                "education_requirements": ["BS in Computer Science"],
                "responsibilities": ["Build APIs"]
            }
        )
        db.add(jd)
        db.commit()
        db.refresh(jd)

        # 4. Successful Flow with Mocked Agent
        payload = {
            "resume_analysis_id": analysis.id,
            "job_description_id": jd.id
        }

        mock_agent_response = SkillGapAgentResponse(
            learning_priority=[
                "Docker: This is a required skill. Candidate must learn containers.",
                "AWS: Preferred skill. Good to have cloud exposure."
            ],
            career_recommendations=[
                "Build a dockerized project with FastAPI and PostgreSQL.",
                "Deploy the app to AWS."
            ]
        )

        with patch("src.services.gemini_service.GeminiService.generate_structured_content", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_agent_response
            response = client.post("/skill-gaps/analyze", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Schema expectations
        assert "matching_skills" in data
        assert "missing_required_skills" in data
        assert "missing_preferred_skills" in data
        assert "gap_score" in data
        assert "learning_priority" in data
        assert "career_recommendations" in data

        # Python Set matching assertions (case-insensitive)
        # matching required: "python" (from JD)
        # matching preferred: "postgresql" (from JD)
        # Total matching sorted: ["postgresql", "python"]
        assert data["matching_skills"] == ["postgresql", "python"]

        # missing required: "docker"
        assert data["missing_required_skills"] == ["docker"]

        # missing preferred: "aws"
        assert data["missing_preferred_skills"] == ["aws"]

        # gap score calculation:
        # required_skills = ["python", "docker"] (total 2)
        # matching required = ["python"] (total 1)
        # Score = (1 / 2) * 100 = 50%
        assert data["gap_score"] == 50

        # Verify Mock data propagates
        assert len(data["learning_priority"]) == 2
        assert "Candidate must learn containers." in data["learning_priority"][0]
        assert len(data["career_recommendations"]) == 2

        # 5. Clean up student (verify cascade deletions work)
        db.delete(student)
        db.commit()

        # Confirm cascades removed downstream details
        assert db.query(Resume).filter(Resume.id == resume.id).first() is None
        assert db.query(ResumeAnalysis).filter(ResumeAnalysis.id == analysis.id).first() is None
        assert db.query(JobDescription).filter(JobDescription.id == jd.id).first() is None

    finally:
        db.close()
