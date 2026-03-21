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
from shapely.geometry import Point, Polygon
from app.models.classroom_polygon import ClassroomPolygon
from sqlalchemy.orm import Session

def check_radius_from_polygon_db(s_lat, s_lon, room_name, db: Session):
    """
    Checks if student is inside the classroom polygon PLUS a 10m buffer.
    """
    room = db.query(ClassroomPolygon).filter(ClassroomPolygon.classroom == room_name).first()
    
    if not room or not room.polygon:
        return False, 0.0

    try:
        # 1. Parse coordinates
        coords = json.loads(room.polygon) if isinstance(room.polygon, str) else room.polygon
        
        # 2. Create Polygon (Lon, Lat)
        # We must use (Lon, Lat) for Shapely geometry
        raw_poly = Polygon([(p[1], p[0]) for p in coords])
        
        # 3. Apply a 10-meter BUFFER to account for GPS drift seen in your images
        # 0.0001 degrees is roughly 11 meters
        buffered_poly = raw_poly.buffer(0.00009) 
        
        student_location = Point(s_lon, s_lat)

        # 4. Check containment in the BUFFERED zone
        is_inside = buffered_poly.contains(student_location)
        
        # 5. Calculate distance to actual center for UI feedback
        center = raw_poly.centroid
        # Degrees to meters conversion
        dist = student_location.distance(center) * 111320 
        
        return is_inside, round(dist, 2)

    except Exception as e:
        print(f"Geofence Error: {e}")
        return False, 0.0