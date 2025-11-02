# Cal.com Chatbot (FastAPI)

This project implements a FastAPI server that demonstrates OpenAI function calling to interact with the Cal.com API.

## Requirements
- Reads API keys from a `.env` file at the repository root. The provided `.env` in the workspace contains `OPENAI_API_KEY`, `CAL_COM_API_KEY`, and `CAL_COM_BASE_URL`.

- Endpoints:
  - POST /chat  — send a user message and let the model call functions to interact with Cal.com
  - POST /book  — directly create a booking
  - POST /list  — list bookings for a given user email
  - POST /cancel — cancel a booking by id

## Quick Start
Install dependencies and run (Windows PowerShell):

```powershell
python3 -m pip install -r requirements.txt
python3 -m uvicorn main:app --reload
```

## Test Booking

Send the post request with:

```javascript
fetch("http://127.0.0.1:8000/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    message: "Hello I want to book an event on 11/04/2025 at 11AM for Jacob Zuo",
    user_email: "jacob.dzwo@gmail.com"
  })
})
.then(response => {
  if (response.ok) return response.json().catch(() => null);
  return response.text().then(text => Promise.reject({ status: response.status, body: text }));
})
.then(data => console.log("Response:", data))
.catch(err => console.error("Request failed:", err));
```

