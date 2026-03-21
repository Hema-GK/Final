# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
# from app.database import Base
# from datetime import datetime

# class Attendance(Base):
#     __tablename__ = "attendance"

#     id = Column(Integer, primary_key=True, index=True)
#     # Ensure this is Integer to match your pgAdmin screenshot
#     student_id = Column(Integer, ForeignKey("students.id")) 
#     timetable_id = Column(Integer, ForeignKey("timetable.id"))
#     timestamp = Column(DateTime, default=datetime.now)
#     status = Column(String(50), default="Present")

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    timetable_id = Column(Integer, ForeignKey("timetable.id"), nullable=False)
    status = Column(String(20), default="Present") # Present/Absent
    timestamp = Column(DateTime, default=func.now())

    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    timetable = relationship("Timetable", back_populates="attendance_records")