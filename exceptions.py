"""Project-specific exception types for clearer error handling."""

class CalClientError(Exception):
    """Raised for errors interacting with the Cal.com API."""


class OpenAIClientError(Exception):
    """Raised for errors related to the OpenAI client configuration or calls."""


class ClientInitError(Exception):
    """Raised when initialization of external clients (Cal, OpenAI) fails."""
