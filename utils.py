import logging
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)
from exceptions import ClientInitError


def build_booking_payload(
    start: str,
    customer_name: str,
    customer_email: str,
    event_type_id: Optional[int] = None,
    event_type_slug: str = "30min",
    note: str = "",
    time_zone: str = "America/Los_Angeles",
    language: str = "en",
) -> Dict[str, Any]:
    """Return a payload dict suitable for Cal.com's create booking API.

    This centralizes the shape used by both the /chat function-calling flow
    and the /book endpoint so changes need to be made in a single place.
    """

    payload = {
        "start": start,
        "attendee": {
            "name": customer_name,
            "email": customer_email,
            "timeZone": time_zone,
            "language": language,
        },
        # Use provided event_type_id when present; otherwise fall back to the
        # historically-used default id (kept for backwards compatibility).
        "eventTypeId": event_type_id or 3778941,
        "eventTypeSlug": event_type_slug,
        "location": {
            "type": "integration",
            "integration": "google-meet",
        },
        "metadata": {"note": note},
    }

    return payload


def create_clients() -> Tuple[object, object]:
    """Create and return (cal_client, openai_client).

    This helper centralizes client construction and mirrors the previous
    behavior in `main.py`. It reads configuration from environment
    variables `CAL_COM_API_KEY`, `CAL_COM_BASE_URL`, and `OPENAI_API_KEY`.

    On error it returns (None, None) and prints a warning.
    """
    import os
    from cal_client import CalClient
    from openai_client import OpenAIClient

    try:
        cal_api_key = os.environ.get("CAL_COM_API_KEY")
        cal_base_url = os.environ.get("CAL_COM_BASE_URL", "https://api.cal.com")
        cal = CalClient(api_key=cal_api_key, base_url=cal_base_url)

        openai_api_key = os.environ.get("OPENAI_API_KEY")
        openai = OpenAIClient(api_key=openai_api_key)
    except Exception as e:
        logger.exception("Failed to initialize clients: %s", e)
        raise ClientInitError("Failed to initialize external clients") from e

    return cal, openai
