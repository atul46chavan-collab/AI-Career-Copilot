from fastapi.testclient import TestClient
from src.main import app
from src.database.session import SessionLocal
from src.models.student import Student

client = TestClient(app)


def test_create_student_endpoint():
    """
    Verifies that the POST /students API endpoint successfully persists a student record
    in PostgreSQL database and returns valid JSON response matching StudentResponse schema.
    """
    test_email = "api_student@example.com"
    
    # 1. Arrange: clean up database prior to running test
    db = SessionLocal()
    try:
        existing = db.query(Student).filter(Student.email == test_email).first()
        if existing:
            db.delete(existing)
            db.commit()
    finally:
        db.close()

    # 2. Act: POST payload to /students route
    payload = {
        "name": "API Student",
        "email": test_email,
        "course": "Vibe Coding 101"
    }
    response = client.post("/students", json=payload)

    # 3. Assert: Verify response payload
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Student created successfully"
    assert data["student_name"] == "API Student"
    assert data["email"] == test_email
    assert data["course"] == "Vibe Coding 101"
    assert "student_id" in data

    # 4. Clean up created database record
    db = SessionLocal()
    try:
        added = db.query(Student).filter(Student.email == test_email).first()
        if added:
            db.delete(added)
            db.commit()
    finally:
        db.close()
