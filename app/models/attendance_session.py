from sqlalchemy import Column, Integer, String
from app.database import Base

class AttendanceSession(Base):

    __tablename__ = "attendance_session"

    id = Column(Integer, primary_key=True, index=True)

    subject = Column(String(100))
    section = Column(String(20))
    semester = Column(String(20))
    class_name = Column(String(50))