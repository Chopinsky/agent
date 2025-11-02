import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from exceptions import ClientInitError
from logging_config import configure_logging
from mcp_tools import FUNCTIONS
from openai_client import extract_function_call
from schemas import ChatRequest, BookRequest, CancelRequest, ListRequest
from utils import build_booking_payload, create_clients


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI(title="Cal.com Chatbot (Function-calling)")

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)


@app.on_event("startup")
def startup_event() -> None:
    """Initialize external clients and attach them to the app state.

    This keeps initialization out of the module import path and makes the
    application easier to test.
    """
    try:
        cal_client, openai_client = create_clients()
        app.state.cal = cal_client
        app.state.openai = openai_client
        logger.info("External clients initialized")
    except ClientInitError as e:
        # Fail early: startup without clients is not supported in the new model
        logger.exception("Failed to initialize external clients: %s", e)
        raise


@app.post("/chat")
async def chat(req: ChatRequest):
    """Accept a user message and use OpenAI function calling to interact with cal.com.

    The flow:
    - Send the user message + function definitions to OpenAI
    - If the model returns a function call, execute the corresponding cal client method
    - Return the final result to the caller
    """
    if not getattr(app.state, "cal", None):
        raise HTTPException(status_code=500, detail="Cal.com client not configured (missing CAL_COM_API_KEY)")

    system = {"role": "system", "content": "You are an assistant that helps users book, list and cancel events using Cal.com. Ask clarifying questions if needed."}
    user = {"role": "user", "content": f"{req.message} (user email: {req.user_email})"}

    try:
        resp = app.state.openai.call_chat_completion([system, user], functions=FUNCTIONS)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # If model asked to call function, execute it
    fc = extract_function_call(resp)
    if fc:
        name = fc.get("name")
        args = fc.get("arguments") or {}
        try:
            if name == "list_bookings":
                result = app.state.cal.list_bookings(
                    {
                        "take": "100",
                        "status": args.get("status"),
                        "attendeeEmail": args.get("user_email"),
                    }
                )
            elif name == "create_booking":
                # translate args to create payload expected by cal.com
                result = app.state.cal.create_booking(
                    build_booking_payload(
                        start=args.get("start_time"),
                        customer_name=args.get("customer_name"),
                        customer_email=args.get("customer_email"),
                        note="chat booking",
                    )
                )
            elif name == "cancel_booking":
                result = app.state.cal.cancel_booking(args["booking_id"])
            else:
                result = {"error": "unknown function"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"cal.com error: {e}")

        # Return model's function call intent plus upstream result
        return JSONResponse({"function_called": name, "arguments": args, "result": result})

    # otherwise return the assistant text
    try:
        msg = resp.choices[0]
    except Exception:
        msg = str(resp)

    return {"assistant": msg}


@app.post("/book")
async def book(req: BookRequest):
    if not getattr(app.state, "cal", None):
        raise HTTPException(status_code=500, detail="Cal.com client not configured")
    
    try:
        result = app.state.cal.create_booking(
            build_booking_payload(
                start=req.start_time,
                customer_name=req.customer_name,
                customer_email=req.customer_email,
                event_type_id=req.event_type_id,
                note="API booking",
            )
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/list")
async def list_bookings(req: ListRequest):
    if not getattr(app.state, "cal", None):
        raise HTTPException(status_code=500, detail="Cal.com client not configured")
    
    try:
        params = {"attendeeEmail": req.user_email, "take": 100}
        result = app.state.cal.list_bookings(params)
        return {"bookings": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cancel")
async def cancel(req: CancelRequest):
    if not getattr(app.state, "cal", None):
        raise HTTPException(status_code=500, detail="Cal.com client not configured")
    
    try:
        result = app.state.cal.cancel_booking(req.booking_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    # When running directly, point uvicorn to this module's app
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
