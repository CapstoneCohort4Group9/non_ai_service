from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from contextlib import asynccontextmanager
from database_connection import init_database, close_database, get_db_session
from database_models import SessionLocal
from data import (
    FlightService, BookingService, SeatService, TripService, 
    PolicyService, InsuranceService, CheckInService, RefundService,
    CustomerServiceService, BaggageService, PricingService
)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_database()
    yield
    # Shutdown
    await close_database()

app = FastAPI(
    title="HopJetAir Customer Service API", 
    description="Comprehensive airline customer service system for HopJetAir",
    version="1.0.0",
    lifespan=lifespan
)

# Keep your existing Pydantic models as they are
class SearchFlightRequest(BaseModel):
    origin: str = "Chicago"
    destination: str = "Madrid"
    departure_date: str = "2025-08-10"
    return_date: str = "2025-08-20"
    trip_type: str = "round-trip"
    airline: str = "American Airlines"
    passengers: int = 1
    non_stop: bool = True
    departure_window: Dict[str, Any] = {'start': '2025-09-10', 'end': '2025-09-20'}
    max_price: int = 700
    airline_preferences: List[Any] = []
    direct_only: bool = True
    max_price_per_passenger: int = 900
    flight_preference: str = "non-stop"
    classname: str = "economy"
    preferred_time: str = "morning"
    budget: int = 700
    preferred_departure_time: str = "morning"
    budget_per_person: int = 900
    airline_type: str = "full-service"
    layover_preference: str = "allowed"
    direct_flights_only: bool = True
    preferences: Dict[str, Any] = {'direct_flight': True}

class BookFlightRequest(BaseModel):
    origin: str = "Chicago"
    destination: str = "Madrid"
    departure_date: str = "2025-08-10"
    return_date: str = "2025-08-20"
    trip_type: str = "round-trip"
    airline: str = "American Airlines"
    price: int = 950
    passengers: int = 1
    non_stop: bool = True
    price_per_passenger: int = 850
    classname: str = "economy"
    direct_only: bool = True
    preferred_time: str = "morning"
    price_per_person: int = 880
    layover_preference: str = "allowed"
    flight_id: str = "cheapest_nonstop_1"
    contact: str = "john.doe@example.com"

# ... [Keep all your other existing Pydantic models] ...

# Helper function to get sync database session
def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {
        "message": "Welcome to HopJetAir Customer Service API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from database_connection import check_database_health
    
    db_healthy = await check_database_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "timestamp": "2025-07-14T10:00:00Z"
    }

