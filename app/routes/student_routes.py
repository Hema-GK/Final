from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import face_recognition
import numpy as np
import base64
import json
import io
from app.database import get_db
from app.models.student import Student

# Prefix matches the frontend call (plural: /students)
router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/register")
def register_student(data: dict, db: Session = Depends(get_db)):
    # 1. Clean the USN (removing accidental spaces)
    usn_clean = str(data.get("usn", "")).strip()
    
    # 2. Duplicate Check
    existing = db.query(Student).filter(Student.usn == usn_clean).first()
    if existing:
        return {"status": "failed", "message": "USN already exists"}

    try:
        # 3. Handle Image
        image_data = data["image"].split(",")[1]
        image_bytes = base64.b64decode(image_data)
        img = face_recognition.load_image_file(io.BytesIO(image_bytes))
        
        encodings = face_recognition.face_encodings(img)
        if len(encodings) == 0:
            return {"status": "failed", "message": "Face not clear"}
        
        face_encoding_str = json.dumps(encodings[0].tolist())

        # 4. Explicitly create the student object
        new_student = Student(
            name=data.get("name"),
            usn=usn_clean,
            section=data.get("section"),
            semester=data.get("semester"),
            password=str(data.get("password", "")).strip(),
            face_encoding=face_encoding_str
        )

        # 5. Force the save
        db.add(new_student)
        db.commit() # This must happen for it to show in pgAdmin
        db.refresh(new_student) 
        
        return {"status": "success", "message": "Registered successfully"}

    except Exception as e:
        db.rollback()
        print(f"DB ERROR: {e}")
        return {"status": "failed", "message": str(e)}
@router.post("/login")
def login_student(data: dict, db: Session = Depends(get_db)):
    # Clean input data
    input_usn = str(data.get("usn", "")).strip()
    input_pwd = str(data.get("password", "")).strip()

    # Case-insensitive USN check is safer for mobile keyboards
    student = db.query(Student).filter(Student.usn == input_usn).first()

    if not student:
        return {"status": "failed", "message": "Invalid Credentials"}

    # Clean database data for comparison
    db_pwd = str(student.password).strip()

    if db_pwd != input_pwd:
        return {"status": "failed", "message": "Invalid Credentials"}

    # --- MATCHING FRONTEND EXPECTATIONS ---
    return {
        "status": "success", 
        "student": {
            "id": student.id,
            "name": student.name,
            "usn": student.usn  # Frontend needs this for the dashboard!
        }
    }