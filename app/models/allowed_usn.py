from sqlalchemy import Column, Integer, String
from app.database import Base

class AllowedUSN(Base):
    __tablename__ = "allowed_usns"

    id = Column(Integer, primary_key=True, index=True)
    usn = Column(String(50), unique=True, index=True, nullable=False)