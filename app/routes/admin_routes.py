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

# from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models.timetable import Timetable

# import csv
# import io
# from datetime import datetime

# router = APIRouter(prefix="/admin", tags=["Admin"])

# @router.post("/upload-timetable")
# async def upload_timetable(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     try:
#         contents = await file.read()
#         # Using decode and splitlines handles potential Windows/Unix line ending issues better
#         decoded = contents.decode("utf-8")
#         csv_reader = csv.DictReader(io.StringIO(decoded))

#         # Optional: Clear old timetable data before uploading new one
#         # db.query(Timetable).delete()

#         for row in csv_reader:
#             # --- FIX 1: SKIP EMPTY ROWS ---
#             # This checks if the 'semester' column exists and isn't just whitespace
#             if not row.get("semester") or not row["semester"].strip():
#                 continue

#             # --- FIX 2: WRAP IN TRY/EXCEPT FOR DATA VALIDATION ---
#             try:
#                 timetable = Timetable(
#                     semester=int(row["semester"]),
#                     section=row["section"],
#                     day=row["day"],

#                     # Ensure your CSV time matches %H:%M (e.g. 14:02)
#                     start_time=datetime.strptime(row["start_time"].strip(), "%H:%M").time(),
#                     end_time=datetime.strptime(row["end_time"].strip(), "%H:%M").time(),

#                     subject=row["subject"],
#                     teacher_id=int(row["teacher_id"]),
#                     teacher_name=row["teacher_name"],
#                     classroom=row["classroom"],

#                     length=float(row["length"]),
#                     width=float(row["width"]),

#                     latitude=float(row["latitude"]),
#                     longitude=float(row["longitude"]),
#                     radius=float(row["radius"]),

#                     is_lunch=int(row["is_lunch"]),

#                     temp_latitude=None,
#                     temp_longitude=None
#                 )
#                 db.add(timetable)
#             except (ValueError, KeyError) as e:
#                 print(f"Skipping bad row: {row}. Error: {e}")
#                 continue

#         db.commit()
#         return {"status": "success", "message": "Timetable uploaded successfully"}

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))


from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import csv
import io
import json
from datetime import datetime

from app.database import get_db
from app.models.timetable import Timetable
from app.models.allowed_usn import AllowedUSN
from app.models.classroom_polygon import ClassroomPolygon

router = APIRouter(prefix="/admin", tags=["Admin"])


# 1. UPLOAD ALLOWED USN ROSTER
@router.post("/upload-usns")
async def upload_usns(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        contents = await file.read()
        decoded = contents.decode("utf-8")
        csv_reader = csv.reader(io.StringIO(decoded))
        
        for row in csv_reader:
            # Skip empty lines or header rows
            if not row or not row[0].strip() or row[0].strip().upper() == "USN":
                continue
            
            usn_val = str(row[0]).strip().upper()
            
            # Skip if the USN already exists in the pre-verified table to prevent duplicates
            exists = db.query(AllowedUSN).filter(AllowedUSN.usn == usn_val).first()
            if not exists:
                new_usn = AllowedUSN(usn=usn_val)
                db.add(new_usn)
                
        db.commit()
        return {"status": "success", "message": "Roster of allowed USNs uploaded successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()


# 2. UPLOAD CLASSROOM GEOLOCATION POLYGONS
@router.post("/upload-polygons")
async def upload_polygon_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        contents = await file.read()
        decoded = contents.decode("utf-8")
        buffer = io.StringIO(decoded)
        reader = csv.DictReader(buffer)

        # Clear old polygons to prevent unique constraints or stale coordinates
        db.query(ClassroomPolygon).delete()

        for row in reader:
            if 'classroom' not in row or 'polygon' not in row:
                raise HTTPException(status_code=400, detail="CSV must have 'classroom' and 'polygon' columns")
            
            # Safely parse the coordinate string array into a proper JSON list object
            try:
                polygon_json = json.loads(row["polygon"])
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail=f"Invalid JSON array structure in polygon field for room {row['classroom']}")

            new_poly = ClassroomPolygon(
                classroom=row["classroom"].strip(),
                polygon=polygon_json
            )
            db.add(new_poly)
        
        db.commit()
        return {"status": "success", "message": "Classroom polygons uploaded successfully"}

    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        print(f"Upload Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        file.file.close()


# 3. UPLOAD TIMETABLE DATA
@router.post("/upload-timetable")
async def upload_timetable(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        contents = await file.read()
        decoded = contents.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(decoded))

        for row in csv_reader:
            if not row.get("semester") or not row["semester"].strip():
                continue

            try:
                timetable = Timetable(
                    semester=int(row["semester"]),
                    section=row["section"].strip(),
                    day=row["day"].strip(),
                    start_time=datetime.strptime(row["start_time"].strip(), "%H:%M").time(),
                    end_time=datetime.strptime(row["end_time"].strip(), "%H:%M").time(),
                    subject=row["subject"].strip(),
                    teacher_id=int(row["teacher_id"]),
                    teacher_name=row["teacher_name"].strip(),
                    classroom=row["classroom"].strip(),
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
    finally:
        file.file.close()