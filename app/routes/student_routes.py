# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# import face_recognition
# import numpy as np
# import base64
# import json
# import io
# from app.database import get_db
# from app.models.student import Student

# # Prefix matches the frontend call (plural: /students)
# router = APIRouter(prefix="/students", tags=["Students"])

# @router.post("/register")
# def register_student(data: dict, db: Session = Depends(get_db)):
#     # 1. Clean the USN (removing accidental spaces)
#     usn_clean = str(data.get("usn", "")).strip()
    
#     # 2. Duplicate Check
#     existing = db.query(Student).filter(Student.usn == usn_clean).first()
#     if existing:
#         return {"status": "failed", "message": "USN already exists"}

#     try:
#         # 3. Handle Image
#         image_data = data["image"].split(",")[1]
#         image_bytes = base64.b64decode(image_data)
#         img = face_recognition.load_image_file(io.BytesIO(image_bytes))
        
#         encodings = face_recognition.face_encodings(img)
#         if len(encodings) == 0:
#             return {"status": "failed", "message": "Face not clear"}
        
#         face_encoding_str = json.dumps(encodings[0].tolist())

#         # 4. Explicitly create the student object
#         new_student = Student(
#             name=data.get("name"),
#             usn=usn_clean,
#             section=data.get("section"),
#             semester=data.get("semester"),
#             password=str(data.get("password", "")).strip(),
#             face_encoding=face_encoding_str
#         )

#         # 5. Force the save
#         db.add(new_student)
#         db.commit() # This must happen for it to show in pgAdmin
#         db.refresh(new_student) 
        
#         return {"status": "success", "message": "Registered successfully"}

#     except Exception as e:
#         db.rollback()
#         print(f"DB ERROR: {e}")
#         return {"status": "failed", "message": str(e)}
# @router.post("/login")
# def login_student(data: dict, db: Session = Depends(get_db)):
#     # Clean input data
#     input_usn = str(data.get("usn", "")).strip()
#     input_pwd = str(data.get("password", "")).strip()

#     # Case-insensitive USN check is safer for mobile keyboards
#     student = db.query(Student).filter(Student.usn == input_usn).first()

#     if not student:
#         return {"status": "failed", "message": "Invalid Credentials"}

#     # Clean database data for comparison
#     db_pwd = str(student.password).strip()

#     if db_pwd != input_pwd:
#         return {"status": "failed", "message": "Invalid Credentials"}

#     # --- MATCHING FRONTEND EXPECTATIONS ---
#     return {
#         "status": "success", 
#         "student": {
#             "id": student.id,
#             "name": student.name,
#             "usn": student.usn  # Frontend needs this for the dashboard!
#         }
#     }


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import face_recognition
import numpy as np
import base64
import json
import io
from app.database import get_db
from app.models.student import Student
from app.models.allowed_usn import AllowedUSN
from app.security import hash_password, verify_password

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/register")
def register_student(data: dict, db: Session = Depends(get_db)):
    usn_clean = str(data.get("usn", "")).strip().upper()
    
    # 1. Verification Check: Check if Admin pre-uploaded this USN
    allowed = db.query(AllowedUSN).filter(AllowedUSN.usn == usn_clean).first()
    if not allowed:
        return {"status": "failed", "message": "Your USN is not authorized by Admin. Registration blocked."}
    
    # 2. Duplicate Check
    existing = db.query(Student).filter(Student.usn == usn_clean).first()
    if existing:
        return {"status": "failed", "message": "USN already registered"}

    try:
        # 3. Handle Biometric Face Processing
        image_data = data["image"].split(",")[1]
        image_bytes = base64.b64decode(image_data)
        img = face_recognition.load_image_file(io.BytesIO(image_bytes))
        
        encodings = face_recognition.face_encodings(img)
        if len(encodings) == 0:
            return {"status": "failed", "message": "Face not clear"}
        
        face_encoding_str = json.dumps(encodings[0].tolist())
        hashed_pwd = hash_password(str(data.get("password", "")).strip())

        # 4. Save detailed metrics
        new_student = Student(
            name=data.get("name"),
            usn=usn_clean,
            year=int(data.get("year")),
            semester=int(data.get("semester")),
            section=data.get("section"),
            password=hashed_pwd,
            face_encoding=face_encoding_str
        )

        db.add(new_student)
        db.commit()
        db.refresh(new_student) 
        
        return {"status": "success", "message": "Registered successfully"}

    except Exception as e:
        db.rollback()
        print(f"DB ERROR: {e}")
        return {"status": "failed", "message": str(e)}

# @router.post("/register")
# def register_student(data: dict, db: Session = Depends(get_db)):
#     try:
#         usn_clean = str(data.get("usn", "")).strip().upper()
        
#         # 1. Verification Check
#         allowed = db.query(AllowedUSN).filter(AllowedUSN.usn == usn_clean).first()
#         if not allowed:
#             return {"status": "failed", "message": "USN not authorized"}
        
#         # 2. Duplicate Check
#         existing = db.query(Student).filter(Student.usn == usn_clean).first()
#         if existing:
#             return {"status": "failed", "message": "USN already registered"}

#         # 3. Handle Biometric Face Processing
#         # ... (your existing face logic) ...

#         # 4. Save to Database
#         new_student = Student(...)
#         db.add(new_student)
#         db.commit()
#         db.refresh(new_student)
        
#         # CRITICAL: Ensure you return something here!
#         return {"status": "success", "message": "Registered successfully"}

#     except Exception as e:
#         db.rollback()
#         print(f"DEBUG: Critical Error: {e}")
#         # Ensure you return an error response, not just print it
#         return {"status": "failed", "message": str(e)}

@router.post("/login")
def login_student(data: dict, db: Session = Depends(get_db)):
    input_usn = str(data.get("usn", "")).strip().upper()
    input_pwd = str(data.get("password", "")).strip()

    student = db.query(Student).filter(Student.usn == input_usn).first()

    if not student:
        return {"status": "failed", "message": "Invalid Credentials"}

    # Secure verification verification step
    if not verify_password(input_pwd, student.password):
        return {"status": "failed", "message": "Invalid Credentials"}

    return {
        "status": "success", 
        "student": {
            "id": student.id,
            "name": student.name,
            "usn": student.usn 
        }
    }