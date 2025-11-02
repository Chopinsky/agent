from pydantic import BaseModel, EmailStr
from typing import Optional, List


class ChatRequest(BaseModel):
    user_email: EmailStr
    message: str


class BookRequest(BaseModel):
    event_type_id: str
    start_time: str  # ISO datetime
    end_time: Optional[str] = None
    customer_name: str
    customer_email: EmailStr
    notes: Optional[str] = None


class CancelRequest(BaseModel):
    booking_id: str


class ListRequest(BaseModel):
    user_email: EmailStr


class Booking(BaseModel):
    id: str
    start_time: str
    end_time: Optional[str]
    name: Optional[str]
    email: Optional[EmailStr]


class BookingList(BaseModel):
    bookings: List[Booking]
