from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base
from datetime import datetime

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    # Ensure this is Integer to match your pgAdmin screenshot
    student_id = Column(Integer, ForeignKey("students.id")) 
    timetable_id = Column(Integer, ForeignKey("timetable.id"))
    timestamp = Column(DateTime, default=datetime.now)
    status = Column(String(50), default="Present")