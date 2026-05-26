# from shapely.geometry import Point, Polygon
# from app.models.classroom_polygon import ClassroomPolygon

# def verify_location(lat, lon, classroom, db):
#     room = db.query(ClassroomPolygon).filter(
#         ClassroomPolygon.classroom == classroom
#     ).first()

#     if not room:
#         return False, "Polygon not found"

#     try:
#         # Your coordinates from DB: [[lat, lon], [lat, lon]...]
#         poly_coords = room.polygon
#         classroom_poly = Polygon(poly_coords)
#         student_point = Point(lat, lon)
#     except Exception as e:
#         return False, f"Geometry error: {str(e)}"

#     # ✅ INCREASED BUFFER
#     # 0.0001 degrees is roughly 10 meters. 
#     # This ensures that even with indoor GPS interference, you are verified.
#     attendance_zone = classroom_poly.buffer(0.00016)
    
#     if attendance_zone.contains(student_point):
#         return True, "Location verified"

#     return False, "📍 Move slightly inside classroom and try again"

from shapely.geometry import Point, Polygon
from app.models.classroom_polygon import ClassroomPolygon
import json


def verify_location(lat, lon, classroom, db):
    room = db.query(ClassroomPolygon).filter(
        ClassroomPolygon.classroom == classroom
    ).first()

    if not room:
        return False, "Polygon not found"

    try:
        poly_coords = room.polygon

        # Safety check in case polygon is accidentally stored as a string
        if isinstance(poly_coords, str):
            poly_coords = json.loads(poly_coords)

        print("CLASSROOM:", classroom)
        print("POLYGON:", poly_coords)
        print("LAT:", lat)
        print("LON:", lon)

        # Create polygon
        classroom_poly = Polygon(poly_coords)

        # Create student location point
        student_point = Point(
            float(lat),
            float(lon)
        )

    except Exception as e:
        print("LOCATION ERROR:", str(e))
        return False, f"Geometry error: {str(e)}"

    # Allow some GPS tolerance (~15-20 meters)
    attendance_zone = classroom_poly.buffer(0.00016)

    print("INSIDE:", attendance_zone.contains(student_point))

    if attendance_zone.contains(student_point):
        return True, "Location verified"

    return False, "📍 Move slightly inside classroom and try again"