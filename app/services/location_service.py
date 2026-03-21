# import json
# from shapely.geometry import Point, Polygon
# from app.models.classroom_polygon import ClassroomPolygon
# from sqlalchemy.orm import Session

# def check_radius_from_polygon_db(s_lat, s_lon, room_name, db: Session):
#     """
#     Checks if the student's current GPS point is INSIDE the classroom polygon.
#     This is much more accurate than a radius check.
#     """
#     # 1. Fetch room boundary from DB
#     room = db.query(ClassroomPolygon).filter(ClassroomPolygon.classroom == room_name).first()
    
#     if not room or not room.polygon:
#         print(f"Room {room_name} not configured in DB.")
#         return False, 0.0

#     # 2. Parse the polygon coordinates
#     try:
#         # Assuming format: [[lat, lon], [lat, lon], ...]
#         coords = json.loads(room.polygon) if isinstance(room.polygon, str) else room.polygon
        
#         if not coords or len(coords) < 3:
#             return False, 0.0

#         # Create a Shapely Polygon (Note: Shapely uses (x, y) which is (lon, lat))
#         # We must be consistent with the order
#         room_polygon = Polygon([(p[1], p[0]) for p in coords])
#         student_point = Point(s_lon, s_lat)

#         # 3. Check if point is inside
#         is_inside = room_polygon.contains(student_point)
        
#         # 4. Optional: Calculate distance to center for the error message
#         center = room_polygon.centroid
#         dist_to_center = student_point.distance(center) * 111320 # Convert degrees to approx meters
        
#         return is_inside, round(dist_to_center, 2)

#     except Exception as e:
#         print(f"Geofencing Error: {e}")
#         return False, 0.0

import json
import math
from shapely.geometry import Point, Polygon
from app.models.classroom_polygon import ClassroomPolygon
from sqlalchemy.orm import Session

def check_radius_from_polygon_db(s_lat, s_lon, room_name, db: Session):
    """
    Checks if student is inside the classroom polygon boundary.
    Fixed to prevent 'unverified distance' errors.
    """
    room = db.query(ClassroomPolygon).filter(ClassroomPolygon.classroom == room_name).first()
    
    if not room or not room.polygon:
        print(f"Room {room_name} not found or polygon is empty.")
        return False, 0.0

    try:
        # 1. Parse coordinates from DB
        coords = json.loads(room.polygon) if isinstance(room.polygon, str) else room.polygon
        
        if not coords or len(coords) < 3:
            return False, 0.0

        # 2. IMPORTANT: Shapely uses (x, y) which is (Longitude, Latitude)
        # Your DB likely stores [Lat, Lon], so we MUST swap them here.
        polygon_points = [(p[1], p[0]) for p in coords]
        room_poly = Polygon(polygon_points)
        
        # 3. Add a 10m buffer (approx 0.00009 degrees) to prevent drift errors
        buffered_poly = room_poly.buffer(0.00009)
        
        student_point = Point(s_lon, s_lat)

        # 4. Verification check
        is_inside = buffered_poly.contains(student_point)
        
        # 5. Calculate real distance for the error message
        # We use a solid centroid to ensure 'dist' is never 'unknown'
        center = room_poly.centroid
        # Basic degree to meter conversion (1 degree ~ 111,320 meters)
        dist = student_point.distance(center) * 111320
        
        return is_inside, round(float(dist), 2)

    except Exception as e:
        print(f"Logic Error: {e}")
        # Return a safe float 0.0 to prevent 'unverified' string errors
        return False, 0.0