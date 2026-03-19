
# from fastapi import APIRouter, UploadFile, File, Depends
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models.classroom_polygon import ClassroomPolygon

# import csv
# import io
# import json

# router = APIRouter(prefix="/polygon", tags=["Polygon"])

# @router.post("/upload-csv")
# async def upload_polygon(file: UploadFile = File(...), db: Session = Depends(get_db)):

#     contents = await file.read()
#     csv_reader = csv.DictReader(io.StringIO(contents.decode("utf-8")))

#     for row in csv_reader:

#         polygon = json.loads(row["polygon"])

#         classroom_polygon = ClassroomPolygon(
#             classroom=row["classroom"],
#             polygon=polygon
#         )

#         db.add(classroom_polygon)

#     db.commit()

#     return {"status": "success", "message": "Polygon CSV uploaded"}


import csv
import io
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.classroom_polygon import ClassroomPolygon

router = APIRouter(prefix="/polygon", tags=["Polygon"])

@router.post("/upload-csv")
async def upload_polygon_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Check file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        # 2. Read file content as bytes
        contents = await file.read()
        # 3. Decode bytes to string and use StringIO for the CSV reader
        decoded = contents.decode("utf-8")
        buffer = io.StringIO(decoded)
        reader = csv.DictReader(buffer)

        # 4. Clear old polygons (to prevent duplicates)
        db.query(ClassroomPolygon).delete()

        # 5. Insert new data
        for row in reader:
            if 'classroom' not in row or 'polygon' not in row:
                raise HTTPException(status_code=400, detail="CSV must have 'classroom' and 'polygon' columns")
            
            new_poly = ClassroomPolygon(
                classroom=row["classroom"],
                polygon=row["polygon"] # This stores the string: [[lat,lon],...]
            )
            db.add(new_poly)
        
        db.commit()
        return {"status": "success", "message": "Classroom polygons uploaded successfully"}

    except Exception as e:
        db.rollback()
        print(f"Upload Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        file.file.close()