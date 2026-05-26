# import json
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from datetime import datetime, timedelta
# from sqlalchemy import func
# from sqlalchemy.types import Time

# from app.database import get_db
# from app.models.timetable import Timetable
# from app.models.teacher import Teacher 
# from app.models.classroom_polygon import ClassroomPolygon

# router = APIRouter(prefix="/timetable", tags=["Timetable"])

# @router.get("/current-class")
# def get_current_class(db: Session = Depends(get_db)):
#     # 1. TIMEZONE MANAGEMENT: Set to IST
#     utc_now = datetime.utcnow()
#     ist_now = utc_now + timedelta(hours=5, minutes=30)
    
#     # Extract current time as HH:MM:SS for comparison
#     current_time_str = ist_now.strftime("%H:%M:%S")
#     current_day = ist_now.strftime("%A")

#     # 2. Find Active Class
#     # We compare strings or use cast() if your DB types are strict. 
#     # This filter works if your start_time/end_time are Time or String types.
#     active_class = db.query(
#         Timetable.id,
#         Timetable.subject,
#         Timetable.classroom,
#         Timetable.start_time,
#         Timetable.end_time,
#         Timetable.section,
#         Teacher.name.label("teacher_name")
#     ).join(Teacher, Timetable.teacher_id == Teacher.id) \
#      .filter(
#         func.lower(Timetable.day) == current_day.lower(),
#         Timetable.start_time <= current_time_str,
#         Timetable.end_time >= current_time_str
#     ).first()

#     if not active_class:
#         return {
#             "status": "No Class", 
#             "message": f"Nothing scheduled for {current_day} at {ist_now.strftime('%H:%M:%S')}"
#         }

#     # 3. Fetch Coordinate Boundary Data
#     geo_poly = db.query(ClassroomPolygon).filter(
#         func.lower(ClassroomPolygon.classroom) == active_class.classroom.lower().strip()
#     ).first()

#     # CRITICAL FIX: Safe JSON parsing
#     polygon_coords = []
#     if geo_poly and geo_poly.polygon:
#         try:
#             if isinstance(geo_poly.polygon, str):
#                 polygon_coords = json.loads(geo_poly.polygon)
#             else:
#                 polygon_coords = geo_poly.polygon
#         except Exception as e:
#             print(f"Error parsing polygon: {e}")
#             polygon_coords = []

#     return {
#         "status": "Class Active",
#         "class": {
#             "id": active_class.id,
#             "subject": active_class.subject,
#             "teacher_name": active_class.teacher_name,
#             "classroom": active_class.classroom,
#             "section": active_class.section,
#             "polygon": polygon_coords, 
#             "start_time": str(active_class.start_time),
#             "end_time": str(active_class.end_time)
#         }
#     }
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func

from app.database import get_db
from app.models.timetable import Timetable
from app.models.teacher import Teacher
from app.models.classroom_polygon import ClassroomPolygon

router = APIRouter(
    prefix="/timetable",
    tags=["Timetable"]
)


@router.get("/current-class")
def get_current_class(
    db: Session = Depends(get_db)
):
    # IST Time
    utc_now = datetime.utcnow()
    ist_now = utc_now + timedelta(
        hours=5,
        minutes=30
    )

    current_time_str = ist_now.strftime(
        "%H:%M:%S"
    )

    current_day = ist_now.strftime(
        "%A"
    )

    active_class = (
        db.query(
            Timetable.id,
            Timetable.subject,
            Timetable.classroom,
            Timetable.start_time,
            Timetable.end_time,
            Timetable.section,
            Teacher.name.label(
                "teacher_name"
            )
        )
        .join(
            Teacher,
            Timetable.teacher_id
            == Teacher.id
        )
        .filter(
            func.lower(
                Timetable.day
            )
            == current_day.lower(),

            Timetable.start_time
            <= current_time_str,

            Timetable.end_time
            >= current_time_str
        )
        .first()
    )

    if not active_class:
        return {
            "status": "No Class",
            "message":
            f"Nothing scheduled for {current_day} at {current_time_str}"
        }

    geo_poly = (
        db.query(ClassroomPolygon)
        .filter(
            func.lower(
                ClassroomPolygon.classroom
            )
            ==
            active_class.classroom
            .lower()
            .strip()
        )
        .first()
    )

    polygon_coords = []
    display_polygon = []

    room_length_cm = None
    room_width_cm = None

    if geo_poly:

        room_length_cm = (
            geo_poly.room_length_cm
        )

        room_width_cm = (
            geo_poly.room_width_cm
        )

        # REAL GPS POLYGON
        try:
            if isinstance(
                geo_poly.polygon,
                str
            ):
                polygon_coords = json.loads(
                    geo_poly.polygon
                )
            else:
                polygon_coords = (
                    geo_poly.polygon
                )

        except Exception as e:
            print(
                f"Polygon Parse Error: {e}"
            )

            polygon_coords = []

        # DISPLAY POLYGON
        try:
            if isinstance(
                geo_poly.display_polygon,
                str
            ):
                display_polygon = json.loads(
                    geo_poly.display_polygon
                )
            else:
                display_polygon = (
                    geo_poly.display_polygon
                )

        except Exception as e:
            print(
                f"Display Polygon Parse Error: {e}"
            )

            display_polygon = []

    return {
        "status": "Class Active",
        "class": {

            "id":
            active_class.id,

            "subject":
            active_class.subject,

            "teacher_name":
            active_class.teacher_name,

            "classroom":
            active_class.classroom,

            "section":
            active_class.section,

            # REAL POLYGON
            "polygon":
            polygon_coords,

            # FRONTEND POLYGON
            "display_polygon":
            display_polygon,

            "room_length_cm":
            room_length_cm,

            "room_width_cm":
            room_width_cm,

            "start_time":
            str(
                active_class.start_time
            ),

            "end_time":
            str(
                active_class.end_time
            )
        }
    }