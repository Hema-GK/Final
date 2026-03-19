import pandas as pd
from sqlalchemy.orm import Session
from app.models.timetable import Timetable
from app.models.teacher import Teacher

def upload_timetable(file, semester_placeholder, db: Session):
    """
    Service to process the Timetable CSV.
    All column names are lowercase to match the Timetable.csv headers.
    """
    try:
        # Read the CSV file content from the FastAPI UploadFile object
        df = pd.read_csv(file.file)
        print(f"DEBUG: Found {len(df)} rows in CSV")

        # Optional: Clear existing timetable data for a clean upload
        # db.query(Timetable).delete()

        for index, row in df.iterrows():
            # 1. Handle Teacher logic
            # Checks 'teacher_id' column from your CSV
            t_id = row.get("teacher_id")
            teacher_name = "Unknown"
            
            if pd.notna(t_id):
                teacher = db.query(Teacher).filter(Teacher.id == int(t_id)).first()
                if teacher:
                    teacher_name = teacher.name
                else:
                    print(f"WARNING: Teacher ID {t_id} not found. Using 'Unknown'.")

            try:
                # 2. Create Database Entry
                # All 'row' keys now match your CSV headers exactly
                entry = Timetable(
                    semester=str(row["semester"]),
                    section=str(row["section"]),
                    day=str(row["day"]),
                    start_time=row["start_time"], 
                    end_time=row["end_time"],
                    subject=str(row["subject"]),
                    teacher_id=int(t_id) if pd.notna(t_id) else None,
                    teacher_name=teacher_name,
                    classroom=str(row["classroom"]) if pd.notna(row["classroom"]) else None,
                    is_lunch=str(row.get("is_lunch", "False")).lower() == 'true'
                )
                db.add(entry)
            except Exception as row_error:
                print(f"ERROR on row {index}: {row_error}")

        # 3. Commit all changes to Railway Database
        db.commit()
        print("DEBUG: Timetable upload successful and committed.")
        
    except Exception as e:
        db.rollback()
        print(f"CRITICAL ERROR: {str(e)}")
        raise e