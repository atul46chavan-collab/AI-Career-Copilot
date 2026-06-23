from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.schemas.student import (
    StudentRequest,
    StudentResponse
)

from src.services.student_service import (
    StudentService
)

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)

student_service = StudentService()


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_student(
    student: StudentRequest,
    db: Session = Depends(get_db)
):

    return student_service.create_student(
        db,
        student
    )