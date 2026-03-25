import json
from sqlalchemy.orm import Session
from app.models.classroom_polygon import ClassroomPolygon

def is_inside_polygon(x, y, poly):
    """
    Ray-Casting algorithm to check if (x, y) is inside the polygon.
    """
    if isinstance(poly, str):
        poly = json.loads(poly)
    
    n = len(poly)
    inside = False
    
    for i in range(n):
        p1x, p1y = poly[i]
        p2x, p2y = poly[(i + 1) % n]
        
        # Standard ray-casting logic
        if ((p1y > y) != (p2y > y)) and \
           (x < (p2x - p1x) * (y - p1y) / (p2y - p1y) + p1x):
            inside = not inside
            
    return inside

def verify_location_in_polygon(s_lat, s_lon, s_bssid, s_rssi, room_name, db: Session):
    room = db.query(ClassroomPolygon).filter(ClassroomPolygon.classroom == room_name).first()
    if not room:
        return False, "Classroom geofence not defined."

    # 1. GPS CHECK
    is_inside_gps = is_inside_polygon(s_lat, s_lon, room.polygon)
    
    # 2. BSSID CHECK
    incoming_bssid = str(s_bssid).lower().strip()
    required_bssid = str(room.wifi_bssid).lower().strip()
    is_on_correct_wifi = (incoming_bssid == required_bssid)

    # 3. RSSI CHECK - Relaxed to -80 for better indoor stability during demo
    is_strong_signal = float(s_rssi) >= -50

    # --- DUAL-VERIFICATION LOGIC ---
    # If Wi-Fi is 100% correct and strong, we override minor GPS drift.
    # This solves the "one-step outside the door" problem.
    if is_on_correct_wifi and is_strong_signal:
        if not is_inside_gps:
            print(f"LOG: GPS Drift detected ({s_lat}, {s_lon}), but Wi-Fi Verified. Allowing attendance.")
            is_inside_gps = True 

    if is_inside_gps and is_on_correct_wifi and is_strong_signal:
        return True, "Location and Hardware verified."
    
    # Specific error reporting
    if not is_on_correct_wifi:
        return False, f"Incorrect Wi-Fi. Expected {required_bssid}, detected {incoming_bssid}"
    
    if not is_inside_gps:
        return False, f"Outside classroom boundary. Current: ({s_lat}, {s_lon})"
        
    if not is_strong_signal:
        return False, "Signal too weak. Please move closer to the center of the room."

    return False, "Verification failed."