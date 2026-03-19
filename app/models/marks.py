from sqlalchemy import Column,Integer,String,ForeignKey
from app.database import Base

class Marks(Base):

    __tablename__ = "marks"

    id = Column(Integer,primary_key=True,index=True)

    student_id = Column(Integer,ForeignKey("students.id"))

    subject = Column(String(100))
    class_name = Column(String(20))
    section = Column(String(10))

    cie1 = Column(Integer,default=0)
    cie2 = Column(Integer,default=0)
    see_exam = Column(Integer,default=0)