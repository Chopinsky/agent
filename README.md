````markdown
# Cal.com Chatbot (FastAPI)

This project implements a FastAPI server that demonstrates OpenAI function calling to interact with the Cal.com API.

Quick notes:
- Reads API keys from a `.env` file at the repository root. The provided `.env` in the workspace contains `OPENAI_API_KEY`, `CAL_COM_API_KEY`, and `CAL_COM_BASE_URL`.
- Endpoints exposed by the server (see `server/main.py`):
  - POST /chat  — send a user message and let the model call functions to interact with Cal.com
  - POST /book  — directly create a booking
  - POST /list  — list bookings for a given user email
  - POST /cancel — cancel a booking by id

Install dependencies and run (Windows PowerShell):

```bash
python -m pip install -r server/requirements.txt
cd server
python -m uvicorn server.main:app --reload
```

Notes and assumptions:
- The Cal.com endpoints used in `server/cal_client.py` follow the documented v2 API:
  - GET `/v2/bookings` to list bookings
  - POST `/v2/bookings` to create bookings
  - POST `/v2/bookings/{bookingUid}/cancel` to cancel bookings
- The client sets the required `cal-api-version` header with sensible defaults (overridable via environment variables `CAL_API_VERSION_BOOKINGS` and `CAL_API_VERSION_SLOTS`).
- OpenAI model id is set to `gpt-4o-mini` in `server/openai_client.py` as an example; change to a model available for your account.
