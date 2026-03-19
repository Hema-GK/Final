from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, date
# Ensure your location_service has the function 'is_student_in_room_polygon'
from app.services.location_service import check_radius_from_polygon_db
from app.database import get_db
from app.models.attendance import Attendance
from app.models.timetable import Timetable
from sqlalchemy import func

router = APIRouter(prefix="/attendance", tags=["Attendance"])
@router.post("/mark")
def mark_attendance(data: dict, db: Session = Depends(get_db)):
    student_id = data.get("student_id")
    timetable_id = data.get("timetable_id")
    lat = float(data.get("latitude"))
    lon = float(data.get("longitude"))

    timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    if not timetable:
        return {"status": "failed", "message": "Class not found"}

    # Use the 'classroom' name from the DB to find the Polygon center in CSV
    # Radius set to 15 meters (standard classroom size)
    # Unpack both the boolean 'allowed' and the 'dist'
    allowed, dist = check_radius_from_polygon_db(lat, lon, timetable.classroom, db, radius_limit=15)

    if not allowed:
        return {
            "status": "failed", 
            "message": f"You are outside the zone.",
            "distance": dist 
        }

    # ... [Your existing duplicate check and Attendance save logic here] ...
    # ... (Rest of your original duplicate check and db.commit code)

    # 3. PREVENT DUPLICATES
    existing = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.timetable_id == timetable_id,
        func.date(Attendance.timestamp) == date.today()
    ).first()

    if existing:
        return {"status": "failed", "message": "Attendance already marked for today"}

    # 4. SAVE ATTENDANCE
    new_record = Attendance(
        student_id=student_id,
        timetable_id=timetable_id,
        status="Present",
        timestamp=datetime.now()
    )

    db.add(new_record)
    db.commit()

    return {"status": "success", "message": "Attendance marked successfully"}