# from fastapi import APIRouter, UploadFile, File, Depends
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models.timetable import Timetable

# import csv
# import io
# from datetime import datetime

# router = APIRouter(prefix="/admin", tags=["Admin"])


# @router.post("/upload-timetable")
# async def upload_timetable(file: UploadFile = File(...), db: Session = Depends(get_db)):

#     contents = await file.read()
#     csv_reader = csv.DictReader(io.StringIO(contents.decode("utf-8")))

#     for row in csv_reader:

#         timetable = Timetable(
#             semester=int(row["semester"]),
#             section=row["section"],
#             day=row["day"],

#             start_time=datetime.strptime(row["start_time"], "%H:%M").time(),
#             end_time=datetime.strptime(row["end_time"], "%H:%M").time(),

#             subject=row["subject"],
#             teacher_id=int(row["teacher_id"]),
#             teacher_name=row["teacher_name"],
#             classroom=row["classroom"],

#             length=float(row["length"]),
#             width=float(row["width"]),

#             latitude=float(row["latitude"]),
#             longitude=float(row["longitude"]),
#             radius=float(row["radius"]),

#             is_lunch=int(row["is_lunch"]),

#             temp_latitude=None,
#             temp_longitude=None
#         )

#         db.add(timetable)

#     db.commit()

#     return {"status": "success", "message": "Timetable uploaded"}

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.timetable import Timetable

import csv
import io
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/upload-timetable")
async def upload_timetable(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        # Using decode and splitlines handles potential Windows/Unix line ending issues better
        decoded = contents.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(decoded))

        # Optional: Clear old timetable data before uploading new one
        # db.query(Timetable).delete()

        for row in csv_reader:
            # --- FIX 1: SKIP EMPTY ROWS ---
            # This checks if the 'semester' column exists and isn't just whitespace
            if not row.get("semester") or not row["semester"].strip():
                continue

            # --- FIX 2: WRAP IN TRY/EXCEPT FOR DATA VALIDATION ---
            try:
                timetable = Timetable(
                    semester=int(row["semester"]),
                    section=row["section"],
                    day=row["day"],

                    # Ensure your CSV time matches %H:%M (e.g. 14:02)
                    start_time=datetime.strptime(row["start_time"].strip(), "%H:%M").time(),
                    end_time=datetime.strptime(row["end_time"].strip(), "%H:%M").time(),

                    subject=row["subject"],
                    teacher_id=int(row["teacher_id"]),
                    teacher_name=row["teacher_name"],
                    classroom=row["classroom"],

                    length=float(row["length"]),
                    width=float(row["width"]),

                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                    radius=float(row["radius"]),

                    is_lunch=int(row["is_lunch"]),

                    temp_latitude=None,
                    temp_longitude=None
                )
                db.add(timetable)
            except (ValueError, KeyError) as e:
                print(f"Skipping bad row: {row}. Error: {e}")
                continue

        db.commit()
        return {"status": "success", "message": "Timetable uploaded successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))