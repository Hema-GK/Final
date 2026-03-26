import json
import math
from sqlalchemy.orm import Session
from app.models.classroom_polygon import ClassroomPolygon


def is_inside_polygon(x, y, poly):
    if isinstance(poly, str):
        poly = json.loads(poly)

    n = len(poly)
    inside = False

    for i in range(n):
        p1x, p1y = poly[i]
        p2x, p2y = poly[(i + 1) % n]

        if ((p1y > y) != (p2y > y)) and \
           (x < (p2x - p1x) * (y - p1y) / (p2y - p1y + 1e-9) + p1x):
            inside = not inside

    return inside


# 🔥 Distance function (for edge cases)
def distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111000  # meters

def verify_location_and_beacon(lat, lon, beacon_uuid, rssi, room_name, db):

    room = db.query(ClassroomPolygon).filter(
        ClassroomPolygon.classroom == room_name
    ).first()

    if not room:
        return False, "Classroom not configured"

    # 📍 GPS
    inside = is_inside_polygon(lat, lon, room.polygon)

    if not inside:
        return False, "Outside classroom"

    # 📡 UUID match
    if beacon_uuid != room.beacon_uuid:
        return False, "Wrong classroom beacon"

    # 🔥 RSSI check
    if rssi is None or rssi < -70:
        return False, "Too far from classroom (weak signal)"

    return True, "Verified"