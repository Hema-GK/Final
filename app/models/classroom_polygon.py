# from sqlalchemy import Column, Integer, String, JSON
# from app.database import Base

# class ClassroomPolygon(Base):
#     __tablename__ = "classroom_polygons"

#     id = Column(Integer, primary_key=True, index=True)
#     classroom = Column(String(50), unique=True, nullable=False)
#     polygon = Column(JSON, nullable=False)


from sqlalchemy import Column, Integer, String, JSON
from app.database import Base

class ClassroomPolygon(Base):
    __tablename__ = "classroom_polygons"

    id = Column(Integer, primary_key=True, index=True)

    classroom = Column(
        String(50),
        unique=True,
        nullable=False
    )

    polygon = Column(JSON, nullable=False)

    room_length_cm = Column(Integer)

    room_width_cm = Column(Integer)