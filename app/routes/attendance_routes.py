from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.services.location_service import verify_location_in_polygon
from app.database import get_db
from app.models.attendance import Attendance
from app.models.timetable import Timetable
from sqlalchemy import func

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/mark")
def mark_attendance(data: dict, db: Session = Depends(get_db)):
    student_id = data.get("student_id")
    timetable_id = data.get("timetable_id")
    student_bssid = data.get("bssid")
    # Defaulting to -100 (weak) if RSSI is missing from the frontend
    student_rssi = data.get("rssi", -100) 
    
    # 1. Parse Coordinates
    try:
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
    except (TypeError, ValueError):
        return {"status": "failed", "message": "Invalid GPS coordinates."}

    # 2. Fetch Session Details
    timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    if not timetable:
        return {"status": "failed", "message": "Class session not found."}

    # 3. Perform Dual-Verification (GPS + Wi-Fi)
    # This now uses the 'High-Confidence Override' logic in location_service.py
    is_verified, message = verify_location_in_polygon(
        lat, lon, student_bssid, student_rssi, timetable.classroom, db
    )

    if not is_verified:
        print(f"DEBUG: Verification Failed for Student {student_id}: {message}")
        return {"status": "failed", "message": message}

    # 4. Prevent Duplicate Attendance for the same day
    existing = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.timetable_id == timetable_id,
        func.date(Attendance.timestamp) == date.today()
    ).first()

    if existing:
        return {"status": "failed", "message": "Attendance already marked for today."}

    # 5. Save the Attendance Record
    new_record = Attendance(
        student_id=student_id,
        timetable_id=timetable_id,
        status="Present",
        timestamp=datetime.now()
    )
    
    try:
        db.add(new_record)
        db.commit()
        print(f"DEBUG: Success! Attendance marked for {student_id} in {timetable.classroom}")
        return {"status": "success", "message": "Attendance marked successfully! ✅"}
    except Exception as e:
        db.rollback()
        return {"status": "failed", "message": f"Database error: {str(e)}"}

@router.get("/student/{student_id}")
def get_student_history(student_id: str, db: Session = Depends(get_db)):
    history = db.query(Attendance).filter(Attendance.student_id == student_id).all()
    return [
        {
            "subject": a.timetable.subject if a.timetable else "Unknown", 
            "date": a.timestamp.strftime("%Y-%m-%d"), 
            "status": a.status
        } for a in history
    ]

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
    ).filter(Attendance.timetable_id.in_(class_id_list))\
     .group_by(Attendance.student_id).all()

    return [
        {
            "student_id": row.student_id, 
            "present": row.present, 
            "absent": row.absent
        } for row in results
    ]
