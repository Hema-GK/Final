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


def verify_location(lat, lon, classroom, db):

    classroom_data = db.execute(
        f"SELECT polygon FROM classroom_polygons WHERE classroom = '{classroom}'"
    ).fetchone()

    if not classroom_data:
        return False, "Polygon not found"

    polygon = classroom_data[0]

    # ✅ inside check
    if not is_inside_polygon(lat, lon, polygon):
        return False, "Outside classroom"

    # ✅ center check (ANTI DOOR CHEATING)
    center_lat = sum(p[0] for p in polygon) / len(polygon)
    center_lon = sum(p[1] for p in polygon) / len(polygon)

    distance = calculate_distance(lat, lon, center_lat, center_lon)

    if distance > 20:
        return False, "Move inside classroom"

    return True, "Verified"