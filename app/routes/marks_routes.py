from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.marks import Marks

router = APIRouter(prefix="/marks", tags=["Marks"])

@router.post("/update")
def update_marks(data:dict,db:Session=Depends(get_db)):

    student_id = data["student_id"]
    subject = data["subject"]

    record = db.query(Marks).filter(
        Marks.student_id == student_id,
        Marks.subject == subject
    ).first()

    if not record:

        record = Marks(
            student_id=student_id,
            subject=subject,
            class_name=data["class_name"],
            section=data["section"]
        )

        db.add(record)

    record.cie1 = data["cie1"]
    record.cie2 = data["cie2"]
    record.see_exam = data["see_exam"]

    db.commit()

    return {"status":"Marks Updated"}