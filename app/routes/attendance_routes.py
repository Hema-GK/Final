from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, date
from sqlalchemy import func

from app.database import get_db
from app.models.attendance import Attendance
from app.models.timetable import Timetable
from app.services.location_service import verify_location

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/mark")
def mark_attendance(data: dict, db: Session = Depends(get_db)):

    student_id = data.get("student_id")
    timetable_id = data.get("timetable_id")

    try:
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
    except:
        return {"status": "failed", "message": "Invalid GPS"}

    timetable = db.query(Timetable).filter(
        Timetable.id == timetable_id
    ).first()

    if not timetable:
        return {"status": "failed", "message": "Class not found"}

    # 🔥 ONLY GEO-FENCING
    verified, msg = verify_location(
        lat, lon, timetable.classroom, db
    )

    if not verified:
        return {"status": "failed", "message": msg}

    existing = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.timetable_id == timetable_id,
        func.date(Attendance.timestamp) == date.today()
    ).first()

    if existing:
        return {"status": "failed", "message": "Already marked"}

    new_record = Attendance(
        student_id=student_id,
        timetable_id=timetable_id,
        status="Present",
        timestamp=datetime.now()
    )

    db.add(new_record)
    db.commit()

    return {"status": "success", "message": "Attendance marked ✅"}