# Cal.com Chatbot (FastAPI)

This project implements a FastAPI server that demonstrates OpenAI function calling to interact with the Cal.com API.

Quick notes:
- Reads API keys from a `.env` file at the repository root. The provided `.env` in the workspace contains `OPENAI_API_KEY`, `CAL_COM_API_KEY`, and `CAL_COM_BASE_URL`.
- Endpoints:
  - POST /chat  — send a user message and let the model call functions to interact with Cal.com
  - POST /book  — directly create a booking
  - POST /list  — list bookings for a given user email
  - POST /cancel — cancel a booking by id

Install dependencies and run (Windows PowerShell):

```powershell
python -m pip install -r server/requirements.txt
python -m uvicorn server.main:app --reload
```

Notes and assumptions:
- The Cal.com endpoints used in `cal_client.py` make reasonable assumptions about v2 endpoints: `/v2/bookings`, `/v2/bookings/{id}/cancel`, `/v2/slots/find`. Adjust these if the real API differs.
- OpenAI model id is set to `gpt-4o-mini` in `openai_client.py` as an example; change to a model available for your account.
