from pydantic import BaseModel


class TeacherRegister(BaseModel):
    name: str
    email: str
    password: str
    class_name: str
    subject: str


class TeacherLogin(BaseModel):
    email: str
    password: str