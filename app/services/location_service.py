from math import radians, cos, sin, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)

    a = sin(d_lat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c


def is_inside_polygon(lat, lon, polygon):
    inside = False
    j = len(polygon) - 1

    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]

        if ((yi > lon) != (yj > lon)) and \
                (lat < (xj - xi) * (lon - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside

        j = i

    return inside


from app.models.classroom_polygon import ClassroomPolygon

def verify_location(lat, lon, classroom, db):

    # ✅ FIXED: use ORM instead of raw SQL
    room = db.query(ClassroomPolygon).filter(
        ClassroomPolygon.classroom == classroom
    ).first()

    if not room:
        return False, "Polygon not found"

    polygon = room.polygon

    # ✅ inside polygon check
    if not is_inside_polygon(lat, lon, polygon):
        return False, "Outside classroom"

    # ✅ center check (anti-door cheating)
    center_lat = sum(p[0] for p in polygon) / len(polygon)
    center_lon = sum(p[1] for p in polygon) / len(polygon)

    distance = calculate_distance(lat, lon, center_lat, center_lon)

    if distance > 50:   # 🔥 keep bigger for now
        return False, "Move inside classroom"

    return True, "Location verified"