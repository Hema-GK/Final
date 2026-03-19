import pandas as pd
import json
import os
import math
from app.models.classroom_polygon import ClassroomPolygon # Ensure this path is correct
from sqlalchemy.orm import Session

# Path to your CSV file on the server
CSV_PATH = "app/data/room_polygons.csv"

def get_polygon_center(room_name):
    """
    Reads the CSV and returns the (lat, lon) center of the room's polygon.
    """
    if not os.path.exists(CSV_PATH):
        print("Error: room_polygons.csv not found!")
        return None

    df = pd.read_csv(CSV_PATH)
    
    # Filter for the specific room
    room_data = df[df['room_name'].str.strip().str.lower() == room_name.strip().lower()]
    
    if room_data.empty:
        print(f"Room {room_name} not found in CSV")
        return None

    # Assuming 'polygon_coords' is stored as a JSON string: "[[lat, lon], [lat, lon]...]"
    try:
        coords = json.loads(room_data.iloc[0]['polygon_coords'])
        
        # Calculate the mathematical center (Centroid)
        center_lat = sum(p[0] for p in coords) / len(coords)
        center_lon = sum(p[1] for p in coords) / len(coords)
        
        return center_lat, center_lon
    except Exception as e:
        print(f"Error parsing polygon for {room_name}: {e}")
        return None

def check_radius_from_polygon_db(s_lat, s_lon, room_name, db: Session, radius_limit=25):
    room = db.query(ClassroomPolygon).filter(ClassroomPolygon.classroom == room_name).first()
    
    if not room or not room.polygon:
        return False, 0 # Return 0 if room not found

    coords = room.polygon 
    center_lat = sum(float(p[0]) for p in coords) / len(coords)
    center_lon = sum(float(p[1]) for p in coords) / len(coords)

    R = 6371000 
    phi1, phi2 = math.radians(s_lat), math.radians(center_lat)
    dphi = math.radians(center_lat - s_lat)
    dlambda = math.radians(center_lon - s_lon)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c

    # Returns a tuple: (Is inside?, Actual Distance in meters)
    return (distance <= radius_limit), round(distance, 2)