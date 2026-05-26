# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from datetime import datetime

# from app.database import get_db
# from app.models.teacher import Teacher
# from app.models.timetable import Timetable
# from app.models.attendance import Attendance
# from app.schemas.teacher_schema import TeacherRegister

# router = APIRouter(prefix="/teachers", tags=["Teachers"])


# # REGISTER
# @router.post("/register")
# def register_teacher(data: dict, db: Session = Depends(get_db)):

#     existing = db.query(Teacher).filter(
#         Teacher.email == data["email"]
#     ).first()

#     if existing:
#         return {"status": "Teacher already registered"}

#     teacher = Teacher(
#         name=data["name"],
#         email=data["email"],
#         password=data["password"],
#         class_name=data["class_name"],
#         subject=data["subject"]
#     )

#     db.add(teacher)
#     db.commit()
#     db.refresh(teacher)

#     return {"status": "Teacher Registered Successfully"}



# # LOGIN
# @router.post("/login")
# def teacher_login(data: dict, db: Session = Depends(get_db)):

#     teacher = db.query(Teacher).filter(
#         Teacher.email == data["email"]
#     ).first()

#     if not teacher:
#         return {"status": "Teacher not found"}

#     if teacher.password != data["password"]:
#         return {"status": "Wrong password"}

#     return {
#         "status": "Login success",
#         "teacher_id": teacher.id,
#         "teacher_name": teacher.name
#     }

# # TODAY CLASSES
# from datetime import datetime

# @router.get("/today-classes/{teacher_id}")
# def today_classes(teacher_id: int, db: Session = Depends(get_db)):

#     today = datetime.now().strftime("%A").strip()

#     classes = db.query(Timetable).filter(
#         Timetable.teacher_id == teacher_id,
#         Timetable.day.ilike(today)
#     ).all()

#     return classes


# # UPDATE LOCATION
# # UPDATE CLASSROOM NAME & COORDINATES
# @router.post("/update-classroom")
# def update_classroom(data: dict, db: Session = Depends(get_db)):
#     timetable_id = data.get("timetable_id")
#     new_room_name = data.get("classroom_name")

#     # 1. Find the timetable entry
#     timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
#     if not timetable:
#         raise HTTPException(status_code=404, detail="Timetable entry not found")

#     # 2. Find the classroom in your database to get its predefined polygons/coords
#     # Assuming you have a model named 'Classroom'
#     from app.models.classroom_polygon import Classroom # Adjust import based on your project
#     target_room = db.query(Classroom).filter(Classroom.name.ilike(new_room_name)).first()

#     if not target_room:
#         return {"status": "failed", "message": f"Room '{new_room_name}' not found in database"}

#     # 3. Update the timetable with the new room name and its stored coordinates
#     timetable.classroom = target_room.name
#     timetable.temp_latitude = target_room.latitude
#     timetable.temp_longitude = target_room.longitude

#     db.commit()

#     return {
#         "status": "success", 
#         "message": f"Class moved to {target_room.name}",
#         "new_room": target_room.name
#     }


# # VIEW ATTENDANCE
# @router.get("/class-attendance/{timetable_id}")
# def class_attendance(timetable_id: int, db: Session = Depends(get_db)):

#     records = db.query(Attendance).filter(
#         Attendance.timetable_id == timetable_id
#     ).all()

#     return records

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from datetime import datetime

# from app.database import get_db
# from app.models.teacher import Teacher
# from app.models.timetable import Timetable
# from app.models.attendance import Attendance
# from app.schemas.teacher_schema import TeacherRegister
# # IMPORTED BOTH: Need hash_password for registration and verify_password for login
# from app.security import hash_password, verify_password 

# router = APIRouter(prefix="/teachers", tags=["Teachers"])


# # REGISTER
# @router.post("/register")
# def register_teacher(data: dict, db: Session = Depends(get_db)):

#     existing = db.query(Teacher).filter(
#         Teacher.email == data["email"]
#     ).first()

#     if existing:
#         return {"status": "Teacher already registered"}

#     hashed_pwd = hash_password(data["password"])

#     teacher = Teacher(
#         name=data["name"],
#         email=data["email"],
#         password=hashed_pwd,
#         class_name=data["class_name"],
#         subject=data["subject"]
#     )

