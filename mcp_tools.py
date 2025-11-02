"""Shared module exporting the OpenAI function definitions used by the app.

Keep function metadata in one place so other modules (tests, tools) can
re-use the same definitions.
"""

__all__ = ["FUNCTIONS"]

FUNCTIONS = [
    {
        "name": "list_bookings",
        "description": "List bookings for a user by email",
        "parameters": {
            "type": "object",
            "properties": {
                "user_email": {"type": "string", "format": "email"},
                "status": {"type": "string", "enum": ["upcoming", "recurring", "past", "cancelled", "unconfirmed"]},
            },
            "required": [],
        },
    },
    {
        "name": "create_booking",
        "description": "Create a new booking using cal.com",
        "parameters": {
            "type": "object",
            "properties": {
                "start_time": {"type": "string"},
                "customer_name": {"type": "string"},
                "customer_email": {"type": "string", "format": "email"},
            },
            "required": ["start_time", "customer_name", "customer_email"],
        },
    },
    {
        "name": "cancel_booking",
        "description": "Cancel an existing booking by booking id",
        "parameters": {
            "type": "object",
            "properties": {"booking_id": {"type": "string"}},
            "required": ["booking_id"],
        },
    },
]
