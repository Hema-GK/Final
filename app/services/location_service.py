import json
from sqlalchemy.orm import Session
from app.models.classroom_polygon import ClassroomPolygon
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))


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


def verify_location_in_polygon(lat, lon, ssid, rssi, room_name, db: Session):

    room = db.query(ClassroomPolygon).filter(
        ClassroomPolygon.classroom == room_name
    ).first()

    if not room:
        return False, "Classroom not configured"

    polygon = room.polygon

    # -------------------------
    # GPS CHECK (PRIMARY)
    # -------------------------
    inside = is_inside_polygon(lat, lon, polygon)

    # -------------------------
    # DISTANCE CHECK (NEW 🔥)
    # Helps near-door accuracy
    # -------------------------
    center_lat, center_lon = json.loads(polygon)[0]

    distance = haversine_distance(lat, lon, center_lat, center_lon)

    near_room = distance < 40  # meters tolerance

    # -------------------------
    # SSID CHECK (OPTIONAL)
    # -------------------------
    expected_ssid = "College_Wifi_Test"

    ssid_ok = (ssid == expected_ssid)

    # -------------------------
    # SIGNAL CHECK
    # -------------------------
    signal_ok = float(rssi) >= -70

    # -------------------------
    # FINAL DECISION
    # -------------------------
    if inside or near_room:
        if signal_ok:
            return True, "Location verified"

    return False, f"Outside classroom (distance: {int(distance)}m)"