# from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
# from sqlalchemy.orm import Session
# from datetime import datetime
# from app.database import get_db
# from app.models.timetable import Timetable
# from app.models.classroom_polygon import ClassroomPolygon
# from app.services.timetable_service import upload_timetable
# from fastapi import APIRouter, Depends, HTTPException
# import pytz
# from app.models.classroom_polygon import ClassroomPolygon

# router = APIRouter(prefix="/timetable", tags=["Timetable"])

# @router.post("/upload")
# async def upload_timetable_endpoint(
#     file: UploadFile = File(...), 
#     semester: str = Form(...), 
#     db: Session = Depends(get_db)
# ):
#     try:
#         upload_timetable(file, semester, db)
#         return {"message": f"Timetable for Semester {semester} uploaded successfully!"}
#     except Exception as e:
#         print(f"Deployment Error: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))
# @router.get("/current-class")
# def get_current_class(db: Session = Depends(get_db)):
#     # 1. Handle Timezone (IST)
#     IST = pytz.timezone('Asia/Kolkata')
#     now_ist = datetime.now(IST)
#     current_time_obj = now_ist.time()
#     today = now_ist.strftime("%A")

#     # 2. Find the active class
#     result = db.query(Timetable).filter(
#         Timetable.day == today,
#         Timetable.start_time <= current_time_obj,
#         Timetable.end_time >= current_time_obj
#     ).first()

#     if not result:
#         return {"status": "No Class", "message": "No active class at this time."}

#     # 3. Fetch the location (polygon) for this classroom
#     poly_data = db.query(ClassroomPolygon).filter(
#         ClassroomPolygon.classroom == result.classroom
#     ).first()

#     return {
#         "status": "Class Active",
#         "class": {
#             "id": result.id,
#             "subject": result.subject,
#             "classroom": result.classroom,
#             # This is the string '[[lat, lon]]' the frontend will parse
#             "polygon": poly_data.polygon if poly_data else None, 
#             "is_lunch": result.is_lunch
#         }
#     }


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.timetable import Timetable
from app.models.teacher import Teacher  # Ensure this model is imported for the Join

router = APIRouter(prefix="/timetable", tags=["Timetable"])

@router.get("/current-class")
def get_current_class(db: Session = Depends(get_db)):
    # Get current time and day
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_day = now.strftime("%A")

    # Join Timetable with Teacher to get the 'teacher_name'
    active_class = db.query(
        Timetable.id,
        Timetable.subject,
        Timetable.classroom,
        Timetable.start_time,
        Timetable.end_time,
        Teacher.name.label("teacher_name")
    ).join(Teacher, Timetable.teacher_id == Teacher.id) \
     .filter(
        Timetable.day == current_day,
        Timetable.start_time <= current_time,
        Timetable.end_time >= current_time
    ).first()

    if not active_class:
        return {"status": "No Class", "message": "No class currently running"}

    # Return full details for the frontend header
    return {
        "status": "Class Active",
        "class": {
            "id": active_class.id,
            "subject": active_class.subject,
            "teacher_name": active_class.teacher_name,
            "classroom": active_class.classroom,
            "start_time": active_class.start_time,
            "end_time": active_class.end_time
        }
    }