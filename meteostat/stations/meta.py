from requests import get, HTTPError, Timeout
from meteostat import settings
from meteostat.core.cache import cache
from meteostat.stations import Station

@cache(60 * 60 * 24 * 7)
def meta(id: str) -> Station | None:
    """
    Get meta data for a specific weather station
    """
    # Get all meta data mirrors
    mirrors = settings.stations_meta_mirrors
    # Get meta data for weather station
    for mirror in mirrors:
        try:  
            with get(mirror.format(id=id)) as res:
                if res.status_code == 200:
                    return res.json()
        except (HTTPError, Timeout):
            continue
    # If meta data could not be found, return None
    return None