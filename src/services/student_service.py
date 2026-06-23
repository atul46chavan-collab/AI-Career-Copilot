from sqlalchemy.orm import Session
from src.models.student import Student
from src.schemas.student import (
    StudentRequest,
    StudentResponse
)


class StudentService:

    def create_student(
        self,
        db: Session,
        student: StudentRequest
    ) -> StudentResponse:

        # Create model instance
        db_student = Student(
            name=student.name,
            email=student.email,
            course=student.course
        )

        # Add to database session and persist
        db.add(db_student)
        db.commit()
        db.refresh(db_student)

        # Map to response schema
        return StudentResponse(
            message="Student created successfully",
            student_id=db_student.id,
            student_name=db_student.name,
            email=db_student.email,
            course=db_student.course
        )