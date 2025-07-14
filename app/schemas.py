from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# =====================
# FLIGHT MODELS
# =====================

class FlightOption(BaseModel):
    flight_id: str
    airline: str
    price: float
    departure_time: str
    arrival_time: str
    duration: str
    stops: int
    cabin_class: str

class FlightSearchResponse(BaseModel):
    results: List[FlightOption]
    currency: str = "USD"
    total_matches: int

class FlightBookingConfirmation(BaseModel):
    booking_id: str
    status: str = "confirmed"
    total_price: float
    passengers: int
    contact_email: str
    flight_details: Dict[str, Any]

class FlightAvailabilityResponse(BaseModel):
    available: bool
    available_classes: List[str]
    next_available_date: Optional[str]

# =====================
# TRIP MODELS
# =====================

class TripBookingResponse(BaseModel):
    trip_id: str
    status: str = "booked"
    total_cost: float
    passengers: int
    included_items: List[str]
    accommodation: Dict[str, str]
    itinerary: List[Dict[str, Any]]

class TripCancellationPolicyResponse(BaseModel):
    refundable: bool
    refund_amount: float
    conditions: List[str]

class TripSegment(BaseModel):
    segment_type: str  # flight, hotel, transfer
    details: Dict[str, Any]

class TripSegmentsResponse(BaseModel):
    booking_reference: str
    segments: List[TripSegment]

# =====================
# GENERIC RESPONSES
# =====================

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str

class SuccessResponse(BaseModel):
    status: str = "success"
    data: Any
