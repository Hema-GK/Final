import csv
import io
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

# Ensure these point to your correct internal database & models paths
from app.database import get_db 
from app.models import timetable, allowed_usn, classroom_polygon

router = APIRouter(prefix="/admin", tags=["Admin Operations"])


# =========================================================================
# ROUTE 1: UPLOAD TIMETABLE (Expects Schedule Rows - NO USN Columns)
# =========================================================================
@router.post("/upload-timetable")
async def upload_timetable(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")
    
    try:
        contents = await file.read()
        text_data = contents.decode('utf-8-sig') # Strips Excel BOM formatting automatically
        buffer = io.StringIO(text_data)
        reader = csv.DictReader(buffer)
        
        # Normalize header column names to clean lowercase
        reader.fieldnames = [name.strip().replace('\r', '').replace('\n', '').lower() for name in reader.fieldnames]
        
        # Strict structural validation for timetable columns
        required_columns = {'section', 'semester', 'day', 'start_time', 'end_time', 'subject', 'teacher_id', 'teacher_name', 'classroom'}
        if not required_columns.issubset(set(reader.fieldnames)):
            missing = required_columns - set(reader.fieldnames)
            raise HTTPException(status_code=400, detail=f"Timetable CSV header mismatch. Missing: {list(missing)}")

        uploaded_records = 0
        for row_number, raw_row in enumerate(reader, start=1):
            try:
                row = {k: v.strip().replace('\r', '').replace('\n', '') if isinstance(v, str) else v for k, v in raw_row.items()}
                
                start_str = row['start_time']
                end_str = row['end_time']
                
                # Check formatting strings for time inputs
                start_time = datetime.strptime(start_str, "%H:%M:%S").time() if len(start_str.split(':')) == 3 else datetime.strptime(start_str, "%H:%M").time()
                end_time = datetime.strptime(end_str, "%H:%M:%S").time() if len(end_str.split(':')) == 3 else datetime.strptime(end_str, "%H:%M").time()

                new_entry = Timetable(
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
                uploaded_records += 1
            except Exception as row_err:
                raise HTTPException(status_code=400, detail=f"Error parsing timetable row {row_number}: {str(row_err)}")

        db.commit()
        return {"status": "success", "message": f"Successfully parsed and committed {uploaded_records} timetable rows."}

    except HTTPException as http_err:
        db.rollback()
        raise http_err
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Timetable database ingestion pipeline failure: {str(e)}")


# =========================================================================
# ROUTE 2: UPLOAD ALLOWED USNs (Expects Authorized Registration Roster)
# =========================================================================
@router.post("/upload-usns")
async def upload_usns(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a standard CSV file.")

    try:
        contents = await file.read()
        text_data = contents.decode('utf-8-sig')
        buffer = io.StringIO(text_data)
        reader = csv.DictReader(buffer)

        reader.fieldnames = [name.strip().replace('\r', '').replace('\n', '').lower() for name in reader.fieldnames]

        if 'usn' not in reader.fieldnames:
            raise HTTPException(status_code=400, detail="USN CSV structure error. Missing required column: 'usn'")

        inserted_count = 0
        for row in reader:
            raw_usn = row.get('usn')
            if not raw_usn:
                continue
                
            usn_val = raw_usn.strip().replace('\r', '').replace('\n', '').upper()
            if not usn_val:
                continue

            exists = db.query(AllowedUSN).filter(AllowedUSN.usn == usn_val).first()
            if not exists:
                new_usn = AllowedUSN(usn=usn_val)
                db.add(new_usn)
                inserted_count += 1

        db.commit()
        return {"status": "success", "message": f"Successfully parsed and saved {inserted_count} unique student USNs to roster."}

    except HTTPException as http_err:
        db.rollback()
        raise http_err
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process USN roster: {str(e)}")


# =========================================================================
# ROUTE 3: UPLOAD POLYGONS (Expects Geofence Coordinates mapping to Room)
# =========================================================================
@router.post("/upload-polygon")
async def upload_polygon(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")

    try:
        contents = await file.read()
        text_data = contents.decode('utf-8-sig')
        buffer = io.StringIO(text_data)
        reader = csv.DictReader(buffer)

        # Sanitize column headers explicitly matching your Polygons.csv structure
        reader.fieldnames = [name.strip().replace('\r', '').replace('\n', '').lower() for name in reader.fieldnames]

        required_columns = {'classroom', 'polygon'}
        if not required_columns.issubset(set(reader.fieldnames)):
            missing = required_columns - set(reader.fieldnames)
            raise HTTPException(status_code=400, detail=f"Polygon CSV header mismatch. Missing: {list(missing)}")

        inserted_count = 0
        for row_number, raw_row in enumerate(reader, start=1):
            try:
                row = {k: v.strip().replace('\r', '').replace('\n', '') if isinstance(v, str) else v for k, v in raw_row.items()}
                
                classroom_val = row['classroom']
                polygon_val = row['polygon']

                if not classroom_val or not polygon_val:
                    continue

                # If the classroom geofence boundary already exists, overwrite it; otherwise add new profile record
                exists = db.query(ClassroomPolygon).filter(ClassroomPolygon.classroom == classroom_val).first()
                if exists:
                    exists.polygon = polygon_val
                else:
                    new_polygon = ClassroomPolygon(
                        classroom=classroom_val,
                        polygon=polygon_val
                    )
                    db.add(new_polygon)
                inserted_count += 1
            except Exception as row_err:
                raise HTTPException(status_code=400, detail=f"Error parsing polygon row {row_number}: {str(row_err)}")

        db.commit()
        return {"status": "success", "message": f"Successfully parsed and stored {inserted_count} classroom geofence boundaries."}

    except HTTPException as http_err:
        db.rollback()
        raise http_err
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Polygon database ingestion pipeline failure: {str(e)}")