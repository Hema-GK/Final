from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import face_routes
from app.models import attendance_session
from app.routes import (
    auth_routes,
    student_routes,
    teacher_routes,
    admin_routes,
    face_routes,
    attendance_routes,
    timetable_routes,
    polygon_routes
)
from app.models import (
    student,
    teacher,
    timetable,
    attendance,
    attendance_session
)

from app.models.classroom_polygon import ClassroomPolygon



app = FastAPI(title="Smart Attendance System")

# Create tables
Base.metadata.create_all(bind=engine)

# CORS (IMPORTANT for React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_routes.router)
app.include_router(student_routes.router)
app.include_router(teacher_routes.router)
app.include_router(admin_routes.router)
app.include_router(attendance_routes.router)
app.include_router(timetable_routes.router)
app.include_router(face_routes.router)
app.include_router(polygon_routes.router)


