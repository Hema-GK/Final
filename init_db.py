from app.database import engine, Base
# You MUST import your models here so SQLAlchemy "sees" them
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.timetable import Timetable
from app.models.attendance import Attendance
from app.models.marks import Marks
from app.models.classroom_polygon import ClassroomPolygon

print("Creating tables in Render PostgreSQL...")
# Now Base is imported directly from database.py
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully!")