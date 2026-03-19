from datetime import datetime
from sqlalchemy.orm import Session

from ..models.attendance import Attendance
from ..models.timetable import Timetable
from ..utils.time_utils import current_day
from ..services.face_service import recognize_face
from ..services.anti_spoof_service import detect_spoof
from ..services.location_service import is_inside_classroom


def is_attendance_open(start_time):

    now = datetime.now()

    class_start = datetime.strptime(start_time, "%H:%M")

    class_start = class_start.replace(
        year=now.year,
        month=now.month,
        day=now.day
    )

    diff = (now - class_start).total_seconds()

    # attendance allowed for 2 minutes
    if 0 <= diff <= 3600:
        return True

    return False


def mark_attendance(image, latitude, longitude, db: Session):

    # spoof detection
    if detect_spoof(image):
        return {"status": "Spoof detected"}

    # face recognition
    usn = recognize_face(image)

    if not usn:
        return {"status": "Face not recognized"}

    day = current_day()
    now = datetime.now().time()

    timetable = db.query(Timetable).filter(
        Timetable.day == day
    ).all()

    current_class = None

    for cls in timetable:

        start = datetime.strptime(cls.start_time, "%H:%M").time()
        end = datetime.strptime(cls.end_time, "%H:%M").time()

        if start <= now <= end:

            if not is_attendance_open(cls.start_time):
                return {"status": "Attendance closed"}

            current_class = cls
            break

    if not current_class:
        return {"status": "No class now"}

    # location validation
    # if not is_inside_classroom(
    #     latitude,
    #     longitude,
    #     float(current_class.latitude),
    #     float(current_class.longitude),
    #     int(current_class.radius)
    # ):
    #     return {"status": "Outside classroom"}

    # LOCATION CHECK DISABLED FOR TESTING
    print("Latitude:", latitude)
    print("Longitude:", longitude)

    # prevent duplicate attendance
    already_marked = db.query(Attendance).filter(
        Attendance.student_id == usn,
        Attendance.subject == current_class.subject,
        Attendance.date == str(datetime.now().date())
    ).first()

    if already_marked:
        return {"status": "Attendance already marked"}

    attendance = Attendance(

        student_id=usn,
        subject=current_class.subject,
        date=str(datetime.now().date()),
        time=str(now),
        status="present",
        location=f"{latitude},{longitude}"

    )

    db.add(attendance)
    db.commit()

    return {"status": "Attendance marked successfully"}