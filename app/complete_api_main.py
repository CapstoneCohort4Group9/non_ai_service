from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from contextlib import asynccontextmanager
from database_connection import init_database, close_database, get_db_session
from database_models import SessionLocal

# Import all service modules
from flight_services import FlightSearchService, FlightStatusService, FlightAvailabilityService, FlightBookingService, FlightChangeService
from booking_services import BookingManagementService, BookingCancellationService, BookingModificationService, TimeCheckServices
from seat_checkin_services import SeatManagementService, CheckInService, BoardingPassService, CheckInInfoService
from trip_insurance_services import TripPackageService, InsuranceService
from support_pricing_services import CustomerSupportService, PolicyQueryService, BaggageService, RefundService, PricingService

# Keep all your existing Pydantic models
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

# [Continue with all other existing Pydantic models from your original file...]

# Lifespan context manager
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
        "status": "operational",
        "endpoints": "Visit /docs for complete API documentation"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from database_connection import check_database_health
    
    db_healthy = await check_database_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "timestamp": datetime.now().isoformat(),
        "services": "all_operational" if db_healthy else "degraded"
    }

# FLIGHT SERVICES (10 endpoints)
@app.post("/search_flight")
async def search_flight(request: SearchFlightRequest, db = Depends(get_sync_db)):
    """Search for available flights"""
    try:
        result = await FlightSearchService.search_flight(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_departure_time")
async def check_departure_time(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check departure time"""
    try:
        result = await TimeCheckServices.check_departure_time(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update_flight_date")
async def update_flight_date(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Update flight date"""
    try:
        result = await FlightChangeService.update_flight_date(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# SEAT & CHECK-IN SERVICES (12 endpoints)
@app.post("/check_seat_availability")
async def check_seat_availability(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check seat availability"""
    try:
        result = await SeatManagementService.check_seat_availability(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/change_seat")
async def change_seat(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Change seat assignment"""
    try:
        result = await SeatManagementService.change_seat(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/choose_seat")
async def choose_seat(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Choose seat"""
    try:
        result = await SeatManagementService.choose_seat(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_in_passenger")
async def check_in_passenger(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check in passenger"""
    try:
        result = await CheckInService.check_in_passenger(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_in")
async def check_in(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Basic check-in"""
    try:
        result = await CheckInService.check_in(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_flight_checkin_status")
async def check_flight_checkin_status(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check flight check-in status"""
    try:
        result = await CheckInService.check_flight_checkin_status(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_boarding_pass")
async def get_boarding_pass(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Get boarding pass"""
    try:
        result = await BoardingPassService.get_boarding_pass(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_boarding_pass_pdf")
async def get_boarding_pass_pdf(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Get boarding pass PDF"""
    try:
        result = await BoardingPassService.get_boarding_pass_pdf(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send_boarding_pass_email")
async def send_boarding_pass_email(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Send boarding pass via email"""
    try:
        result = await BoardingPassService.send_boarding_pass_email(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify_booking_and_get_boarding_pass")
async def verify_booking_and_get_boarding_pass(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Verify booking and get boarding pass"""
    try:
        result = await BoardingPassService.verify_booking_and_get_boarding_pass(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_check_in_info")
async def get_check_in_info(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Get check-in information"""
    try:
        result = await CheckInInfoService.get_check_in_info(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query_airport_checkin_info")
async def query_airport_checkin_info(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Query airport check-in info"""
    try:
        result = await CheckInInfoService.query_airport_checkin_info(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# TRIP & INSURANCE SERVICES (12 endpoints)
@app.post("/search_trip")
async def search_trip(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Search trip packages"""
    try:
        result = await TripPackageService.search_trip(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/book_trip")
async def book_trip(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Book trip package"""
    try:
        result = await TripPackageService.book_trip(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_trip_details")
async def check_trip_details(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check trip details"""
    try:
        result = await TripPackageService.check_trip_details(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_trip_offers")
async def check_trip_offers(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check trip offers"""
    try:
        result = await TripPackageService.check_trip_offers(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_flight_insurance")
async def search_flight_insurance(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Search flight insurance"""
    try:
        result = await InsuranceService.search_flight_insurance(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/purchase_flight_insurance")
async def purchase_flight_insurance(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Purchase flight insurance"""
    try:
        result = await InsuranceService.purchase_flight_insurance(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_trip_insurance")
async def search_trip_insurance(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Search trip insurance"""
    try:
        result = await InsuranceService.search_trip_insurance(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/purchase_trip_insurance")
async def purchase_trip_insurance(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Purchase trip insurance"""
    try:
        result = await InsuranceService.purchase_trip_insurance(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_flight_insurance_coverage")
async def check_flight_insurance_coverage(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check flight insurance coverage"""
    try:
        result = await InsuranceService.check_flight_insurance_coverage(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_trip_insurance_coverage")
async def check_trip_insurance_coverage(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check trip insurance coverage"""
    try:
        result = await InsuranceService.check_flight_insurance_coverage(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/retrieve_flight_insurance")
async def retrieve_flight_insurance(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Retrieve flight insurance"""
    try:
        result = await InsuranceService.check_flight_insurance_coverage(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PRICING SERVICES (8 endpoints)
@app.post("/search_flight_prices")
async def search_flight_prices(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Search flight prices"""
    try:
        result = await PricingService.search_flight_prices(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_flight_prices")
async def check_flight_prices(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check flight prices"""
    try:
        result = await PricingService.search_flight_prices(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_flight_offers")
async def check_flight_offers(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check flight offers"""
    try:
        result = await PricingService.check_flight_offers(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_trip_prices")
async def check_trip_prices(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check trip prices"""
    try:
        result = await PricingService.search_flight_prices(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_trip_prices")
async def search_trip_prices(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Search trip prices"""
    try:
        result = await TripPackageService.search_trip(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# SUPPORT & POLICY SERVICES (15 endpoints)
@app.post("/escalate_to_human_agent")
async def escalate_to_human_agent(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Escalate to human agent"""
    try:
        result = await CustomerSupportService.escalate_to_human_agent(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedule_callback")
async def schedule_callback(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Schedule callback"""
    try:
        result = await CustomerSupportService.schedule_callback(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query_policy_rag_db")
async def query_policy_rag_db(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Query airline policies"""
    try:
        result = await PolicyQueryService.query_policy_rag_db(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_cancellation_fee")
async def check_cancellation_fee(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check cancellation fees"""
    try:
        result = await PolicyQueryService.check_cancellation_fee(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_baggage_allowance")
async def check_baggage_allowance(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check baggage allowance"""
    try:
        result = await BaggageService.check_baggage_allowance(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/initiate_refund")
async def initiate_refund(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Initiate refund"""
    try:
        result = await RefundService.initiate_refund(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_refund_eligibility")
async def check_refund_eligibility(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check refund eligibility"""
    try:
        result = await RefundService.check_refund_eligibility(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ADDITIONAL ENDPOINTS (remaining ones with basic implementations)
@app.post("/cancel_trip")
async def cancel_trip(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Cancel trip"""
    try:
        result = await RefundService.initiate_refund(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/change_trip") 
async def change_trip(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Change trip booking"""
    try:
        result = {
            "status": "success",
            "booking_reference": request.get('booking_reference'),
            "changes_applied": {
                "new_destination": request.get('new_destination'),
                "new_dates": f"{request.get('new_departure_date')} to {request.get('new_return_date')}",
            },
            "additional_fees": 150.00,
            "confirmation": "Trip changes confirmed"
        }
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_trip_plan")
async def check_trip_plan(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check trip plan"""
    try:
        result = await TripPackageService.check_trip_details(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Generic handler for remaining endpoints
async def generic_endpoint_handler(request: Dict[str, Any], endpoint_name: str):
    """Generic handler for remaining endpoints"""
    return {
        "status": "success",
        "endpoint": endpoint_name,
        "message": f"{endpoint_name} processed successfully",
        "data": {
            "note": "This endpoint is functional but returns simulated data for demo purposes",
            "request_received": bool(request),
            "timestamp": datetime.now().isoformat()
        }
    }

# List of remaining endpoints to auto-generate
remaining_endpoints = [
    "get_trip_segments", "get_excursion_cancellation_policy", "check_excursion_availability",
    "book_excursion", "book_activity", "get_trip_cancellation_policy", "send_email",
    "resend_boarding_pass", "get_airline_checkin_baggage_info", "get_phone_checkin_info",
    "get_refund", "update_refund_method", "query_compensation_eligibility", 
    "issue_travel_credit_voucher", "issue_travel_voucher", "query_booking_details"
]

# Auto-generate endpoints
for endpoint in remaining_endpoints:
    def make_endpoint(name):
        async def endpoint_func(request: Dict[str, Any], db = Depends(get_sync_db)):
            try:
                result = await generic_endpoint_handler(request, name)
                return {"status": "success", "data": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        return endpoint_func
    
    app.add_api_route(f"/{endpoint}", make_endpoint(endpoint), methods=["POST"])

@app.get("/api/stats")
async def api_stats():
    """API statistics and endpoint summary"""
    return {
        "total_endpoints": len([route for route in app.routes if hasattr(route, 'methods') and 'POST' in route.methods]),
        "service_categories": {
            "flight_services": 10,
            "booking_services": 10, 
            "seat_checkin_services": 12,
            "trip_insurance_services": 12,
            "pricing_services": 8,
            "support_policy_services": 15,
            "additional_endpoints": len(remaining_endpoints)
        },
        "status": "All services operational",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) detail=str(e))

@app.post("/search_flights")
async def search_flights(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Advanced flight search"""
    try:
        result = await FlightSearchService.search_flights(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/book_flight")
async def book_flight(request: BookFlightRequest, db = Depends(get_sync_db)):
    """Book a flight"""
    try:
        result = await FlightBookingService.book_flight(db, request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_flight_status")
async def check_flight_status(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check flight status"""
    try:
        result = await FlightStatusService.check_flight_status(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_flight_status")
async def get_flight_status(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Alternative flight status endpoint"""
    try:
        result = await FlightStatusService.get_flight_status(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_flight_availability")
async def check_flight_availability(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check flight availability"""
    try:
        result = await FlightAvailabilityService.check_flight_availability(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query_flight_availability")
async def query_flight_availability(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Query flight availability"""
    try:
        result = await FlightAvailabilityService.query_flight_availability(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_flight_availability_and_fare")
async def check_flight_availability_and_fare(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check availability and fare"""
    try:
        result = await FlightAvailabilityService.check_flight_availability_and_fare(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/change_flight")
async def change_flight(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Change flight booking"""
    try:
        result = await FlightChangeService.change_flight(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/confirm_flight_change")
async def confirm_flight_change(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Confirm flight change"""
    try:
        result = await FlightChangeService.confirm_flight_change(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# BOOKING SERVICES (10 endpoints)
@app.post("/get_booking_details")
async def get_booking_details(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Get booking details"""
    try:
        result = await BookingManagementService.get_booking_details(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_flight_reservation")
async def check_flight_reservation(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check flight reservation"""
    try:
        result = await BookingManagementService.check_flight_reservation(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query_booking_details")
async def query_booking_details(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Query booking details"""
    try:
        result = await BookingManagementService.query_booking_details(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/retrieve_booking_by_email")
async def retrieve_booking_by_email(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Retrieve booking by email"""
    try:
        result = await BookingManagementService.retrieve_booking_by_email(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cancel_booking")
async def cancel_booking(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Cancel booking"""
    try:
        result = await BookingCancellationService.cancel_booking(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send_itinerary_email")
async def send_itinerary_email(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Send itinerary email"""
    try:
        result = await BookingModificationService.send_itinerary_email(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_arrival_time")
async def check_arrival_time(request: Dict[str, Any], db = Depends(get_sync_db)):
    """Check arrival time"""
    try:
        result = await TimeCheckServices.check_arrival_time(db, request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500,