# Flight-related endpoints
@app.post("/search_flight")
async def search_flight(request: SearchFlightRequest, db = Depends(get_sync_db)):
    """Search for available flights"""
    try:
        result = await FlightService.search_flights(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/book_flight")
async def book_flight(request: BookFlightRequest, db = Depends(get_sync_db)):
    """Book a flight"""
    try:
        result = await FlightService.book_flight(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_flights")
async def search_flights(request: SearchFlightsRequest, db = Depends(get_sync_db)):
    """Search flights with advanced filters"""
    try:
        result = await FlightService.search_flights(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_flight_status")
async def check_flight_status(request: CheckFlightStatusRequest, db = Depends(get_sync_db)):
    """Check flight status"""
    try:
        result = await FlightService.check_flight_status(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_flight_availability")
async def check_flight_availability(request: CheckFlightAvailabilityRequest, db = Depends(get_sync_db)):
    """Check flight availability"""
    try:
        result = await FlightService.search_flights(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_flight_prices")
async def search_flight_prices(request: SearchFlightPricesRequest, db = Depends(get_sync_db)):
    """Search flight prices"""
    try:
        result = await PricingService.search_flight_prices(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_flight_prices")
async def check_flight_prices(request: CheckFlightPricesRequest, db = Depends(get_sync_db)):
    """Check flight prices"""
    try:
        result = await PricingService.search_flight_prices(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Booking-related endpoints
@app.post("/get_booking_details")
async def get_booking_details(request: GetBookingDetailsRequest, db = Depends(get_sync_db)):
    """Get booking details"""
    try:
        result = await BookingService.check_booking_details(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_flight_reservation")
async def check_flight_reservation(request: CheckFlightReservationRequest, db = Depends(get_sync_db)):
    """Check flight reservation"""
    try:
        result = await BookingService.check_booking_details(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cancel_booking")
async def cancel_booking(request: CancelBookingRequest, db = Depends(get_sync_db)):
    """Cancel booking"""
    try:
        result = await BookingService.cancel_booking(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Seat-related endpoints
@app.post("/check_seat_availability")
async def check_seat_availability(request: CheckSeatAvailabilityRequest, db = Depends(get_sync_db)):
    """Check seat availability"""
    try:
        result = await SeatService.check_seat_availability(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/change_seat")
async def change_seat(request: ChangeSeatRequest, db = Depends(get_sync_db)):
    """Change seat assignment"""
    try:
        result = await SeatService.change_seat(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/choose_seat")
async def choose_seat(request: ChooseSeatRequest, db = Depends(get_sync_db)):
    """Choose seat"""
    try:
        result = await SeatService.change_seat(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Trip and package endpoints
@app.post("/search_trip")
async def search_trip(request: SearchTripRequest, db = Depends(get_sync_db)):
    """Search trip packages"""
    try:
        result = await TripService.search_trip(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/book_trip")
async def book_trip(request: BookTripRequest, db = Depends(get_sync_db)):
    """Book trip package"""
    try:
        result = await TripService.book_trip(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Policy endpoints
@app.post("/query_policy_rag_db")
async def query_policy_rag_db(request: QueryPolicyRagDbRequest, db = Depends(get_sync_db)):
    """Query airline policies"""
    try:
        result = await PolicyService.query_policy(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Insurance endpoints
@app.post("/search_flight_insurance")
async def search_flight_insurance(request: SearchFlightInsuranceRequest, db = Depends(get_sync_db)):
    """Search flight insurance options"""
    try:
        result = await InsuranceService.search_flight_insurance(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/purchase_flight_insurance")
async def purchase_flight_insurance(request: PurchaseFlightInsuranceRequest, db = Depends(get_sync_db)):
    """Purchase flight insurance"""
    try:
        result = await InsuranceService.purchase_flight_insurance(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Check-in endpoints
@app.post("/check_in_passenger")
async def check_in_passenger(request: CheckInPassengerRequest, db = Depends(get_sync_db)):
    """Check in passenger"""
    try:
        result = await CheckInService.check_in_passenger(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_boarding_pass")
async def get_boarding_pass(request: GetBoardingPassRequest, db = Depends(get_sync_db)):
    """Get boarding pass"""
    try:
        result = await CheckInService.get_boarding_pass(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Baggage endpoints
@app.post("/check_baggage_allowance")
async def check_baggage_allowance(request: CheckBaggageAllowanceRequest, db = Depends(get_sync_db)):
    """Check baggage allowance"""
    try:
        result = await BaggageService.check_baggage_allowance(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Refund endpoints
@app.post("/initiate_refund")
async def initiate_refund(request: InitiateRefundRequest, db = Depends(get_sync_db)):
    """Initiate refund process"""
    try:
        result = await RefundService.initiate_refund(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Customer service endpoints
@app.post("/escalate_to_human_agent")
async def escalate_to_human_agent(request: EscalateToHumanAgentRequest, db = Depends(get_sync_db)):
    """Escalate to human agent"""
    try:
        result = await CustomerServiceService.escalate_to_human_agent(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional utility endpoints that can be implemented similarly
@app.post("/change_flight")
async def change_flight(request: ChangeFlightRequest, db = Depends(get_sync_db)):
    """Change flight booking"""
    try:
        # Implement flight change logic
        result = {
            "status": "success",
            "message": "Flight change request processed",
            "new_flight_details": {
                "flight_number": request.new_flight,
                "change_fee": request.change_fee,
                "new_departure": request.new_departure_time
            }
        }
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_arrival_time")
async def check_arrival_time(request: CheckArrivalTimeRequest, db = Depends(get_sync_db)):
    """Check flight arrival time"""
    try:
        result = await FlightService.check_flight_status(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_departure_time")
async def check_departure_time(request: CheckDepartureTimeRequest, db = Depends(get_sync_db)):
    """Check flight departure time"""
    try:
        result = await FlightService.check_flight_status(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add all other endpoint implementations
@app.post("/get_trip_cancellation_policy")
async def get_trip_cancellation_policy(request: GetTripCancellationPolicyRequest, db = Depends(get_sync_db)):
    """Get trip cancellation policy"""
    try:
        result = await PolicyService.query_policy(db, {"query": "trip cancellation policy"})
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cancel_trip")
async def cancel_trip(request: CancelTripRequest, db = Depends(get_sync_db)):
    """Cancel trip"""
    try:
        result = await RefundService.initiate_refund(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_trip_details")
async def check_trip_details(request: CheckTripDetailsRequest, db = Depends(get_sync_db)):
    """Check trip details"""
    try:
        # Implement trip details check
        result = {
            "booking_reference": request.booking_reference,
            "destination": request.destination,
            "trip_dates": {
                "start": request.trip_start_date,
                "end": request.trip_end_date
            },
            "status": "confirmed",
            "package_details": "Cultural tour package with guided activities"
        }
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_trip_insurance_coverage")
async def check_trip_insurance_coverage(request: CheckTripInsuranceCoverageRequest, db = Depends(get_sync_db)):
    """Check trip insurance coverage"""
    try:
        result = {
            "policy_number": request.policy_number,
            "coverage_active": True,
            "coverage_details": {
                "trip_cancellation": "$5,000",
                "medical_emergency": "$50,000",
                "baggage_protection": "$1,500"
            },
            "claim_process": "Call 1-800-CLAIM-HJ to initiate claim"
        }
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_flight_insurance_coverage")
async def check_flight_insurance_coverage(request: CheckFlightInsuranceCoverageRequest, db = Depends(get_sync_db)):
    """Check flight insurance coverage"""
    try:
        result = {
            "booking_reference": request.booking_reference,
            "policy_active": True,
            "coverage_amount": "$2,500",
            "benefits": [
                "Flight cancellation coverage",
                "Flight delay compensation",
                "Missed connection protection"
            ]
        }
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_flight_offers")
async def check_flight_offers(request: CheckFlightOffersRequest, db = Depends(get_sync_db)):
    """Check flight offers and deals"""
    try:
        result = {
            "origin": request.origin,
            "destination": request.destination,
            "current_offers": [
                {
                    "offer_type": "Early Bird Special",
                    "discount": "15% off",
                    "valid_until": "2025-08-31",
                    "conditions": "Book 30 days in advance"
                },
                {
                    "offer_type": "Weekend Getaway",
                    "discount": "$100 off",
                    "valid_until": "2025-07-31",
                    "conditions": "Minimum 3-day stay"
                }
            ],
            "recommended_dates": ["2025-09-15", "2025-09-22", "2025-10-05"]
        }
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_trip_offers")
async def check_trip_offers(request: CheckTripOffersRequest, db = Depends(get_sync_db)):
    """Check trip package offers"""
    try:
        result = await TripService.search_trip(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_trip_plan")
async def check_trip_plan(request: CheckTripPlanRequest, db = Depends(get_sync_db)):
    """Check trip plan details"""
    try:
        result = {
            "booking_reference": request.booking_reference,
            "destination": request.destination,
            "itinerary": [
                {"day": 1, "activity": "Arrival and hotel check-in"},
                {"day": 2, "activity": "City tour and museum visits"},
                {"day": 3, "activity": "Cultural experiences"},
                {"day": 4, "activity": "Free time and shopping"},
                {"day": 5, "activity": "Departure"}
            ],
            "included_services": ["Hotel accommodation", "Daily breakfast", "Guided tours"],
            "contact_info": "Local guide: +34-xxx-xxx-xxxx"
        }
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_trip_prices")
async def check_trip_prices(request: CheckTripPricesRequest, db = Depends(get_sync_db)):
    """Check trip prices"""
    try:
        result = {
            "destination": request.destination,
            "date_range": f"{request.start_date} to {request.end_date}",
            "price_options": [
                {"package": "Budget Explorer", "price": 899, "includes": ["Flight", "3-star hotel"]},
                {"package": "Comfort Plus", "price": 1299, "includes": ["Flight", "4-star hotel", "Some meals"]},
                {"package": "Luxury Experience", "price": 1899, "includes": ["Flight", "5-star hotel", "All meals", "Private tours"]}
            ]
        }
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_trip_prices")
async def search_trip_prices(request: SearchTripPricesRequest, db = Depends(get_sync_db)):
    """Search trip prices"""
    try:
        result = await TripService.search_trip(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/change_trip")
async def change_trip(request: ChangeTripRequest, db = Depends(get_sync_db)):
    """Change trip booking"""
    try:
        result = {
            "booking_reference": request.booking_reference,
            "changes_applied": {
                "new_destination": request.new_destination,
                "new_dates": f"{request.new_departure_date} to {request.new_return_date}",
                "added_activities": request.add_activities if hasattr(request, 'add_activities') else [],
                "removed_activities": request.remove_activities if hasattr(request, 'remove_activities') else []
            },
            "additional_fees": 150.00,
            "new_total": 1449.00,
            "confirmation": "Trip changes confirmed"
        }
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_cancellation_fee")
async def check_cancellation_fee(request: CheckCancellationFeeRequest, db = Depends(get_sync_db)):
    """Check cancellation fees"""
    try:
        result = await PolicyService.query_policy(db, {"query": "cancellation fee policy"})
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/purchase_trip_insurance")
async def purchase_trip_insurance(request: PurchaseTripInsuranceRequest, db = Depends(get_sync_db)):
    """Purchase trip insurance"""
    try:
        result = await InsuranceService.purchase_flight_insurance(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_trip_insurance")
async def search_trip_insurance(request: SearchTripInsuranceRequest, db = Depends(get_sync_db)):
    """Search trip insurance options"""
    try:
        result = await InsuranceService.search_flight_insurance(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Check-in related endpoints
@app.post("/check_in")
async def check_in(request: CheckInRequest, db = Depends(get_sync_db)):
    """Basic check-in"""
    try:
        result = await CheckInService.check_in_passenger(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_flight_checkin_status")
async def check_flight_checkin_status(request: CheckFlightCheckinStatusRequest, db = Depends(get_sync_db)):
    """Check flight check-in status"""
    try:
        result = {
            "booking_reference": request.booking_reference,
            "flight_number": request.flight_number,
            "check_in_status": "completed",
            "boarding_pass_issued": True,
            "seat_assignment": "12A",
            "gate": "B15",
            "boarding_time": "07:30"
        }
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_boarding_pass_pdf")
async def get_boarding_pass_pdf(request: GetBoardingPassPdfRequest, db = Depends(get_sync_db)):
    """Get boarding pass PDF"""
    try:
        result = await CheckInService.get_boarding_pass(db, request.dict())
        result["data"]["format"] = "PDF"
        result["data"]["download_link"] = f"https://hopjetair.com/boarding-pass-pdf/{request.booking_reference}"
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send_boarding_pass_email")
async def send_boarding_pass_email(request: SendBoardingPassEmailRequest, db = Depends(get_sync_db)):
    """Send boarding pass via email"""
    try:
        result = {
            "booking_reference": request.booking_reference,
            "passenger_name": request.passenger_name,
            "email_sent": True,
            "email_address": "passenger@example.com",
            "sent_at": "2025-07-14T10:30:00Z",
            "message": "Boarding pass sent successfully to your email"
        }
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error handling for unimplemented endpoints
async def not_implemented_handler(request, db):
    """Generic handler for endpoints not yet fully implemented"""
    return {
        "status": "success", 
        "message": "Request processed successfully",
        "data": {"note": "This endpoint is functional but returns simulated data for demo purposes"}
    }

# Add remaining endpoints with basic implementations
endpoint_mappings = [
    ("/get_trip_segments", "GetTripSegmentsRequest"),
    ("/get_excursion_cancellation_policy", "GetExcursionCancellationPolicyRequest"),
    ("/check_excursion_availability", "CheckExcursionAvailabilityRequest"),
    ("/book_excursion", "BookExcursionRequest"),
    ("/query_flight_availability", "QueryFlightAvailabilityRequest"),
    ("/check_flight_availability_and_fare", "CheckFlightAvailabilityAndFareRequest"),
    ("/confirm_flight_change", "ConfirmFlightChangeRequest"),
    ("/get_airline_checkin_baggage_info", "GetAirlineCheckinBaggageInfoRequest"),
    ("/resend_boarding_pass", "ResendBoardingPassRequest"),
    ("/get_check_in_info", "GetCheckInInfoRequest"),
    ("/query_airport_checkin_info", "QueryAirportCheckinInfoRequest"),
    ("/schedule_callback", "ScheduleCallbackRequest"),
    ("/get_phone_checkin_info", "GetPhoneCheckinInfoRequest"),
    ("/retrieve_booking_by_email", "RetrieveBookingByEmailRequest"),
    ("/get_flight_status", "GetFlightStatusRequest"),
    ("/book_activity", "BookActivityRequest"),
    ("/send_itinerary_email", "SendItineraryEmailRequest"),
    ("/send_email", "SendEmailRequest"),
    ("/get_refund", "GetRefundRequest"),
    ("/query_booking_details", "QueryBookingDetailsRequest"),
    ("/check_refund_eligibility", "CheckRefundEligibilityRequest"),
    ("/update_refund_method", "UpdateRefundMethodRequest"),
    ("/query_compensation_eligibility", "QueryCompensationEligibilityRequest"),
    ("/issue_travel_credit_voucher", "IssueTravelCreditVoucherRequest"),
    ("/issue_travel_voucher", "IssueTravelVoucherRequest"),
    ("/update_flight_date", "UpdateFlightDateRequest"),
    ("/verify_booking_and_get_boarding_pass", "VerifyBookingAndGetBoardingPassRequest"),
    ("/retrieve_flight_insurance", "RetrieveFlightInsuranceRequest")
]

# Auto-generate simple endpoints for remaining functionality
for endpoint, request_class in endpoint_mappings:
    def make_endpoint(endpoint_name):
        async def endpoint_func(request_data: dict, db = Depends(get_sync_db)):
            try:
                result = await not_implemented_handler(request_data, db)
                return {"status": "success", "data": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        return endpoint_func
    
    # Register the endpoint
    app.add_api_route(endpoint, make_endpoint(endpoint), methods=["POST"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)time")
async def check_departure_