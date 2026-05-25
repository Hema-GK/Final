import csv
import io
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

# Import the specific database connection
from app.database.connection import get_db 

# Import the specific model classes directly from their files
from app.models.timetable import timetable
from app.models.allowed_usn import allowed_usn
from app.models.classroom_polygon import classroom_polygon

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

# =========================================================================
# ROUTE 1: UPLOAD TIMETABLE
# =========================================================================
@router.post("/upload-timetable")
async def upload_timetable(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # ... (Your validation code) ...
    # Use the 'timetable' class directly
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
    # ...

# =========================================================================
# ROUTE 2: UPLOAD ALLOWED USNs
# =========================================================================
@router.post("/upload-usns")
async def upload_usns(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # ... (Your validation code) ...
    # Use the 'allowed_usn' class directly
    exists = db.query(allowed_usn).filter(allowed_usn.usn == usn_val).first()
    if not exists:
        new_usn = allowed_usn(usn=usn_val)
        db.add(new_usn)
        inserted_count += 1
    # ...

# =========================================================================
# ROUTE 3: UPLOAD POLYGONS
# =========================================================================
@router.post("/upload-polygon")
async def upload_polygon(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # ... (Your validation code) ...
    # Use the 'classroom_polygon' class directly
    exists = db.query(classroom_polygon).filter(classroom_polygon.classroom == classroom_val).first()
    if exists:
        exists.polygon = polygon_val
    else:
        new_polygon = classroom_polygon(
            classroom=classroom_val,
            polygon=polygon_val
        )
        db.add(new_polygon)
    # ...