from pydantic import BaseModel

class AttendanceRequest(BaseModel):


  image: str

  latitude: float

  longitude: float

