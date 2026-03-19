from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.teacher import Teacher
from ..models.admin import Admin
from ..schemas.teacher_schema import TeacherLogin
from ..security import verify_password, create_access_token

router = APIRouter(prefix="/auth")

@router.post("/teacher-login")
def teacher_login(data: TeacherLogin, db: Session = Depends(get_db)):

  teacher = db.query(Teacher).filter(
      Teacher.email == data.email
  ).first()

  if not teacher:
      return {"status":"teacher not found"}

  if not verify_password(data.password, teacher.password):
      return {"status":"wrong password"}

  token = create_access_token({
      "teacher_id": teacher.id
  })

  return {"token":token}


@router.post("/admin-login")
def admin_login(username: str, password: str, db: Session = Depends(get_db)):

  admin = db.query(Admin).filter(
      Admin.username == username
  ).first()

  if not admin:
      return {"status":"admin not found"}

  if not verify_password(password, admin.password):
      return {"status":"wrong password"}

  token = create_access_token({
      "admin_id": admin.id
  })

  return {"token":token}

