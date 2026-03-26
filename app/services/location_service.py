import math
from app.models.classroom_polygon import ClassroomPolygon


# 🔥 Point in Polygon (Ray Casting)
def is_inside_polygon(lat, lon, polygon):
    x = lat
    y = lon

    inside = False
    n = len(polygon)

    p1x, p1y = polygon[0]

    for i in range(n + 1):
        p2x, p2y = polygon[i % n]

        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x

                    if p1x == p2x or x <= xinters:
                        inside = not inside

        p1x, p1y = p2x, p2y

    return inside


# 🔥 Main Verification (STRICT MODE)
def verify_location(lat, lon, classroom, db):

    room = db.query(ClassroomPolygon).filter(
        ClassroomPolygon.classroom == classroom
    ).first()

    if not room:
        return False, "Polygon not found"

    polygon = room.polygon

    # 🔥 ONLY boundary check (NO distance)
    if not is_inside_polygon(lat, lon, polygon):
        return False, "❌ You are outside classroom"

    return True, "✅ Inside classroom"