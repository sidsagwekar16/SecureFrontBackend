# utils.py
from fastapi import HTTPException, Header
from firebase_admin import auth
from shapely.geometry import Point, Polygon

def is_inside_geofence(user_lat: float, user_lng: float, polygon_coords: list) -> bool:
    polygon_points = [(p["lng"], p["lat"]) for p in polygon_coords]
    polygon = Polygon(polygon_points)
    point = Point(user_lng, user_lat)
    return polygon.contains(point)

def validate_geofence_coordinates(coordinates: list) -> None:
    if len(coordinates) < 3:
        raise HTTPException(status_code=400, detail="Geofence must have at least 3 coordinates to form a polygon")
    for coord in coordinates:
        if "lat" not in coord or "lng" not in coord:
            raise HTTPException(status_code=400, detail="Each coordinate must have 'lat' and 'lng' fields")
        if not isinstance(coord["lat"], (int, float)) or not isinstance(coord["lng"], (int, float)):
            raise HTTPException(status_code=400, detail="Coordinates 'lat' and 'lng' must be numbers")
    try:
        Polygon([(p["lat"], p["lng"]) for p in coordinates])
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid geofence coordinates: unable to form a valid polygon")

def get_agency_id(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    id_token = authorization.split(" ")[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        agency_id = decoded_token.get("agencyId")
        if not agency_id:
            raise HTTPException(status_code=403, detail="User not linked to an agency")
        return agency_id
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Invalid token: {str(e)}")
