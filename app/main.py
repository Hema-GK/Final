# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.database import Base, engine

# # This now matches the function name in your location_service.py
# from app.services.location_service import verify_location

# # Import all routes
# from app.routes import (
#     auth_routes,
#     student_routes,
#     teacher_routes,
#     admin_routes,
#     face_routes,
#     attendance_routes,
#     timetable_routes,
#     polygon_routes
# )

# # Import models to ensure they are registered with Base
# from app.models import (
#     student,
#     teacher,
#     timetable,
#     attendance,
#     attendance_session,
#     classroom_polygon
# )

# app = FastAPI(title="Smart Attendance System")

# # Create tables in Database automatically 
# # Note: Railway/Vercel will use the DATABASE_URL from your env
# Base.metadata.create_all(bind=engine)

# # CORS Configuration
# # "allow_origins=['*']" is fine for development/testing
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], 
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Register Routers
# app.include_router(auth_routes.router)
# app.include_router(student_routes.router)
# app.include_router(teacher_routes.router)
# app.include_router(admin_routes.router)
# app.include_router(attendance_routes.router)
# app.include_router(timetable_routes.router)
# app.include_router(face_routes.router)
# app.include_router(polygon_routes.router)

# @app.on_event("startup")
# def startup_event():
#     """
#     Called when the server starts on Railway.
#     """
#     print("Startup: Smart Attendance Backend is ready.")

# @app.get("/")
# def root():
#     """
#     Health check endpoint.
#     """
#     return {
#         "status": "online",
#         "message": "Smart Attendance System Backend is running!"
#     }


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine

# This now matches the function name in your location_service.py
from app.services.location_service import verify_location

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
# Note: Railway/Vercel will use the DATABASE_URL from your env
Base.metadata.create_all(bind=engine)

# CORS Configuration - REMOVED trailing slashes to prevent browser CORS blocks
# origins = [
#     "https://smart-attendance-frontend-nu.vercel.app",
#     "https://smart-attendance-frontend-ocr98rx6f-hema-gks-projects.vercel.app",
#     "http://localhost:5173"  # for local testing
# ]
origins = [
    "https://smart-attendance-frontend-sigma.vercel.app",
    "https://smart-attendance-frontend-nu.vercel.app",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers with specific prefixes to match your frontend paths
app.include_router(auth_routes.router)
app.include_router(student_routes.router)
app.include_router(teacher_routes.router)
app.include_router(admin_routes.router)
app.include_router(attendance_routes.router)
app.include_router(timetable_routes.router, prefix="/timetable")  # Added prefix here!
app.include_router(face_routes.router)
app.include_router(polygon_routes.router)

@app.on_event("startup")
def startup_event():
    """
    Called when the server starts on Railway.
    """
    print("Startup: Smart Attendance Backend is ready.")

@app.get("/")
def root():
    """
    Health check endpoint.
    """
    return {
        "status": "online",
        "message": "Smart Attendance System Backend is running!"
    }