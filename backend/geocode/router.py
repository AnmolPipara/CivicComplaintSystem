from fastapi import APIRouter, Query
import httpx
import logging
import urllib.parse
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/geocode", tags=["Geocoding"])

HEADERS = {
    "User-Agent": "JanSewa-CivicComplaintSystem/1.0 (contact: anmolpipara@gmail.com)",
    "Accept": "application/json",
}

# In-memory LRU cache to reduce external Nominatim requests and prevent rate-limiting
_search_cache: Dict[str, List[Dict[str, Any]]] = {}
_reverse_cache: Dict[str, Dict[str, Any]] = {}


@router.get("/search")
async def search_locations(
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=10)
):
    query_clean = q.lower().strip()
    cache_key = f"{query_clean}_{limit}"
    if cache_key in _search_cache:
        return _search_cache[cache_key]

    try:
        encoded_query = urllib.parse.quote(query_clean)
        async with httpx.AsyncClient(timeout=7.0, headers=HEADERS) as client:
            # Primary search restricted to India for civic municipal relevance
            url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=jsonv2&addressdetails=1&countrycodes=in&limit={limit}"
            resp = await client.get(url)
            data = resp.json() if resp.status_code == 200 else []

            # Fallback without country filter if no results in India
            if not data or not isinstance(data, list) or len(data) == 0:
                url_fallback = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=jsonv2&addressdetails=1&limit={limit}"
                resp_fb = await client.get(url_fallback)
                if resp_fb.status_code == 200:
                    data = resp_fb.json()

            if isinstance(data, list):
                if len(_search_cache) > 500:
                    _search_cache.clear()
                _search_cache[cache_key] = data
                return data
            return []
    except Exception as e:
        logger.warning(f"Geocoding search failed for '{q}': {e}")
        return []


@router.get("/reverse")
async def reverse_geocode(
    lat: float = Query(...),
    lon: float = Query(...)
):
    cache_key = f"{round(lat, 5)}_{round(lon, 5)}"
    if cache_key in _reverse_cache:
        return _reverse_cache[cache_key]

    try:
        async with httpx.AsyncClient(timeout=7.0, headers=HEADERS) as client:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2&addressdetails=1"
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if len(_reverse_cache) > 500:
                    _reverse_cache.clear()
                _reverse_cache[cache_key] = data
                return data
            return {"display_name": f"Location ({lat:.5f}, {lon:.5f})"}
    except Exception as e:
        logger.warning(f"Reverse geocode failed for ({lat}, {lon}): {e}")
        return {"display_name": f"Location ({lat:.5f}, {lon:.5f})"}
