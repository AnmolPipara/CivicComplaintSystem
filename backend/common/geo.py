import math
import os
import urllib.request
import urllib.parse
import json
from typing import Optional, Tuple
from sqlalchemy import func

DEFAULT_VISIBILITY_RADIUS_KM = 25.0


def get_visibility_radius_km() -> float:
    """Return the configured incident visibility and upvoting radius in km."""
    try:
        val = os.getenv("INCIDENT_VISIBILITY_RADIUS_KM")
        if val is not None and val.strip() != "":
            return float(val.strip())
        return DEFAULT_VISIBILITY_RADIUS_KM
    except (ValueError, TypeError):
        return DEFAULT_VISIBILITY_RADIUS_KM


def calculate_haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth (decimal degrees)
    using the Haversine formula. Returns distance in kilometers.
    """
    R = 6371.0  # Earth radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    a = max(0.0, min(1.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def get_haversine_sql_expression(user_lat: float, user_lon: float, lat_col, lon_col):
    """
    Constructs a SQLAlchemy SQL expression for great-circle distance in kilometers.
    Compatible with PostgreSQL and SQLite using standard trigonometric functions.
    """
    rad_ulat = math.radians(user_lat)
    rad_ulon = math.radians(user_lon)
    cos_ulat = math.cos(rad_ulat)
    sin_ulat = math.sin(rad_ulat)

    rad_lat2 = func.radians(lat_col)
    rad_lon2 = func.radians(lon_col)

    cos_prod = cos_ulat * func.cos(rad_lat2) * func.cos(rad_lon2 - rad_ulon)
    sin_prod = sin_ulat * func.sin(rad_lat2)

    # Clamp argument to [-1.0, 1.0] to prevent floating point domain errors with acos
    clamped_val = func.greatest(-1.0, func.least(1.0, cos_prod + sin_prod))
    return 6371.0 * func.acos(clamped_val)


def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Geocode an address string to (latitude, longitude) using OpenStreetMap Nominatim.
    Returns (lat, lon) or None if not found or on network failure.
    """
    if not address or not address.strip():
        return None
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(address.strip())}&format=json&limit=1"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "JanSewa-CivicComplaintSystem/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                if data and len(data) > 0:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    return (lat, lon)
    except Exception as e:
        print(f"Geocoding error for '{address}': {e}")
    return None
