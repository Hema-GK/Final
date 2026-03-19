from pydantic import BaseModel

class TimetableUpload(BaseModel):

  semester: str

