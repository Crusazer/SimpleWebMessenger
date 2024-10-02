import logging

import httpx
from httpx import Response
from src.config import settings

logger = logging.getLogger(__name__)


async def get_location_by_ip(ip: str) -> str | None:
    """
    Return location by ip. If no location exists or problem with connection to service, return None.
    Change this function to work with other services.
    """
    if settings.USE_USER_GEOLOCATION:
        try:
            async with httpx.AsyncClient() as client:
                response: Response = await client.get(
                    f"https://api.ipinfo.info/{ip}/?access_key={settings.API_LOCATION_KEY}&output=json"
                )
                data: dict = response.json()
                location = (
                    f"{data["continent_name"]}, {data["country_name"]}, {data["city"]}"
                )
                return location
        except (httpx.RequestError, KeyError):
            logger.exception("Failed to get location for ip %s", ip)
            return None
    return ""
