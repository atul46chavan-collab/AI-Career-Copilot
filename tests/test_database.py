import pytest
from sqlalchemy.orm import Session
from src.database.session import SessionLocal
from src.models.student import Student
from src.models.resume import Resume
from src.models.job_description import JobDescription
from src.models.analysis import ResumeAnalysis


def test_database_crud_relations():
    """
    Verifies creation, relationship linking, JSON serialization, and cascade deletion
    across Student, Resume, JobDescription, and ResumeAnalysis models.
    """
    db = SessionLocal()
    try:
        # Clean up any existing test student to avoid duplicate email key violation
        test_email = "test_candidate@example.com"
        existing = db.query(Student).filter(Student.email == test_email).first()
        if existing:
            db.delete(existing)
            db.commit()

        # 1. Create Student
        student = Student(
            name="Test Candidate",
            email=test_email,
            course="AI Engineering"
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        
        assert student.id is not None
        assert student.name == "Test Candidate"

        # 2. Create Resume
        resume = Resume(
            student_id=student.id,
            filename="my_resume.pdf",
            file_path="/path/to/my_resume.pdf",
            raw_text="Extensive experience in Deep Learning and PyTorch."
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        assert resume.id is not None
        assert resume.student_id == student.id

        # 3. Create Job Description
        jd = JobDescription(
            student_id=student.id,
            title="Senior GenAI Engineer",
            company="DeepMind",
            jd_text="Looking for a specialist in LangGraph and Gemini API."
        )
        db.add(jd)
        db.commit()
        db.refresh(jd)
        
        assert jd.id is not None
        assert jd.student_id == student.id

        # 4. Create Resume Analysis (testing JSON serialization)
        analysis = ResumeAnalysis(
            resume_id=resume.id,
            jd_id=jd.id,
            strengths=["Python proficiency", "Deep learning experience"],
            weaknesses=["Lacks LangGraph experience"],
            suggestions=["Build projects using LangGraph and Gemini API"],
            skills_extracted=["Python", "Deep Learning", "PyTorch"],
            score=85
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        assert analysis.id is not None
        assert analysis.resume_id == resume.id
        assert analysis.jd_id == jd.id
        assert analysis.score == 85
        assert isinstance(analysis.strengths, list)

        # 5. Verify back-population relationships
        db.expire_all()  # Force reload from DB
        
        assert len(student.resumes) == 1
        assert student.resumes[0].id == resume.id
        assert len(student.job_descriptions) == 1
        assert student.job_descriptions[0].id == jd.id
        assert len(resume.analyses) == 1
        assert resume.analyses[0].id == analysis.id

        # 6. Verify cascade deletion
        db.delete(student)
        db.commit()

        # Confirm cascades removed all downstream data
        assert db.query(Student).filter(Student.id == student.id).first() is None
        assert db.query(Resume).filter(Resume.id == resume.id).first() is None
        assert db.query(JobDescription).filter(JobDescription.id == jd.id).first() is None
        assert db.query(ResumeAnalysis).filter(ResumeAnalysis.id == analysis.id).first() is None

    finally:
        db.close()
