# Cal.com Chatbot (FastAPI)

This project implements a FastAPI server that demonstrates OpenAI function calling to interact with the Cal.com API. It provides natural language understanding for booking management through a combination of OpenAI's chat completions and Cal.com's booking APIs.

## Project Structure

```
.
├── main.py              # FastAPI application and endpoint handlers
├── cal_client.py        # Cal.com API client implementation
├── openai_client.py     # OpenAI client wrapper and function call helpers
├── schemas.py           # Pydantic models for request/response validation
├── utils.py             # Shared utilities and client initialization
├── mcp_tools.py         # OpenAI function definitions
├── exceptions.py        # Custom exception types
├── logging_config.py    # Centralized logging configuration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### File Responsibilities

- `main.py`: FastAPI application setup, client initialization during startup, and endpoint handlers for chat, book, list, and cancel operations.
- `cal_client.py`: Wraps Cal.com's API with proper error handling and logging. Uses requests.Session for efficient connections.
- `openai_client.py`: Manages OpenAI chat completions and function calling, with helpers to extract function calls from responses.
- `schemas.py`: Pydantic models that validate incoming requests and define the API contract.
- `utils.py`: Shared utilities including `build_booking_payload()` for consistent Cal.com payloads and `create_clients()` for initialization.
- `mcp_tools.py`: OpenAI function definitions that tell the model what Cal.com operations are available.
- `exceptions.py`: Custom exception types for Cal.com errors, OpenAI issues, and client initialization failures.
- `logging_config.py`: Centralized logging setup to ensure consistent logging across modules.

## Setup

### Requirements

1. Python 3.7+ and pip
2. A Cal.com API key  
3. An OpenAI API key

### Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-...            # Your OpenAI API key
CAL_COM_API_KEY=cal_...          # Your Cal.com API key
CAL_COM_BASE_URL=https://api.cal.com  # Optional: Cal.com API URL
```

### Installation

```bash
# Create and activate a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
python3 -m pip install -r requirements.txt
```

## Running the Server

Start the development server:

```bash
python3 -m uvicorn main:app --reload
```

Or run directly:

```bash
python3 main.py
```

The server will be available at `http://127.0.0.1:8000`.

## API Endpoints

### POST /chat
Natural language interface to Cal.com operations. Analyzes the message and executes the appropriate booking action.

```json
{
  "message": "Book a meeting for tomorrow at 3pm",
  "user_email": "user@example.com"
}
```

### POST /book
Direct booking creation endpoint.

```json
{
  "event_type_id": "123",
  "start_time": "2025-11-04T11:00:00Z",
  "customer_name": "Jacob Zuo",
  "customer_email": "jacob@example.com"
}
```

### POST /list
List bookings for a user.

```json
{
  "user_email": "user@example.com"
}
```

### POST /cancel
Cancel a specific booking.

```json
{
  "booking_id": "booking_xyz123"
}
```

## Example Usage

### Chat Interface

Using fetch in browser console or JavaScript:

```javascript
fetch("http://127.0.0.1:8000/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    message: "Book a meeting with Joe Doe tomorrow at 3pm",
    user_email: "user@example.com"
  })
})
.then(res => res.json())
.then(data => console.log("Response:", data))
.catch(err => console.error("Request failed:", err));
```

### Using curl

```bash
# List bookings
curl -X POST http://127.0.0.1:8000/list \
  -H "Content-Type: application/json" \
  -d '{"user_email": "user@example.com"}'

# Create booking
curl -X POST http://127.0.0.1:8000/book \
  -H "Content-Type: application/json" \
  -d '{
    "event_type_id": "123",
    "start_time": "2025-11-04T11:00:00Z",
    "customer_name": "Test User",
    "customer_email": "test@example.com"
  }'
```

## Error Handling

The application uses custom exception types for different failure modes:

- `CalClientError`: Raised for Cal.com API issues
- `OpenAIClientError`: Indicates OpenAI configuration or API problems
- `ClientInitError`: Signals failures during external client initialization

HTTP 500 responses include error details in the response body.

## Development

### Architecture

1. FastAPI handles HTTP routing and request validation
2. Clients are initialized during app startup and stored in app.state
3. The chat endpoint:
   - Sends messages to OpenAI with function definitions
   - Extracts and executes any function calls from the response
   - Returns both the function execution result and model's response
4. Direct endpoints provide programmatic access to Cal.com operations

### Logging

The application uses Python's logging framework, configured in `logging_config.py`. 
All modules use named loggers for proper attribution of log messages.

### Interactive Documentation

FastAPI's automatic documentation is available at:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
