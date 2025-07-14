from fastapi import APIRouter, HTTPException
from schemas import *

router = APIRouter()

@router.post("/search_flight", response_model=FlightSearchResponse)
async def search_flight(request: dict):
    try:
        # Replace this with service call
        dummy = FlightSearchResponse(
            results=[FlightOption(
                flight_id="ABC123",
                airline="Delta",
                price=499.0,
                departure_time="2025-08-10T08:00",
                arrival_time="2025-08-10T16:00",
                duration="8h",
                stops=0,
                cabin_class="economy"
            )],
            total_matches=1
        )
        return dummy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/book_flight", response_model=FlightBookingConfirmation)
async def book_flight(request: dict):
    try:
        confirmation = FlightBookingConfirmation(
            booking_id="BOOK123",
            total_price=950.0,
            passengers=1,
            contact_email="john.doe@example.com",
            flight_details={"flight_id": "ABC123", "airline": "Delta"}
        )
        return confirmation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/book_trip", response_model=TripBookingResponse)
async def book_trip(request: dict):
    try:
        result = TripBookingResponse(
            trip_id="TRIP789",
            total_cost=1800.0,
            passengers=2,
            included_items=["flight", "hotel", "excursions"],
            accommodation={"type": "hotel", "name": "Madrid Inn"},
            itinerary=[{"day": 1, "activity": "Museum tour"}]
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
