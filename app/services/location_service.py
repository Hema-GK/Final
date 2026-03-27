from shapely.geometry import Point, Polygon
from app.models.classroom_polygon import ClassroomPolygon

def verify_location(lat, lon, classroom, db):
    """
    Verifies if a user is within the classroom or a 3-meter buffer using Shapely.
    """
    room = db.query(ClassroomPolygon).filter(
        ClassroomPolygon.classroom == classroom
    ).first()

    if not room:
        return False, "Polygon not found"

    # room.polygon is a list of [lat, lon] pairs from your DB
    try:
        poly_coords = room.polygon
        classroom_poly = Polygon(poly_coords)
        student_point = Point(lat, lon)
    except Exception as e:
        return False, f"Geometry error: {str(e)}"

    # ✅ 1. Check if strictly inside or on the boundary line
    # .contains() and .touches() replace your manual Ray Casting code
    if classroom_poly.contains(student_point) or classroom_poly.touches(student_point):
        return True, "Location verified"

    # ✅ 2. Check within a 3-meter buffer zone (0.00003 degrees)
    # .buffer() replaces your manual distance and is_near_polygon code
    buffered_poly = classroom_poly.buffer(0.00003)
    
    if buffered_poly.contains(student_point):
        return True, "Location verified"

    # 3. Rejection: If more than ~3 meters away
    return False, "📍 Move slightly inside classroom and try again"