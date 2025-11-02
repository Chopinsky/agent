import os
import logging
from typing import Optional, Dict, Any

import requests

logger = logging.getLogger(__name__)
from exceptions import CalClientError

# Environment / defaults
CAL_API_KEY = os.environ.get("CAL_COM_API_KEY")
CAL_BASE = os.environ.get("CAL_COM_BASE_URL", "https://api.cal.com")
# API version headers required by Cal.com docs
CAL_API_VERSION_BOOKINGS = os.environ.get("CAL_COM_API_VERSION_BOOKINGS", "2024-08-13")
CAL_API_VERSION_SLOTS = os.environ.get("CAL_COM_API_VERSION_SLOTS", "2024-09-04")


class CalClient:
    """Simple Cal.com API client.

    This client implements the endpoints documented here:
    - Get all bookings: https://cal.com/docs/api-reference/v2/bookings/get-all-bookings
    - Create a booking: https://cal.com/docs/api-reference/v2/bookings/create-a-booking
    - Cancel a booking: https://cal.com/docs/api-reference/v2/bookings/cancel-a-booking
    - Get available slots: https://cal.com/docs/api-reference/v2/slots/get-available-time-slots-for-an-event-type

    Notes:
    - The Cal API requires a `cal-api-version` header for these endpoints. We use
      sensible defaults above but you can override via environment variables.
    - The client expects an API key available in the `CAL_COM_API_KEY` environment
      variable (or passed to the constructor). The Authorization header is set to
      `Bearer <api_key>` per docs.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 10,
    ) -> None:
        self.api_key = api_key or CAL_API_KEY
        self.base = (base_url or CAL_BASE).rstrip("/")
        if not self.api_key:
            raise CalClientError("CAL_COM_API_KEY is not set in environment or passed to CalClient")

        self.timeout = timeout

        # Base headers common to requests; individual methods will add `cal-api-version`
        self.base_headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _headers_for(self, *, bookings: bool = False, slots: bool = False) -> Dict[str, str]:
        """Return headers including the appropriate cal-api-version for the endpoint."""
        headers = dict(self.base_headers)
        if bookings:
            headers["cal-api-version"] = CAL_API_VERSION_BOOKINGS
        if slots:
            headers["cal-api-version"] = CAL_API_VERSION_SLOTS
        return headers

    def list_bookings(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List bookings using GET /v2/bookings.

        Accepts any of the documented query parameters (see docs) via `params`.
        Example: client.list_bookings({"attendeeEmail": "joe@example.com", "take": 50})

        Returns the parsed JSON response (the docs return an object with keys
        `status`, `data`, and `pagination`).
        """
        url = f"{self.base}/v2/bookings"
        headers = self._headers_for(bookings=True)
        try:
            with requests.Session() as session:
                resp = session.get(url, headers=headers, params=params or {}, timeout=self.timeout)
                resp.raise_for_status()
                return resp.json()
        except requests.HTTPError as e:
            resp_text = getattr(e.response, "text", None)
            logger.exception("Cal.com list_bookings HTTP error: %s - Response: %s", e, resp_text)
            raise CalClientError(f"list_bookings failed: {resp_text}") from e
        except Exception as e:
            logger.exception("Cal.com list_bookings unexpected error: %s", e)
            raise CalClientError("list_bookings failed") from e

    def create_booking(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a booking using POST /v2/bookings.

        The payload should follow the create booking schema from the docs. The
        endpoint supports regular, instant and recurring bookings depending on
        the provided payload.
        """
        url = f"{self.base}/v2/bookings"
        headers = self._headers_for(bookings=True)
        try:
            with requests.Session() as session:
                resp = session.post(url, headers=headers, json=payload, timeout=self.timeout)
                resp.raise_for_status()
                return resp.json()
        except requests.HTTPError as e:
            resp_text = getattr(e.response, "text", None)
            logger.exception("Cal.com create_booking HTTP error: %s - Response: %s", e, resp_text)
            raise CalClientError(f"create_booking failed: {resp_text}") from e
        except Exception as e:
            logger.exception("Cal.com create_booking unexpected error: %s", e)
            raise CalClientError("create_booking failed") from e

    def cancel_booking(self, booking_uid: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Cancel a booking using POST /v2/bookings/{bookingUid}/cancel.

        `booking_uid` is the booking's UID (string) per docs. Optional `body`
        can include `cancellationReason`, `cancelSubsequentBookings`, `seatUid`, etc.
        Returns the parsed JSON response.
        """
        url = f"{self.base}/v2/bookings/{booking_uid}/cancel"
        headers = self._headers_for(bookings=True)
        try:
            with requests.Session() as session:
                resp = session.post(url, headers=headers, json=body or {}, timeout=self.timeout)
                resp.raise_for_status()
                return resp.json()
        except requests.HTTPError as e:
            resp_text = getattr(e.response, "text", None)
            logger.exception("Cal.com cancel_booking HTTP error: %s - Response: %s", e, resp_text)
            raise CalClientError(f"cancel_booking failed: {resp_text}") from e
        except Exception as e:
            logger.exception("Cal.com cancel_booking unexpected error: %s", e)
            raise CalClientError("cancel_booking failed") from e


__all__ = ["CalClient"]
