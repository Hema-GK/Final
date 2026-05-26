# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models.marks import Marks
# from app.models.student import Student

# router = APIRouter(prefix="/marks", tags=["Marks"])

# @router.post("/update")
# def update_marks(data:dict,db:Session=Depends(get_db)):

#     student_id = data["student_id"]
#     subject = data["subject"]

#     record = db.query(Marks).filter(
#         Marks.student_id == student_id,
#         Marks.subject == subject
#     ).first()

#     if not record:

#         record = Marks(
#             student_id=student_id,
#             subject=subject,
#             class_name=data["class_name"],
#             section=data["section"]
#         )

#         db.add(record)

#     record.cie1 = data["cie1"]
#     record.cie2 = data["cie2"]
#     record.see_exam = data["see_exam"]

#     db.commit()

#     return {"status":"Marks Updated"}

# @router.get("/class/{class_name}/{section}")
# def get_class_marks(
#     class_name: str,
#     section: str,
#     db: Session = Depends(get_db)
# ):

#     students = db.query(Student).filter(
#         Student.section == section
#     ).all()

#     result = []

#     for student in students:

#         marks = db.query(Marks).filter(
#             Marks.student_id == student.id
#         ).first()

#         result.append({
#             "student_id": student.id,
#             "name": student.name,
#             "usn": student.usn,
#             "cie1": marks.cie1 if marks else 0,
#             "cie2": marks.cie2 if marks else 0,
#             "see_exam": marks.see_exam if marks else 0
#         })

#     return result

# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from app.database import get_db
# from app.models.marks import Marks
# from app.models.student import Student

# router = APIRouter(
#     prefix="/marks",
#     tags=["Marks"]
# )


# # -----------------------------------
# # UPDATE MARKS
# # -----------------------------------

# @router.post("/update")
# def update_marks(
#     data: dict,
#     db: Session = Depends(get_db)
# ):

#     student_id = data["student_id"]
#     subject = data["subject"]

#     record = db.query(Marks).filter(
#         Marks.student_id == student_id,
#         Marks.subject == subject
#     ).first()

#     if not record:

#         record = Marks(
#             student_id=student_id,
#             subject=subject,
#             class_name=data["class_name"],
#             section=data["section"]
#         )

#         db.add(record)

#     record.cie1 = data["cie1"]
#     record.cie2 = data["cie2"]
#     record.see_exam = data["see_exam"]

#     db.commit()

#     return {
#         "status": "success",
#         "message": "Marks Updated"
#     }


# # -----------------------------------
# # GET MARKS FOR SECTION
# # -----------------------------------

# @router.get("/class/{section}")
# def get_class_marks(
#     section: str,
#     db: Session = Depends(get_db)
# ):

#     students = db.query(Student).filter(
#         Student.section == section
#     ).all()

#     result = []

#     for student in students:

#         marks = db.query(Marks).filter(
#             Marks.student_id == student.id
#         ).first()

#         result.append({
#             "student_id": student.id,
#             "name": student.name,
#             "usn": student.usn,
#             "section": student.section,
#             "cie1": marks.cie1 if marks else 0,
#             "cie2": marks.cie2 if marks else 0,
#             "see_exam": marks.see_exam if marks else 0
#         })

#     return result


# # -----------------------------------
# # STUDENT MARKS
# # -----------------------------------

# @router.get("/student/{student_id}")
# def get_student_marks(
#     student_id: int,
#     db: Session = Depends(get_db)
# ):

#     marks = db.query(Marks).filter(
#         Marks.student_id == student_id
#     ).all()

#     return [
#         {
#             "subject": m.subject,
#             "class_name": m.class_name,
#             "section": m.section,
#             "cie1": m.cie1,
#             "cie2": m.cie2,
#             "see_exam": m.see_exam
#         }
#         for m in marks
#     ]


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.marks import Marks
from app.models.student import Student

router = APIRouter(
    prefix="/marks",
    tags=["Marks"]
)
# Note: removed stray JavaScript line 'const semesterNumber = parseInt(semester);'
# which caused a syntax error in this Python module.

# =====================================================
# UPDATE MARKS
# =====================================================

@router.post("/update")
def update_marks(
    data: dict,
    db: Session = Depends(get_db)
):

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

    record.cie1 = int(data.get("cie1", 0))
    record.cie2 = int(data.get("cie2", 0))
    record.see_exam = int(data.get("see_exam", 0))

    db.commit()

    return {
        "status": "success",
        "message": "Marks Updated Successfully"
    }


# =====================================================
# GET STUDENTS OF PARTICULAR SEMESTER + SECTION
# =====================================================


@router.get("/class/{semester}/{section}")

def get_class_marks(
    semester: str,
    section: str,
    db: Session = Depends(get_db)
):

    students = db.query(Student).filter(
    Student.semester == semester,
    Student.section == section
    ).all()

    result = []

    for student in students:

        marks = db.query(Marks).filter(
            Marks.student_id == student.id
        ).first()

        result.append({
            "student_id": student.id,
            "name": student.name,
            "usn": student.usn,
            "semester": student.semester,
            "section": student.section,
            "cie1": marks.cie1 if marks else 0,
            "cie2": marks.cie2 if marks else 0,
            "see_exam": marks.see_exam if marks else 0
        })

    return result


# =====================================================
# GET MARKS OF SINGLE STUDENT
# =====================================================

@router.get("/student/{student_id}")
def get_student_marks(
    student_id: int,
    db: Session = Depends(get_db)
):

    marks = db.query(Marks).filter(
        Marks.student_id == student_id
    ).all()

    return [
        {
            "subject": m.subject,
            "class_name": m.class_name,
            "section": m.section,
            "cie1": m.cie1,
            "cie2": m.cie2,
            "see_exam": m.see_exam
        }
        for m in marks
    ]