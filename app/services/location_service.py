# import json
# import pandas as pd
# import os
# import math
# from app.models.classroom_polygon import ClassroomPolygon # Ensure this path is correct
# from sqlalchemy.orm import Session

# # Path to your CSV file on the server
# CSV_PATH = "app/data/room_polygons.csv"

# def get_polygon_center(room_name):
#     """
#     Reads the CSV and returns the (lat, lon) center of the room's polygon.
#     """
#     if not os.path.exists(CSV_PATH):
#         print("Error: room_polygons.csv not found!")
#         return None

#     df = pd.read_csv(CSV_PATH)
    
#     # Filter for the specific room
#     room_data = df[df['room_name'].str.strip().str.lower() == room_name.strip().lower()]
    
#     if room_data.empty:
#         print(f"Room {room_name} not found in CSV")
#         return None

#     # Assuming 'polygon_coords' is stored as a JSON string: "[[lat, lon], [lat, lon]...]"
#     try:
#         coords = json.loads(room_data.iloc[0]['polygon_coords'])
        
#         # Calculate the mathematical center (Centroid)
#         center_lat = sum(p[0] for p in coords) / len(coords)
#         center_lon = sum(p[1] for p in coords) / len(coords)
        
#         return center_lat, center_lon
#     except Exception as e:
#         print(f"Error parsing polygon for {room_name}: {e}")
#         return None

# def check_radius_from_polygon_db(s_lat, s_lon, room_name, db: Session, radius_limit=25):
#     room = db.query(ClassroomPolygon).filter(ClassroomPolygon.classroom == room_name).first()
    
#     # FIX: Provide a clear error if room data is missing
#     if not room or not room.polygon:
#         print(f"Room {room_name} missing from database")
#         return False, "Data Missing" 

#     coords = room.polygon
#     if isinstance(coords, str):
#         try:
#             coords = json.loads(coords)
#         except Exception as e:
#             return False, "Invalid Format"

#     try:
#         # Check if coords list is empty to avoid division by zero
#         if not coords: return False, "No Coords"
        
#         center_lat = sum(float(p[0]) for p in coords) / len(coords)
#         center_lon = sum(float(p[1]) for p in coords) / len(coords)
#     except Exception as e:
#         return False, "Calc Error"

#         # Haversine Formula
#         R = 6371000 
        
#         phi1, phi2 = math.radians(lat1), math.radians(lat2)
#         dphi = math.radians(lat2 - lat1)
#         dlambda = math.radians(lon2 - lon1)

#         # Haversine formula for high-precision distance
#         a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
#         c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
#         distance = R * c

#         # If distance is exactly 0 (same spot), it's still valid
#         return (distance <= radius), float(distance)

import json
from shapely.geometry import Point, Polygon
from app.models.classroom_polygon import ClassroomPolygon
from sqlalchemy.orm import Session

def check_radius_from_polygon_db(s_lat, s_lon, room_name, db: Session):
    """
    Checks if the student's current GPS point is INSIDE the classroom polygon.
    This is much more accurate than a radius check.
    """
    # 1. Fetch room boundary from DB
    room = db.query(ClassroomPolygon).filter(ClassroomPolygon.classroom == room_name).first()
    
    if not room or not room.polygon:
        print(f"Room {room_name} not configured in DB.")
        return False, 0.0

    # 2. Parse the polygon coordinates
    try:
        # Assuming format: [[lat, lon], [lat, lon], ...]
        coords = json.loads(room.polygon) if isinstance(room.polygon, str) else room.polygon
        
        if not coords or len(coords) < 3:
            return False, 0.0

        # Create a Shapely Polygon (Note: Shapely uses (x, y) which is (lon, lat))
        # We must be consistent with the order
        room_polygon = Polygon([(p[1], p[0]) for p in coords])
        student_point = Point(s_lon, s_lat)

        # 3. Check if point is inside
        is_inside = room_polygon.contains(student_point)
        
        # 4. Optional: Calculate distance to center for the error message
        center = room_polygon.centroid
        dist_to_center = student_point.distance(center) * 111320 # Convert degrees to approx meters
        
        return is_inside, round(dist_to_center, 2)

    except Exception as e:
        print(f"Geofencing Error: {e}")
        return False, 0.0