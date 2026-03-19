from sqlalchemy import Column, Integer, String
from ..database import Base

class Admin(Base):

  __tablename__ = "admins"

  id = Column(Integer, primary_key=True, index=True)

  username = Column(String(100), unique=True)

  password = Column(String(200))

