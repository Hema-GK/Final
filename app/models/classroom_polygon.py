from sqlalchemy import Column, Integer, String, JSON
from app.database import Base

class ClassroomPolygon(Base):

    __tablename__ = "classroom_polygons"

    id = Column(Integer, primary_key=True, index=True)
    classroom = Column(String(50))
    polygon = Column(JSON)