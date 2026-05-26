# from shapely.geometry import Point, Polygon
# from app.models.classroom_polygon import ClassroomPolygon

# def verify_location(lat, lon, classroom, db):
#     room = db.query(ClassroomPolygon).filter(
#         ClassroomPolygon.classroom == classroom
#     ).first()

#     if not room:
#         return False, "Polygon not found"

#     try:
#         # Your coordinates from DB: [[lat, lon], [lat, lon]...]
#         poly_coords = room.polygon
#         classroom_poly = Polygon(poly_coords)
#         student_point = Point(lat, lon)
#     except Exception as e:
#         return False, f"Geometry error: {str(e)}"

#     # ✅ INCREASED BUFFER
#     # 0.0001 degrees is roughly 10 meters. 
#     # This ensures that even with indoor GPS interference, you are verified.
#     attendance_zone = classroom_poly.buffer(0.00016)
    
#     if attendance_zone.contains(student_point):
#         return True, "Location verified"

#     return False, "📍 Move slightly inside classroom and try again"

from shapely.geometry import Point, Polygon
from app.models.classroom_polygon import ClassroomPolygon
import json


def verify_location(
    lat,
    lon,
    classroom,
    db
):
    room = (
        db.query(ClassroomPolygon)
        .filter(
            ClassroomPolygon.classroom
            == classroom
        )
        .first()
    )

    if not room:
        return False, "Polygon not found"

    try:

        poly_coords = room.polygon

        if isinstance(
            poly_coords,
            str
        ):
            poly_coords = json.loads(
                poly_coords
            )

        polygon_points = [
            (
                float(lon_val),
                float(lat_val)
            )
            for lat_val, lon_val
            in poly_coords
        ]

        classroom_poly = Polygon(
            polygon_points
        )

        student_point = Point(
            float(lon),
            float(lat)
        )

        print(
            "CLASSROOM:",
            classroom
        )

        print(
            "POLYGON:",
            polygon_points
        )

        print(
            "STUDENT:",
            (
                float(lon),
                float(lat)
            )
        )

        print(
            "POLYGON BOUNDS:",
            classroom_poly.bounds
        )

    except Exception as e:

        print(
            "LOCATION ERROR:",
            str(e)
        )

        return (
            False,
            f"Geometry error: {str(e)}"
        )

    # GPS tolerance
    attendance_zone = (
        classroom_poly.buffer(
            0.00005
        )
    )

    inside = attendance_zone.contains(
        student_point
    )

    print(
        "INSIDE CLASSROOM:",
        inside
    )

    print(
        "DISTANCE FROM POLYGON:",
        classroom_poly.distance(
            student_point
        )
    )

    if inside:
        return (
            True,
            "Location verified"
        )

    return (
        False,
        "📍 Outside classroom boundary"
    )