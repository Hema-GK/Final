from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.classroom_polygon import ClassroomPolygon

router = APIRouter(
    prefix="/classroom",
    tags=["Classroom"]
)


@router.get("/polygon/{classroom}")
def get_polygon(classroom: str, db: Session = Depends(get_db)):

    room = db.query(ClassroomPolygon).filter(
        ClassroomPolygon.classroom == classroom
    ).first()

    if not room:
        raise HTTPException(
            status_code=404,
            detail="Classroom polygon not found"
        )

    return {
        "classroom": room.classroom,
        "polygon": room.polygon
    }