from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
from sqlalchemy import func
import face_recognition
import numpy as np
import base64
import io
import json

from app.database import get_db
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.timetable import Timetable
from app.services.location_service import verify_location # Ensure this import works

# router = APIRouter(prefix="/attendance", tags=["Attendance"])
router = APIRouter(prefix="/attendance", tags=["Attendance"])

# 1. NEW: Identity Verification Endpoint
@router.post("/verify-identity")
def verify_identity(data: dict, db: Session = Depends(get_db)):
    try:
        image_str = data.get("image")
        if "," in image_str:
            image_str = image_str.split(",")[1]
        
        image_bytes = base64.b64decode(image_str)
        img = face_recognition.load_image_file(io.BytesIO(image_bytes))
        encodings = face_recognition.face_encodings(img)
        
        if not encodings:
            return {"status": "failed", "message": "No face detected"}
        
        captured_encoding = encodings[0]
        
        students = db.query(Student).all()
        for student in students:
            if student.face_encoding:
                known_encoding = np.array(json.loads(student.face_encoding))
                match = face_recognition.compare_faces([known_encoding], captured_encoding)
                if match[0]:
                    return {"status": "success", "student": {"name": student.name, "usn": student.usn}}
        
        return {"status": "failed", "message": "Identity not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark")
def mark_attendance(data: dict, db: Session = Depends(get_db)):

    print("RECEIVED DATA:", data)

    # Accept both old and new payload formats
    usn = data.get("usn")
    student_id = data.get("student_id")

    class_id = data.get("timetable_id") or data.get("class_id")

    lat = data.get("latitude")
    if lat is None:
        lat = data.get("lat")

    lon = data.get("longitude")
    if lon is None:
        lon = data.get("lon")

    print("USN:", usn)
    print("STUDENT_ID:", student_id)
    print("CLASS_ID:", class_id)
    print("LAT:", lat)
    print("LON:", lon)

    # Find student
    if usn:
        student = db.query(Student).filter(
            Student.usn == usn
        ).first()
    else:
        student = db.query(Student).filter(
            Student.id == student_id
        ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Find timetable
    timetable = db.query(Timetable).filter(
        Timetable.id == class_id
    ).first()

    print("TIMETABLE:", timetable)

    if not timetable:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    # Verify location
    is_valid, message = verify_location(
        lat,
        lon,
        timetable.classroom,
        db
    )

    if not is_valid:
        return {
            "status": "failed",
            "message": message
        }

    # Prevent duplicate attendance
    existing = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.timetable_id == class_id,
        func.date(Attendance.timestamp) == date.today()
    ).first()

    if existing:
        return {
            "status": "failed",
            "message": "Already marked today"
        }

    # Save attendance
    attendance = Attendance(
        student_id=student.id,
        timetable_id=class_id,
        status="Present",
        timestamp=datetime.now()
    )

    db.add(attendance)
    db.commit()

    return {
        "status": "success",
        "message": "Attendance marked successfully ✅"
    }


# 3. GET STUDENT HISTORY
@router.get("/student/{student_id}")
def get_student_history(student_id: str, db: Session = Depends(get_db)):
    history = db.query(Attendance).filter(Attendance.student_id == student_id).all()
    return [
        {
            "subject": a.timetable.subject if a.timetable else "Unknown",
            "date": a.timestamp.strftime("%Y-%m-%d"),
            "status": a.status
        }
        for a in history
    ]

# 4. GET TEACHER ANALYTICS
@router.get("/analytics/{teacher_id}")
def get_teacher_analytics(teacher_id: int, db: Session = Depends(get_db)):
    class_ids = db.query(Timetable.id).filter(Timetable.teacher_id == teacher_id).all()
    class_id_list = [c[0] for c in class_ids]

    if not class_id_list:
        return []

    results = db.query(
        Attendance.student_id,
        func.count(Attendance.id).filter(Attendance.status == "Present").label("present"),
        func.count(Attendance.id).filter(Attendance.status == "Absent").label("absent")
    ).filter(
        Attendance.timetable_id.in_(class_id_list)
    ).group_by(Attendance.student_id).all()

    return [
        {"student_id": row.student_id, "present": row.present, "absent": row.absent}
        for row in results
    ]