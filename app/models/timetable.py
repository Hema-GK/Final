from sqlalchemy import Column, Integer, String, ForeignKey, Time
from sqlalchemy.orm import relationship
from app.database import Base

class Timetable(Base):
    __tablename__ = "timetable"

    id = Column(Integer, primary_key=True, index=True)
    semester = Column(String(50))
    section = Column(String(20))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    subject = Column(String(100))
    day = Column(String(20))
    start_time = Column(Time)
    end_time = Column(Time)
    classroom = Column(String(100))
    teacher_name = Column(String(100)) # Keeps the column active

    # Relationships
    teacher = relationship("Teacher", back_populates="timetables")
    attendance_records = relationship("Attendance", back_populates="timetable")