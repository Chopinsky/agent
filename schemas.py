from pydantic import BaseModel, EmailStr


class ChatRequest(BaseModel):
    user_email: EmailStr
    message: str


class BookRequest(BaseModel):
    event_type_id: str
    start_time: str  # ISO datetime
    customer_name: str
    customer_email: EmailStr


class CancelRequest(BaseModel):
    booking_id: str


class ListRequest(BaseModel):
    user_email: EmailStr
