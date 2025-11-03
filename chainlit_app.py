import chainlit as cl
import httpx

# Default email used for bookings if not provided
DEFAULT_EMAIL = "andrew.zuo@gmail.com"

# API endpoint (update this if your FastAPI server runs on a different port/host)
API_URL = "http://127.0.0.1:8000"


@cl.on_chat_start
def start():
    """Initialize the chat session."""
    cl.user_session.set("email", DEFAULT_EMAIL)


@cl.action_callback("set_email")
async def set_email(action):
    """Handle the email setting action."""
    new_email = action.value
    cl.user_session.set("email", new_email)
    await cl.Message(
        content=f"Email updated to: {new_email}",
        author="System"
    ).send()


async def call_api(endpoint: str, payload: dict) -> dict:
    """Make API calls to the FastAPI backend."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_URL}/{endpoint}",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            error_msg = f"API error: {str(e)}"
            if hasattr(e, "response") and e.response is not None:
                error_msg = f"API error: {e.response.text}"
            raise cl.Error(error_msg)


async def list_bookings(email: str) -> str:
    """List bookings for the specified email."""
    result = await call_api("list", {"user_email": email})
    bookings = result.get("bookings", [])

    if not bookings:
        return "No bookings found."

    # Format bookings into a readable list
    booking_list = []
    for booking in bookings:
        start = booking.get("startTime", "N/A")
        title = booking.get("title", "Untitled")
        status = booking.get("status", "unknown")
        id = booking.get("id", "N/A")
        booking_list.append(
            f"- {title} on {start} (Status: {status}, ID: {id})")

    return "Your bookings:\n" + "\n".join(booking_list)


@cl.on_message
async def main(message: cl.Message):
    """Main chat handler."""
    # Get current user email
    email = cl.user_session.get("email")

    # Create actions for setting email
    actions = [
        cl.Action(
            name="set_email",
            value=email,
            label="Change Email",
            description="Update the email used for bookings"
        )
    ]

    try:
        # Call the chat endpoint
        response = await call_api(
            "chat",
            {
                "message": message.content,
                "user_email": email
            }
        )

        # Handle function calls from the API
        if "function_called" in response:
            function = response["function_called"]
            result = response["result"]

            if function == "list_bookings":
                # Format the booking list response
                content = await list_bookings(email)
            elif function == "create_booking":
                # Format the booking creation response
                booking_time = result.get("startTime", "unknown time")
                content = f"✅ Booking created successfully for {booking_time}"
            elif function == "cancel_booking":
                # Format the cancellation response
                content = f"❌ Booking cancelled successfully"
            else:
                content = f"Operation completed: {function}"

            elements = []

            # If we have booking details, show them
            if isinstance(result, dict) and result.get("startTime"):
                elements.append(
                    cl.Text(name="booking_details",
                            content=f"Booking Details:\n{str(result)}")
                )

            await cl.Message(
                content=content,
                elements=elements,
                actions=actions
            ).send()
        else:
            # Direct message from assistant
            await cl.Message(
                content=response.get(
                    "assistant", "No response from assistant"),
                actions=actions
            ).send()

    except cl.Error as e:
        await cl.Message(
            content=f"Error: {str(e)}",
            actions=actions
        ).send()
    except Exception as e:
        await cl.Message(
            content=f"Unexpected error: {str(e)}",
            actions=actions
        ).send()