#     db.add(teacher)
#     db.commit()
#     db.refresh(teacher)

#     return {"status": "Teacher Registered Successfully"}



# # LOGIN
# @router.post("/login")
# def teacher_login(data: dict, db: Session = Depends(get_db)):

#     teacher = db.query(Teacher).filter(
#         Teacher.email == data["email"]
#     ).first()

#     if not teacher:
#         return {"status": "Teacher not found"}

#     # FIXED: Uses your security script to compare the typed password against the hashed string safely
#     if not verify_password(data["password"], teacher.password):
#         return {"status": "Wrong password"}

#     return {
#         "status": "Login success",
#         "teacher_id": teacher.id,
#         "teacher_name": teacher.name
#     }


# # TODAY CLASSES
# @router.get("/today-classes/{teacher_id}")
# def today_classes(teacher_id: int, db: Session = Depends(get_db)):

#     today = datetime.now().strftime("%A").strip()

#     classes = db.query(Timetable).filter(
#         Timetable.teacher_id == teacher_id,
#         Timetable.day.ilike(today)
#     ).all()

#     return classes


# # UPDATE LOCATION / CLASSROOM NAME & COORDINATES
# @router.post("/update-classroom")
# def update_classroom(data: dict, db: Session = Depends(get_db)):
#     timetable_id = data.get("timetable_id")
#     new_room_name = data.get("classroom_name")

#     timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
#     if not timetable:
#         raise HTTPException(status_code=404, detail="Timetable entry not found")

#     from app.models.classroom import Classroom 
#     target_room = db.query(Classroom).filter(Classroom.name.ilike(new_room_name)).first()

#     if not target_room:
#         return {"status": "failed", "message": f"Room '{new_room_name}' not found in database"}

#     timetable.classroom = target_room.name
#     timetable.temp_latitude = target_room.latitude
#     timetable.temp_longitude = target_room.longitude

#     db.commit()

#     return {
#         "status": "success", 
#         "message": f"Class moved to {target_room.name}",
#         "new_room": target_room.name
#     }


# # VIEW ATTENDANCE
# @router.get("/class-attendance/{timetable_id}")
# def class_attendance(
#     timetable_id: int,
#     db: Session = Depends(get_db)
# ):

#     records = db.query(
#         Attendance
#     ).filter(
#         Attendance.timetable_id == timetable_id
#     ).all()

#     return [
#         {
#             "student_id": r.student.id,
#             "student_name": r.student.name,
#             "usn": r.student.usn,
#             "status": r.status,
#             "timestamp": str(r.timestamp)
#         }
#         for r in records
#     ]


# @router.get("/class-details/{timetable_id}")
# def class_details(timetable_id: int, db: Session = Depends(get_db)):

#     timetable = db.query(Timetable).filter(
#         Timetable.id == timetable_id
#     ).first()

#     if not timetable:
#         raise HTTPException(404, "Class not found")

#     room = db.query(ClassroomPolygon).filter(
#         ClassroomPolygon.classroom == timetable.classroom
#     ).first()

#     records = db.query(Attendance).filter(
#         Attendance.timetable_id == timetable_id
#     ).all()

#     students = []

#     for r in records:
#         students.append({
#             "student_id": r.student.id,
#             "name": r.student.name,
#             "usn": r.student.usn,
#             "status": r.status,
#             "timestamp": str(r.timestamp)
#         })

#     return {
#         "class_info": {
#             "subject": timetable.subject,
#             "teacher": timetable.teacher_name,
#             "room": timetable.classroom,
#             "start_time": str(timetable.start_time),
#             "end_time": str(timetable.end_time)
#         },
#         "polygon": room.display_polygon if room else [],
#         "room_length_cm": room.room_length_cm if room else 0,
#         "room_width_cm": room.room_width_cm if room else 0,
#         "attendance": students
#     }

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db

from app.models.teacher import Teacher
from app.models.timetable import Timetable
from app.models.attendance import Attendance
from app.models.classroom_polygon import ClassroomPolygon

from app.security import (
    hash_password,
    verify_password
)

router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)


# -------------------------------------------------
# REGISTER
# -------------------------------------------------

