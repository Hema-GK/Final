import math
import json
from app.models.classroom_polygon import ClassroomPolygon
from sqlalchemy.orm import Session

def calculate_haversine(lat1, lon1, lat2, lon2):
    """
    Calculates the great-circle distance between two points 
    on the Earth in METERS.
    """
    R = 6371000  # Radius of Earth in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def check_radius_from_polygon_db(s_lat, s_lon, room_name, db: Session):
    """
    Checks if student is inside the classroom.
    Automatically calculates room center and custom radius if they don't exist.
    """
    try:
        # 1. Fetch Room Data
        room = db.query(ClassroomPolygon).filter(ClassroomPolygon.classroom == room_name).first()
        
        if not room or not room.polygon:
            print(f"Room {room_name} not found or has no polygon data.")
            return False, 0.0

        # 2. AUTOMATION: Calculate dimensions if they are missing from DB
        if not room.center_lat or not room.calculated_radius:
            print(f"--- Automating dimensions for {room_name} ---")
            
            # Parse corners from JSON string
            coords = json.loads(room.polygon) if isinstance(room.polygon, str) else room.polygon
            
            if not coords or len(coords) < 3:
                print(f"Invalid polygon data for {room_name}.")
                return False, 0.0

            # Find Mathematical Center (Average of all corners)
            c_lat = sum(float(p[0]) for p in coords) / len(coords)
            c_lon = sum(float(p[1]) for p in coords) / len(coords)
            
            # Find the distance to the furthest corner to set the radius
            # This makes the radius 'adaptive' to the room size
            max_d = max([calculate_haversine(c_lat, c_lon, float(p[0]), float(p[1])) for p in coords])
            
            # Add 5-meter buffer to handle indoor GPS drift (16m-19m range)
            rec_radius = max_d + 5.0 
            
            # Update the record so we don't do this math every single time
            room.center_lat = c_lat
            room.center_lon = c_lon
            room.calculated_radius = rec_radius
            db.commit()
            
            print(f"Saved: Center({c_lat}, {c_lon}), Radius: {rec_radius}m")
        else:
            # Use pre-existing automated values
            c_lat = room.center_lat
            c_lon = room.center_lon
            rec_radius = room.calculated_radius

        # 3. VERIFICATION: Compare student location to calculated center
        # If dummy coords (0,0) are sent from startup, skip the distance check
        if s_lat == 0.0 and s_lon == 0.0:
            return True, 0.0

        actual_distance = calculate_haversine(c_lat, c_lon, s_lat, s_lon)
        is_inside = actual_distance <= rec_radius
        
        return is_inside, round(float(actual_distance), 2)

    except Exception as e:
        print(f"Location Service Error: {e}")
        db.rollback()
        return False, 0.0