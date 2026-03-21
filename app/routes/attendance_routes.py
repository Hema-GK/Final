# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from datetime import datetime, date
# # Ensure your location_service has the function 'is_student_in_room_polygon'
# from app.services.location_service import check_radius_from_polygon_db
# from app.database import get_db
# from app.models.attendance import Attendance
# from app.models.timetable import Timetable
# from sqlalchemy import func

# router = APIRouter(prefix="/attendance", tags=["Attendance"])
# @router.post("/mark")
# def mark_attendance(data: dict, db: Session = Depends(get_db)):
#     student_id = data.get("student_id")
#     timetable_id = data.get("timetable_id")
#     lat = float(data.get("latitude"))
#     lon = float(data.get("longitude"))

#     timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
#     if not timetable:
#         return {"status": "failed", "message": "Class not found"}

#     # Use the 'classroom' name from the DB to find the Polygon center in CSV
#     # Radius set to 15 meters (standard classroom size)
#     # Unpack both the boolean 'allowed' and the 'dist'
#     allowed, dist = check_radius_from_polygon_db(lat, lon, timetable.classroom, db, radius_limit=15)

#     if not allowed:
#         return {
#             "status": "failed", 
#             "message": f"You are outside the zone.",
#             "distance": dist 
#         }

#     # ... [Your existing duplicate check and Attendance save logic here] ...
#     # ... (Rest of your original duplicate check and db.commit code)

#     # 3. PREVENT DUPLICATES
#     existing = db.query(Attendance).filter(
#         Attendance.student_id == student_id,
#         Attendance.timetable_id == timetable_id,
#         func.date(Attendance.timestamp) == date.today()
#     ).first()

#     if existing:
#         return {"status": "failed", "message": "Attendance already marked for today"}

#     # 4. SAVE ATTENDANCE
#     new_record = Attendance(
#         student_id=student_id,
#         timetable_id=timetable_id,
#         status="Present",
#         timestamp=datetime.now()
#     )

#     db.add(new_record)
#     db.commit()

#     return {"status": "success", "message": "Attendance marked successfully"}

# @router.get("/student/{student_id}")
# def get_student_history(student_id: int, db: Session = Depends(get_db)):
#     # Join with Timetable to get the Subject Name for the table
#     history = db.query(Attendance).filter(Attendance.student_id == student_id).all()
    
#     # If your Attendance model has a relationship with Timetable:
#     return [{"subject": a.timetable.subject, "date": a.date, "status": "Present"} for a in history]
    

# @router.get("/analytics/{teacher_id}")
# def get_teacher_analytics(teacher_id: int, db: Session = Depends(get_db)):
#     """
#     Returns data formatted for the frontend BarChart:
#     [{"usn": "1MS21CS001", "present": 10, "absent": 2}, ...]
#     """
    
#     # 1. Find all timetable IDs belonging to this teacher
#     class_ids = db.query(Timetable.id).filter(Timetable.teacher_id == teacher_id).all()
#     class_id_list = [c[0] for c in class_ids]

#     if not class_id_list:
#         return []

#     # 2. Query attendance records for those classes
#     # We group by student_id (or USN) and count the statuses
#     results = db.query(
#         Attendance.student_id,
#         func.count(Attendance.id).filter(Attendance.status == "Present").label("present"),
#         func.count(Attendance.id).filter(Attendance.status == "Absent").label("absent")
#     ).filter(Attendance.timetable_id.in_(class_id_list))\
#      .group_by(Attendance.student_id).all()

#     # 3. Format for Recharts (Frontend expects 'usn' or 'student_id')
#     chart_data = []
#     for row in results:
#         chart_data.append({
#             "usn": f"ID: {row[0]}", # Or row.student_id if you have a USN field
#             "present": row.present,
#             "absent": row.absent
#         })

#     return chart_data






from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.services.location_service import check_radius_from_polygon_db
from app.database import get_db
from app.models.attendance import Attendance
from app.models.timetable import Timetable
from sqlalchemy import func

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/mark")
def mark_attendance(data: dict, db: Session = Depends(get_db)):
    # Extract data from request
    student_id = data.get("student_id")
    timetable_id = data.get("timetable_id")
    
    try:
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
    except (TypeError, ValueError):
        return {"status": "failed", "message": "Invalid GPS coordinates received."}

    # 1. Validate Timetable Entry
    timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    if not timetable:
        return {"status": "failed", "message": "Class session not found in database."}

    # 2. Location Verification
    # radius_limit=30.0 covers the 16.45m - 19.80m drift seen in your tests
    # allowed, dist = check_radius_from_polygon_db(lat, lon, timetable.classroom, db, radius_limit=20.0)
    allowed, dist = check_radius_from_polygon_db(lat, lon, timetable.classroom, db, radius_limit=10.0)


    if not allowed:
        # dist will be a float (e.g., 19.8), preventing 'unverified distance' error
        return {
            "status": "failed", 
            "message": f"Geofencing Error: You are {dist}m away from the classroom center.",
            "distance": dist 
        }

    # 3. Prevent Duplicate Attendance for the same student on the same day
    # Assuming your Attendance model has a 'timestamp' column
    existing = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.timetable_id == timetable_id,
        func.date(Attendance.timestamp) == date.today()
    ).first()

    if existing:
        return {"status": "failed", "message": "Attendance already marked for this class today."}

    # 4. Save Attendance Record
    try:
        new_record = Attendance(
            student_id=student_id,
            timetable_id=timetable_id,
            status="Present",
            timestamp=datetime.now()
        )
        db.add(new_record)
        db.commit()
        
        return {
            "status": "success", 
            "message": "Attendance marked successfully!",
            "distance": dist
        }
    except Exception as e:
        db.rollback()
        print(f"Database Error: {e}")
        return {"status": "failed", "message": "Internal Server Error during saving."}

@router.get("/student/{student_id}")
def get_student_history(student_id: int, db: Session = Depends(get_db)):
    # Returns the attendance history for a specific student
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
    """
    Returns data formatted for the frontend BarChart:
    [{"usn": "Student ID", "present": 10, "absent": 2}, ...]
    """
    # 1. Find all timetable IDs belonging to this teacher
    class_ids = db.query(Timetable.id).filter(Timetable.teacher_id == teacher_id).all()
    class_id_list = [c[0] for c in class_ids]

    if not class_id_list:
        return []

    # 2. Query attendance records grouped by student
    results = db.query(
        Attendance.student_id,
        func.count(Attendance.id).filter(Attendance.status == "Present").label("present"),
        func.count(Attendance.id).filter(Attendance.status == "Absent").label("absent")
    ).filter(Attendance.timetable_id.in_(class_id_list))\
     .group_by(Attendance.student_id).all()

    return [
        {
            "usn": f"Student {row.student_id}", 
            "present": row.present, 
            "absent": row.absent
        } for row in results
    ]