@router.post("/register")
def register_teacher(
    data: dict,
    db: Session = Depends(get_db)
):

    existing = db.query(
        Teacher
    ).filter(
        Teacher.email == data["email"]
    ).first()

    if existing:
        return {
            "status":
            "Teacher already registered"
        }

    teacher = Teacher(
        name=data["name"],
        email=data["email"],
        password=hash_password(
            data["password"]
        ),
        class_name=data["class_name"],
        subject=data["subject"]
    )

    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return {
        "status":
        "Teacher Registered Successfully"
    }


# -------------------------------------------------
# LOGIN
# -------------------------------------------------

@router.post("/login")
def teacher_login(
    data: dict,
    db: Session = Depends(get_db)
):

    teacher = db.query(
        Teacher
    ).filter(
        Teacher.email == data["email"]
    ).first()

    if not teacher:
        return {
            "status":
            "Teacher not found"
        }

    if not verify_password(
        data["password"],
        teacher.password
    ):
        return {
            "status":
            "Wrong password"
        }

    return {
        "status":
        "Login success",

        "teacher_id":
        teacher.id,

        "teacher_name":
        teacher.name
    }


# -------------------------------------------------
# TODAY CLASSES
# -------------------------------------------------

@router.get("/today-classes/{teacher_id}")
def today_classes(
    teacher_id: int,
    db: Session = Depends(get_db)
):

    today = datetime.now().strftime(
        "%A"
    ).strip()

    classes = db.query(
        Timetable
    ).filter(
        Timetable.teacher_id == teacher_id,
        Timetable.day.ilike(today)
    ).all()

    return classes


# -------------------------------------------------
# UPDATE CLASSROOM
# -------------------------------------------------

@router.post("/update-classroom")
def update_classroom(
    data: dict,
    db: Session = Depends(get_db)
):

    timetable_id = data.get(
        "timetable_id"
    )

    new_room_name = data.get(
        "classroom_name"
    )

    timetable = db.query(
        Timetable
    ).filter(
        Timetable.id == timetable_id
    ).first()

    if not timetable:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    room = db.query(
        ClassroomPolygon
    ).filter(
        ClassroomPolygon.classroom.ilike(
            new_room_name
        )
    ).first()

    if not room:
        return {
            "status": "failed",
            "message":
            f"Room '{new_room_name}' not found"
        }

    timetable.classroom = room.classroom

    db.commit()

    return {
        "status": "success",
        "message":
        f"Class moved to {room.classroom}",
        "new_room":
        room.classroom
    }


# -------------------------------------------------
# ATTENDANCE LIST
# -------------------------------------------------

@router.get("/class-attendance/{timetable_id}")
def class_attendance(
    timetable_id: int,
    db: Session = Depends(get_db)
):

    records = db.query(
        Attendance
    ).filter(
        Attendance.timetable_id ==
        timetable_id
    ).all()

    return [
        {
            "student_id":
            r.student.id,

            "student_name":
            r.student.name,

            "usn":
            r.student.usn,

            "status":
            r.status,

            "timestamp":
            str(r.timestamp)
        }
        for r in records
    ]


# -------------------------------------------------
# FULL CLASS DETAILS
# -------------------------------------------------

@router.get("/class-details/{timetable_id}")
def class_details(
    timetable_id: int,
    db: Session = Depends(get_db)
):

    timetable = db.query(
        Timetable
    ).filter(
        Timetable.id == timetable_id
    ).first()

    if not timetable:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    room = db.query(
        ClassroomPolygon
    ).filter(
        ClassroomPolygon.classroom ==
        timetable.classroom
    ).first()

    attendance_records = db.query(
        Attendance
    ).filter(
        Attendance.timetable_id ==
        timetable_id
    ).all()

    students = []

    for record in attendance_records:

        students.append({
            "student_id":
            record.student.id,

            "name":
            record.student.name,

            "usn":
            record.student.usn,

            "status":
            record.status,

            "timestamp":
            str(record.timestamp)
        })

    return {

        "class_info": {

            "subject":
            timetable.subject,

            "teacher":
            timetable.teacher_name,

            "room":
            timetable.classroom,

            "start_time":
            str(timetable.start_time),

            "end_time":
            str(timetable.end_time)
        },

        "polygon":
        room.display_polygon
        if room else [],

        "room_length_cm":
        room.room_length_cm
        if room else 0,

        "room_width_cm":
        room.room_width_cm
        if room else 0,

        "attendance":
        students
    }