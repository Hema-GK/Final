from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine, SessionLocal
from app.services.location_service import check_radius_from_polygon_db
from app.models.classroom_polygon import ClassroomPolygon

# Import all routes
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

# Import models to ensure they are registered with Base
from app.models import (
    student,
    teacher,
    timetable,
    attendance,
    attendance_session,
    classroom_polygon
)

app = FastAPI(title="Smart Attendance System")

# Create tables in Database automatically
Base.metadata.create_all(bind=engine)

# CORS Configuration for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth_routes.router)
app.include_router(student_routes.router)
app.include_router(teacher_routes.router)
app.include_router(admin_routes.router)
app.include_router(attendance_routes.router)
app.include_router(timetable_routes.router)
app.include_router(face_routes.router)
app.include_router(polygon_routes.router)

@app.on_event("startup")
def precalculate_rooms():
    """
    On startup, iterate through all rooms and calculate their 
    mathematical center and radius if not already done.
    """
    print("Startup: Pre-calculating room dimensions...")
    db = SessionLocal()
    try:
        rooms = db.query(ClassroomPolygon).all()
        for room in rooms:
            # We use 0.0, 0.0 as dummy coordinates.
            # The service function will see the center is missing and fix the DB.
            check_radius_from_polygon_db(0.0, 0.0, room.classroom, db)
        print(f"Successfully processed {len(rooms)} classrooms.")
    except Exception as e:
        print(f"Startup Error: {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Attendance System Backend is running!"}