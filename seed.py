import json
from app.database import SessionLocal
from app.models.student import Student
from app.models.classroom_polygon import ClassroomPolygon

def seed():
    db = SessionLocal()
    try:
        # Add your student record
        new_student = Student(
            name="Hema G K",
            usn="4PS22CS062",
            section="A",
            face_encoding="[]" # You can update this later
        )
        db.add(new_student)

        # Add your classroom polygon coordinates
        new_poly = ClassroomPolygon(
            classroom="Room101",
            polygon=json.dumps([
                [12.51675, 76.88035],
                [12.51685, 76.88035],
                [12.51685, 76.88045],
                [12.51675, 76.88035]
            ])
        )
        db.add(new_poly)

        db.commit()
        print("✅ Data seeded! You can now log in on your phone.")
    except Exception as e:
        print(f"❌ Seed error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()