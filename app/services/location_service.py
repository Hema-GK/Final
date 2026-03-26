import math
from app.models.classroom_polygon import ClassroomPolygon

# 🔥 Point in Polygon (Ray Casting)
def is_inside_polygon(lat, lon, polygon):
    x, y = lat, lon
    inside = False
    n = len(polygon)
    p1x, p1y = polygon[0]

    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y) and y <= max(p1y, p2y):
            if x <= max(p1x, p2x):
                if p1y != p2y:
                    xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or x <= xinters:
                    inside = not inside
        p1x, p1y = p2x, p2y
    return inside

# 🔥 Distance calculation from Point to Wall (Line Segment)
def point_to_line_distance(py, px, y1, x1, y2, x2):
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.sqrt((px - x1)**2 + (py - y1)**2)
    
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t)) # Clamp to segment
    
    nearest_x = x1 + t * dx
    nearest_y = y1 + t * dy
    return math.sqrt((px - nearest_x)**2 + (py - nearest_y)**2)

# 🔥 Boundary Proximity Check
def is_near_polygon(lat, lon, polygon, threshold_degrees):
    for i in range(len(polygon)):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]
        # p1[0] is lat, p1[1] is lon per your DB structure
        distance = point_to_line_distance(lat, lon, p1[0], p1[1], p2[0], p2[1])
        if distance <= threshold_degrees:
            return True
    return False

# 🔥 Main Verification Service
def verify_location(lat, lon, classroom, db):
    room = db.query(ClassroomPolygon).filter(ClassroomPolygon.classroom == classroom).first()
    if not room:
        return False, "Polygon not found"

    polygon = room.polygon # List of [lat, lon] pairs from DB

    # 1. Strict check
    if is_inside_polygon(lat, lon, polygon):
        return True, "Location verified"

    # 2. 3-meter buffer (0.00003 degrees) for edge cases/doorways
    if is_near_polygon(lat, lon, polygon, threshold_degrees=0.00003):
        return True, "Location verified (Edge)"

    # 3. Beyond 3 meters
    return False, "📍 Move slightly inside classroom and try again"