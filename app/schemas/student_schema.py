# from pydantic import BaseModel


# class StudentRegister(BaseModel):

#     name: str
#     usn: str
#     password: str
#     class_name: str
#     section: str
#     image: str

from pydantic import BaseModel


class StudentRegister(BaseModel):

    name: str
    usn: str
    password: str
    class_name: str
    section: str
    image: str


class StudentLogin(BaseModel):

    usn: str
    password: str