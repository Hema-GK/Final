from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class QRSession(Base):
    __tablename__ = "qr_sessions"

    id = Column(Integer, primary_key=True, index=True)
    timetable_id = Column(Integer)
    token = Column(String, unique=True)
    expires_at = Column(DateTime)