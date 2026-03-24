# import math
# import json
# from app.models.classroom_polygon import ClassroomPolygon
# from sqlalchemy.orm import Session

# def calculate_haversine(lat1, lon1, lat2, lon2):
#     """Calculates distance between two points in meters."""
#     R = 6371000 
#     phi1, phi2 = math.radians(lat1), math.radians(lat2)
#     dphi = math.radians(lat2 - lat1)
#     dlambda = math.radians(lon2 - lon1)
#     a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
#     return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# def check_radius_from_polygon_db(s_lat, s_lon, room_name, db: Session):
#     try:
#         # 1. Fetch the room record
#         room = db.query(ClassroomPolygon).filter(ClassroomPolygon.classroom == room_name).first()
        
#         if not room or not room.polygon:
#             return False, 0.0

#         # 2. AUTOMATIC DETECTION: If dimensions are missing, calculate and SAVE them immediately
#         if room.center_lat is None or room.calculated_radius is None:
#             # Handle both string and list formats for the polygon data
#             raw_poly = room.polygon
#             if isinstance(raw_poly, str):
#                 # Cleans common CSV formatting issues before parsing
#                 raw_poly = raw_poly.replace("'", '"') 
#                 coords = json.loads(raw_poly)
#             else:
#                 coords = raw_poly

#             # Calculate mathematical center (Centroid)
#             c_lat = sum(float(p[0]) for p in coords) / len(coords)
#             c_lon = sum(float(p[1]) for p in coords) / len(coords)
            
#             # Find furthest corner + 5m buffer for the "Perfect Radius"
#             max_dist = max([calculate_haversine(c_lat, c_lon, float(p[0]), float(p[1])) for p in coords])
#             rec_radius = max_dist + 6.5
#             # UPDATE DATABASE PERMANENTLY
#             room.center_lat = c_lat
#             room.center_lon = c_lon
#             room.calculated_radius = rec_radius
#             db.commit() # This pushes the [null] to actual numbers
#             db.refresh(room)
            
#             print(f"AUTO-CALC SUCCESS: {room_name} is now centered at {c_lat}, {c_lon}")
#         else:
#             # Values already exist, just use them
#             c_lat = room.center_lat
#             c_lon = room.center_lon
#             rec_radius = room.calculated_radius

#         # 3. If this is a 'startup' check with 0,0 coords, return early
#         if s_lat == 0.0 and s_lon == 0.0:
#             return True, 0.0

#         # 4. FINAL DISTANCE CHECK
#         actual_distance = calculate_haversine(c_lat, c_lon, s_lat, s_lon)
#         is_inside = actual_distance <= rec_radius
        
#         return is_inside, round(float(actual_distance), 2)

#     except Exception as e:
#         db.rollback()
#         print(f"Auto-Calc Critical Error: {e}")
#         return False, 0.0
import json
import math
from sqlalchemy.orm import Session
from app.models.classroom_polygon import ClassroomPolygon

def is_inside_polygon(x, y, poly):
    """
    Standard Ray-Casting algorithm. 
    IMPORTANT: x should be Latitude, y should be Longitude (or vice versa), 
    as long as it is consistent with your DB format.
    """
    if isinstance(poly, str):
        poly = json.loads(poly)
    
    n = len(poly)
    inside = False
    
    # Correcting the loop to prevent index out of bounds
    for i in range(n):
        p1x, p1y = poly[i]
        p2x, p2y = poly[(i + 1) % n]
        
        if ((p1y > y) != (p2y > y)) and \
           (x < (p2x - p1x) * (y - p1y) / (p2y - p1y) + p1x):
            inside = not inside
            
    return inside

def verify_location_in_polygon(s_lat, s_lon, s_bssid, s_rssi, room_name, db: Session):
    room = db.query(ClassroomPolygon).filter(ClassroomPolygon.classroom == room_name).first()
    if not room:
        return False, "Classroom geofence not defined."

    # 1. STRICT GPS CHECK
    is_inside_gps = is_inside_polygon(s_lat, s_lon, room.polygon)
    
    # 2. STRICT BSSID CHECK (No placeholders allowed)
    incoming_bssid = str(s_bssid).lower().strip()
    required_bssid = str(room.wifi_bssid).lower().strip()
    
    is_on_correct_wifi = (incoming_bssid == required_bssid)

    # 3. RSSI CHECK
    is_strong_signal = float(s_rssi) >= -70

    # BOTH MUST BE TRUE
    if is_inside_gps and is_on_correct_wifi and is_strong_signal:
        return True, "Location and Hardware verified."
    
    # Specific error reporting for debugging
    if not is_on_correct_wifi:
        return False, f"Incorrect Wi-Fi. Expected {required_bssid}, detected {incoming_bssid}"
    
    if not is_inside_gps:
        return False, f"Outside classroom boundary. Current: ({s_lat}, {s_lon})"
        
    if not is_strong_signal:
        return False, "Signal too weak. Please step further into the classroom."

    return False, "Verification failed."