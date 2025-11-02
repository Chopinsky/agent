import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from server.schemas import ChatRequest, BookRequest, CancelRequest, ListRequest
from server.cal_client import CalClient
from server.openai_client import call_chat_completion, extract_function_call


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(title="Cal.com Chatbot (Function-calling)")

# Instantiate Cal client (will read CAL_COM_API_KEY from environment)
try:
    cal = CalClient()
except Exception as e:
    # Keep app running but mark cal as None
    cal = None


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
                "end_time": {"type": "string"},
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


@app.post("/chat")
async def chat(req: ChatRequest):
    """Accept a user message and use OpenAI function calling to interact with cal.com.

    The flow:
    - Send the user message + function definitions to OpenAI
    - If the model returns a function call, execute the corresponding cal client method
    - Return the final result to the caller
    """
    if cal is None:
        raise HTTPException(status_code=500, detail="Cal.com client not configured (missing CAL_COM_API_KEY)")

    system = {"role": "system", "content": "You are an assistant that helps users book, list and cancel events using Cal.com. Ask clarifying questions if needed."}
    user = {"role": "user", "content": f"{req.message} (user email: {req.user_email})"}

    try:
        resp = call_chat_completion([system, user], functions=FUNCTIONS)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # If model asked to call function, execute it
    fc = extract_function_call(resp)
    if fc:
        name = fc.get("name")
        args = fc.get("arguments") or {}
        try:
            if name == "list_bookings":
                params = {
                    "take": "100",
                    "status": args.get("status"),
                    "attendeeEmail": args.get("user_email"),
                }
                result = cal.list_bookings(params)
            elif name == "create_booking":
                # translate args to create payload expected by cal.com
                payload = {
                    "start": args.get("start_time"),
                    "end": args.get("end_time"),
                    "attendee": {
                        "name": args.get("customer_name"),
                        "email": args.get("customer_email"),
                        "timeZone": "America/Los_Angeles",
                        "language": "en"
                    },
                    "eventTypeId": 3778941,
                    "eventTypeSlug": "30min",
                    "location": {
                        "type": "integration",
                        "integration": "google-meet"
                    },
                    "metadata": {
                        "key": "value"
                    },
                    "lengthInMinutes": 30
                }
                result = cal.create_booking(payload)
            elif name == "cancel_booking":
                result = cal.cancel_booking(args["booking_id"])
            else:
                result = {"error": "unknown function"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"cal.com error: {e}")

        # Return model's function call intent plus upstream result
        return JSONResponse({"function_called": name, "arguments": args, "result": result})

    # otherwise return the assistant text
    try:
        msg = resp["choices"][0]["message"]["content"]
    except Exception:
        msg = str(resp)
    return {"assistant": msg}


@app.post("/book")
async def book(req: BookRequest):
    if cal is None:
        raise HTTPException(status_code=500, detail="Cal.com client not configured")
    payload = {
        "eventTypeId": req.event_type_id,
        "start": req.start_time,
        "end": req.end_time,
        "attendee": {"name": req.customer_name, "email": req.customer_email},
        "notes": req.notes,
    }
    try:
        result = cal.create_booking(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/list")
async def list_bookings(req: ListRequest):
    if cal is None:
        raise HTTPException(status_code=500, detail="Cal.com client not configured")
    try:
        params = {"attendeeEmail": req.user_email, "take": 100}
        result = cal.list_bookings(params)
        return {"bookings": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cancel")
async def cancel(req: CancelRequest):
    if cal is None:
        raise HTTPException(status_code=500, detail="Cal.com client not configured")
    try:
        result = cal.cancel_booking(req.booking_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)
