from shapely.geometry import Point, Polygon
from app.models.classroom_polygon import ClassroomPolygon

def verify_location(lat, lon, classroom, db):
    room = db.query(ClassroomPolygon).filter(
        ClassroomPolygon.classroom == classroom
    ).first()

    if not room:
        return False, "Polygon not found"

    try:
        # Your coordinates from DB: [[lat, lon], [lat, lon]...]
        poly_coords = room.polygon
        classroom_poly = Polygon(poly_coords)
        student_point = Point(lat, lon)
    except Exception as e:
        return False, f"Geometry error: {str(e)}"

    # ✅ INCREASED BUFFER
    # 0.0001 degrees is roughly 10 meters. 
    # This ensures that even with indoor GPS interference, you are verified.
    attendance_zone = classroom_poly.buffer(0.00016)
    
    if attendance_zone.contains(student_point):
        return True, "Location verified"

    return False, "📍 Move slightly inside classroom and try again"