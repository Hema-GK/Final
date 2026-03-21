# from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Time
# from app.database import Base

# class Timetable(Base):
#     __tablename__ = "timetable"

#     id = Column(Integer, primary_key=True, index=True)
#     semester = Column(String(50))
#     section = Column(String(20))
#     day = Column(String(20))
    
#     # Using Time object to match your pgAdmin 'time without time zone'
#     start_time = Column(Time)
#     end_time = Column(Time)

#     subject = Column(String(100))
#     teacher_id = Column(Integer, ForeignKey("teachers.id"))
#     teacher_name = Column(String(100))
#     classroom = Column(String(100))
#     is_lunch = Column(Boolean, default=False)

# from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Time
# from sqlalchemy.orm import relationship
# from app.database import Base

# class Timetable(Base):
#     __tablename__ = "timetable"

#     id = Column(Integer, primary_key=True, index=True)
#     semester = Column(String(50))
#     section = Column(String(20))
#     day = Column(String(20))
    
#     start_time = Column(Time)
#     end_time = Column(Time)

#     subject = Column(String(100))
#     teacher_id = Column(Integer, ForeignKey("teachers.id")) # Correctly references the teachers table
    
#     # IMPROVEMENT: Add this relationship line
#     teacher = relationship("Teacher", back_populates="timetables")
    
#     teacher_name = Column(String(100))
#     classroom = Column(String(100))
#     is_lunch = Column(Boolean, default=False)


from sqlalchemy import Column, Integer, String, ForeignKey, Time,Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Timetable(Base):
    __tablename__ = "timetable"

    id = Column(Integer, primary_key=True, index=True)
    semester = Column(String(50))
    section = Column(String(20))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    subject = Column(String(100))
 # This matches 'classroom' in ClassroomPolygon
    day = Column(String(20))
    start_time = Column(Time)
    end_time = Column(Time)
    teacher = relationship("Teacher", back_populates="timetables")
    teacher_name = Column(String(100))
    classroom = Column(String(100))
    is_lunch = Column(Boolean, default=False)

    # Relationship to Attendance
    attendance_records = relationship("Attendance", back_populates="timetable")