import csv
import io
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

# 1. Correct import for database.py located in the root 'backend/' folder
from database import get_db 

# 2. Correct imports for models located in 'backend/app/models/'
from app.models.timetable import timetable
from app.models.allowed_usn import allowed_usn
from app.models.classroom_polygon import classroom_polygon

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

# =========================================================================
# ROUTE 1: UPLOAD TIMETABLE
# =========================================================================
@router.post("/upload-timetable")
async def upload_timetable(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type.")
    
    try:
        contents = await file.read()
        text_data = contents.decode('utf-8-sig')
        buffer = io.StringIO(text_data)
        reader = csv.DictReader(buffer)
        reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
        
        for row_number, raw_row in enumerate(reader, start=1):
            row = {k: v.strip() for k, v in raw_row.items()}
            start_time = datetime.strptime(row['start_time'], "%H:%M").time()
            end_time = datetime.strptime(row['end_time'], "%H:%M").time()

            new_entry = timetable(
                semester=row['semester'],
                section=row['section'],
                day=row['day'],
                start_time=start_time,
                end_time=end_time,
                subject=row['subject'],
                teacher_id=int(row['teacher_id']),
                teacher_name=row['teacher_name'],
                classroom=row['classroom']
            )
            db.add(new_entry)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# =========================================================================
# ROUTE 2: UPLOAD ALLOWED USNs
# =========================================================================
@router.post("/upload-usns")
async def upload_usns(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        buffer = io.StringIO(contents.decode('utf-8-sig'))
        reader = csv.DictReader(buffer)
        
        for row in reader:
            usn_val = row['usn'].strip().upper()
            if not db.query(allowed_usn).filter(allowed_usn.usn == usn_val).first():
                db.add(allowed_usn(usn=usn_val))
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# =========================================================================
# ROUTE 3: UPLOAD POLYGONS
# =========================================================================
@router.post("/upload-polygon")
async def upload_polygon(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        buffer = io.StringIO(contents.decode('utf-8-sig'))
        reader = csv.DictReader(buffer)
        
        for row in reader:
            room = row['classroom'].strip()
            poly = row['polygon'].strip()
            
            exists = db.query(classroom_polygon).filter(classroom_polygon.classroom == room).first()
            if exists:
                exists.polygon = poly
            else:
                db.add(classroom_polygon(classroom=room, polygon=poly))
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))