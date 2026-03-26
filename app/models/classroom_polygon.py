# from sqlalchemy import Column, Integer, String, JSON, Float # Added Float
# from app.database import Base

# class ClassroomPolygon(Base):
#     __tablename__ = "classroom_polygons"

#     id = Column(Integer, primary_key=True, index=True)
#     classroom = Column(String(50), unique=True, index=True)
#     polygon = Column(JSON)  # Stores [[lat, lon], ...]
    
#     # # ADD THESE THREE LINES BELOW:
#     # center_lat = Column(Float, nullable=True)
#     # center_lon = Column(Float, nullable=True)
#     # calculated_radius = Column(Float, nullable=True)

from sqlalchemy import Column, Integer, String, JSON
from app.database import Base

class ClassroomPolygon(Base):
    __tablename__ = "classroom_polygons"

    id = Column(Integer, primary_key=True, index=True)
    classroom = Column(String(50), unique=True, nullable=False)

    # GPS polygon
    polygon = Column(JSON, nullable=False)

    # 🔥 NEW: BLE UUID
    beacon_uuid = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<ClassroomPolygon(classroom='{self.classroom}', uuid='{self.beacon_uuid}')>"