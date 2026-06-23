from pydantic import BaseModel, EmailStr, Field


class StudentRequest(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    course: str = Field(..., max_length=100)


class StudentResponse(BaseModel):
    message: str
    student_id: int
    student_name: str
    email: EmailStr
    course: str

    model_config = {
        "from_attributes": True
    }