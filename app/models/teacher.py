# from sqlalchemy import Column,Integer,String
# from ..database import Base

# class Teacher(Base):

#     __tablename__ = "teachers"

#     id = Column(Integer, primary_key=True)
#     name = Column(String(100))
#     email = Column(String(100))
#     password = Column(String(100))
#     class_name = Column(String(50))
#     subject = Column(String(50))

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship # Add this
from ..database import Base

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    password = Column(String(100))
    class_name = Column(String(50))
    subject = Column(String(50))

    # Add this relationship to link back to the timetable
    timetables = relationship("Timetable", back_populates="teacher")