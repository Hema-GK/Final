from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.teacher import Teacher
from app.models.timetable import Timetable
from app.models.attendance import Attendance
from app.schemas.teacher_schema import TeacherRegister

router = APIRouter(prefix="/teachers", tags=["Teachers"])


# REGISTER
@router.post("/register")
def register_teacher(data: dict, db: Session = Depends(get_db)):

    existing = db.query(Teacher).filter(
        Teacher.email == data["email"]
    ).first()

    if existing:
        return {"status": "Teacher already registered"}

    teacher = Teacher(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        class_name=data["class_name"],
        subject=data["subject"]
    )

    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return {"status": "Teacher Registered Successfully"}



# LOGIN
@router.post("/login")
def teacher_login(data: dict, db: Session = Depends(get_db)):

    teacher = db.query(Teacher).filter(
        Teacher.email == data["email"]
    ).first()

    if not teacher:
        return {"status": "Teacher not found"}

    if teacher.password != data["password"]:
        return {"status": "Wrong password"}

    return {
        "status": "Login success",
        "teacher_id": teacher.id,
        "teacher_name": teacher.name
    }

# TODAY CLASSES
from datetime import datetime

@router.get("/today-classes/{teacher_id}")
def today_classes(teacher_id: int, db: Session = Depends(get_db)):

    today = datetime.now().strftime("%A").strip()

    classes = db.query(Timetable).filter(
        Timetable.teacher_id == teacher_id,
        Timetable.day.ilike(today)
    ).all()

    return classes


# UPDATE LOCATION
@router.post("/update-location")
def update_location(data: dict, db: Session = Depends(get_db)):

    timetable = db.query(Timetable).filter(
        Timetable.id == data["class_id"]
    ).first()

    if not timetable:
        return {"status": "failed", "message": "Class not found"}

    timetable.temp_latitude = float(data["latitude"])
    timetable.temp_longitude = float(data["longitude"])

    db.commit()

    return {"status": "Location updated successfully"}


# VIEW ATTENDANCE
@router.get("/class-attendance/{timetable_id}")
def class_attendance(timetable_id: int, db: Session = Depends(get_db)):

    records = db.query(Attendance).filter(
        Attendance.timetable_id == timetable_id
    ).all()

    return records