# from sqlalchemy import Column, Integer, String, DateTime
# from app.database import Base


# class Student(Base):

#     __tablename__ = "students"

#     id = Column(Integer, primary_key=True, index=True)

#     name = Column(String(100))
#     usn = Column(String(50), unique=True)

#     password = Column(String(100))

#     class_name = Column(String(20))
#     section = Column(String(10))

#     image = Column(String(255))

#     registered_at = Column(DateTime)

# from sqlalchemy import Column, Integer, String, DateTime, Text
# from app.database import Base

# class Student(Base):

#     __tablename__ = "students"

#     id = Column(Integer, primary_key=True, index=True)

#     name = Column(String(100))
#     usn = Column(String(50), unique=True)

#     password = Column(String(100))

#     class_name = Column(String(20))
#     section = Column(String(10))

#     image = Column(String(255))
#     semester = Column(Integer)
#     face_encoding = Column(Text)   # NEW

#     registered_at = Column(DateTime)

# from sqlalchemy import Column, Integer, String, Text
# from app.database import Base

# class Student(Base):
#     __tablename__ = "students"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100))
#     usn = Column(String(50), unique=True, index=True)
#     section = Column(String(10))
#     semester = Column(Integer)
#     password = Column(String(100))
#     face_encoding = Column(Text)

from sqlalchemy import Column, Integer, String, Text
from app.database import Base
from sqlalchemy.orm import relationship

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    usn = Column(String(50), unique=True, index=True)
    section = Column(String(10))
    semester = Column(Integer)
    password = Column(String(100))
    # This will store the 128-float array as a string
    face_encoding = Column(Text)
    attendance_records = relationship("Attendance", back_populates="student")