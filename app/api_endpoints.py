# api_endpoints.py

from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from typing import Optional, List, Dict, Any
import uvicorn
from contextlib import asynccontextmanager
from .database_connection import init_database, close_database, get_db_session
from .database_models import SessionLocal
from .service_registry import execute_service_endpoint, get_service_info, check_service_health

# Import all Pydantic models from the new file
from .request_models import (
    SearchFlightRequest, BookFlightRequest, BookTripRequest,
    GetTripCancellationPolicyRequest, CancelTripRequest, GetTripSegmentsRequest,
    GetExcursionCancellationPolicyRequest, CheckExcursionAvailabilityRequest, BookExcursionRequest,
    ChangeFlightRequest, QueryPolicyRagDbRequest, SearchFlightsRequest,
    GetBookingDetailsRequest, CheckFlightAvailabilityRequest, CancelBookingRequest,
    QueryFlightAvailabilityRequest, CheckFlightAvailabilityAndFareRequest, ConfirmFlightChangeRequest,
    CheckSeatAvailabilityRequest, ChangeSeatRequest, ChangeTripRequest,
    CheckArrivalTimeRequest, CheckBaggageAllowanceRequest, CheckCancellationFeeRequest,
    CheckDepartureTimeRequest, CheckFlightInsuranceCoverageRequest, CheckFlightOffersRequest,
    SearchFlightPricesRequest, CheckFlightPricesRequest, CheckFlightReservationRequest,
    SendItineraryEmailRequest, CheckFlightStatusRequest, GetBoardingPassRequest,
    CheckInRequest, CheckInPassengerRequest, GetAirlineCheckinBaggageInfoRequest,
    ResendBoardingPassRequest, GetCheckInInfoRequest, QueryAirportCheckinInfoRequest,
    ScheduleCallbackRequest, GetPhoneCheckinInfoRequest, RetrieveBookingByEmailRequest,
    GetFlightStatusRequest, CheckTripDetailsRequest, CheckTripInsuranceCoverageRequest,
    CheckTripOffersRequest, CheckTripPlanRequest, BookActivityRequest,
    CheckTripPricesRequest, SearchTripPricesRequest, ChooseSeatRequest,
    SendBoardingPassEmailRequest, SendEmailRequest, CheckFlightCheckinStatusRequest,
    InitiateRefundRequest, GetRefundRequest, QueryBookingDetailsRequest,
    CheckRefundEligibilityRequest, UpdateRefundMethodRequest, QueryCompensationEligibilityRequest,
    IssueTravelCreditVoucherRequest, IssueTravelVoucherRequest, EscalateToHumanAgentRequest,
    UpdateFlightDateRequest, GetBoardingPassPdfRequest, VerifyBookingAndGetBoardingPassRequest,
    PurchaseFlightInsuranceRequest, RetrieveFlightInsuranceRequest, PurchaseTripInsuranceRequest,
    SearchFlightInsuranceRequest, SearchTripRequest, SearchTripInsuranceRequest
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

# Main application endpoints
@app.get("/")
async def root():
    return {
        "message": "Welcome to HopJetAir Customer Service API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": 70,
        "documentation": "/docs"
    }

# region health
@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    from .database_connection import check_database_health

    db_healthy = await check_database_health()
    service_health = await check_service_health()

    return {
        "status": "healthy" if db_healthy and service_health["status"] == "healthy" else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "services": service_health,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/service-info")
async def service_information():
    """Get information about available services"""
    return get_service_info()

# endregion
# Generic endpoint handler using service registry
async def handle_endpoint(endpoint_name: str, request_data: dict, db):
    """Generic handler for all endpoints using service registry"""
    try:
        result = await execute_service_endpoint(endpoint_name, db, request_data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# region Flight-related endpoints 8
@app.post("/search_flight")
async def search_flight(request: SearchFlightRequest, db = Depends(get_db_session)):
    """Search for available flights"""
    return await handle_endpoint("search_flight", request.dict(), db)

@app.post("/search_flights")
async def search_flights(request: SearchFlightsRequest, db = Depends(get_db_session)):
    """Search flights with advanced filters"""
    return await handle_endpoint("search_flights", request.dict(), db)

@app.post("/book_flight")
async def book_flight(request: BookFlightRequest, db = Depends(get_db_session)):
    """Book a flight"""
    return await handle_endpoint("book_flight", request.dict(), db)

@app.post("/check_flight_status")
async def check_flight_status(request: CheckFlightStatusRequest, db = Depends(get_db_session)):
    """Check flight status"""
    return await handle_endpoint("check_flight_status", request.dict(), db)

@app.post("/check_flight_availability")
async def check_flight_availability(request: CheckFlightAvailabilityRequest, db = Depends(get_db_session)):
    """Check flight availability"""
    return await handle_endpoint("check_flight_availability", request.dict(), db)

@app.post("/change_flight")
async def change_flight(request: ChangeFlightRequest, db = Depends(get_db_session)):
    """Change flight booking"""
    return await handle_endpoint("change_flight", request.dict(), db)

@app.post("/search_flight_prices")
async def search_flight_prices(request: SearchFlightPricesRequest, db = Depends(get_db_session)):
    """Search flight prices"""
    return await handle_endpoint("search_flight_prices", request.dict(), db)

@app.post("/check_flight_prices")
async def check_flight_prices(request: CheckFlightPricesRequest, db = Depends(get_db_session)):
    """Check flight prices"""
    return await handle_endpoint("check_flight_prices", request.dict(), db)
# endregion

# region Booking-related endpoints 6
@app.post("/get_booking_details")
async def get_booking_details(request: GetBookingDetailsRequest, db = Depends(get_db_session)):
    """Get booking details"""
    return await handle_endpoint("get_booking_details", request.dict(), db)

@app.post("/check_flight_reservation")
async def check_flight_reservation(request: CheckFlightReservationRequest, db = Depends(get_db_session)):
    """Check flight reservation"""
    return await handle_endpoint("check_flight_reservation", request.dict(), db)

@app.post("/cancel_booking")
async def cancel_booking(request: CancelBookingRequest, db = Depends(get_db_session)):
    """Cancel booking"""
    return await handle_endpoint("cancel_booking", request.dict(), db)

@app.post("/send_itinerary_email")
async def send_itinerary_email(request: SendItineraryEmailRequest, db = Depends(get_db_session)):
    """Send itinerary via email"""
    return await handle_endpoint("send_itinerary_email", request.dict(), db)

@app.post("/check_arrival_time")
async def check_arrival_time(request: CheckArrivalTimeRequest, db = Depends(get_db_session)):
    """Check flight arrival time"""
    return await handle_endpoint("check_arrival_time", request.dict(), db)

@app.post("/check_departure_time")
async def check_departure_time(request: CheckDepartureTimeRequest, db = Depends(get_db_session)):
    """Check flight departure time"""
    return await handle_endpoint("check_departure_time", request.dict(), db)
#endregion

# region Seat and Check-in endpoints 9
@app.post("/check_seat_availability")
async def check_seat_availability(request: CheckSeatAvailabilityRequest, db = Depends(get_db_session)):
    """Check seat availability"""
    return await handle_endpoint("check_seat_availability", request.dict(), db)

@app.post("/change_seat")
async def change_seat(request: ChangeSeatRequest, db = Depends(get_db_session)):
    """Change seat assignment"""
    return await handle_endpoint("change_seat", request.dict(), db)

@app.post("/choose_seat")
async def choose_seat(request: ChooseSeatRequest, db = Depends(get_db_session)):
    """Choose seat"""
    return await handle_endpoint("choose_seat", request.dict(), db)

@app.post("/check_in_passenger")
async def check_in_passenger(request: CheckInPassengerRequest, db = Depends(get_db_session)):
    """Check in passenger"""
    return await handle_endpoint("check_in_passenger", request.dict(), db)

@app.post("/check_in")
async def check_in(request: CheckInRequest, db = Depends(get_db_session)):
    """Basic check-in"""
    return await handle_endpoint("check_in", request.dict(), db)

@app.post("/get_boarding_pass")
async def get_boarding_pass(request: GetBoardingPassRequest, db = Depends(get_db_session)):
    """Get boarding pass"""
    return await handle_endpoint("get_boarding_pass", request.dict(), db)

@app.post("/get_boarding_pass_pdf")
async def get_boarding_pass_pdf(request: GetBoardingPassPdfRequest, db = Depends(get_db_session)):
    """Get boarding pass PDF"""
    return await handle_endpoint("get_boarding_pass_pdf", request.dict(), db)

@app.post("/send_boarding_pass_email")
async def send_boarding_pass_email(request: SendBoardingPassEmailRequest, db = Depends(get_db_session)):
    """Send boarding pass via email"""
    return await handle_endpoint("send_boarding_pass_email", request.dict(), db)

@app.post("/check_flight_checkin_status")
async def check_flight_checkin_status(request: CheckFlightCheckinStatusRequest, db = Depends(get_db_session)):
    """Check flight check-in status"""
    return await handle_endpoint("check_flight_checkin_status", request.dict(), db)
# endregion

# region Trip and Package endpoints 4
@app.post("/search_trip")
async def search_trip(request: SearchTripRequest, db = Depends(get_db_session)):
    """Search trip packages"""
    return await handle_endpoint("search_trip", request.dict(), db)

@app.post("/book_trip")
async def book_trip(request: BookTripRequest, db = Depends(get_db_session)):
    """Book trip package"""
    return await handle_endpoint("book_trip", request.dict(), db)

@app.post("/check_trip_details")
async def check_trip_details(request: CheckTripDetailsRequest, db = Depends(get_db_session)):
    """Check trip details"""
    return await handle_endpoint("check_trip_details", request.dict(), db)

@app.post("/check_trip_offers")
async def check_trip_offers(request: CheckTripOffersRequest, db = Depends(get_db_session)):
    """Check trip offers"""
    return await handle_endpoint("check_trip_offers", request.dict(), db)
#endregion

# region Insurance endpoints 5
@app.post("/search_flight_insurance")
async def search_flight_insurance(request: SearchFlightInsuranceRequest, db = Depends(get_db_session)):
    """Search flight insurance options"""
    return await handle_endpoint("search_flight_insurance", request.dict(), db)

@app.post("/purchase_flight_insurance")
async def purchase_flight_insurance(request: PurchaseFlightInsuranceRequest, db = Depends(get_db_session)):
    """Purchase flight insurance"""
    return await handle_endpoint("purchase_flight_insurance", request.dict(), db)

@app.post("/search_trip_insurance")
async def search_trip_insurance(request: SearchTripInsuranceRequest, db = Depends(get_db_session)):
    """Search trip insurance options"""
    return await handle_endpoint("search_trip_insurance", request.dict(), db)

@app.post("/purchase_trip_insurance")
async def purchase_trip_insurance(request: PurchaseTripInsuranceRequest, db = Depends(get_db_session)):
    """Purchase trip insurance"""
    return await handle_endpoint("purchase_trip_insurance", request.dict(), db)

@app.post("/check_flight_insurance_coverage")
async def check_flight_insurance_coverage(request: CheckFlightInsuranceCoverageRequest, db = Depends(get_db_session)):
    """Check flight insurance coverage"""
    return await handle_endpoint("check_flight_insurance_coverage", request.dict(), db)
#endregion

# region Support and Policy endpoints 6
@app.post("/query_policy_rag_db")
async def query_policy_rag_db(request: QueryPolicyRagDbRequest, db = Depends(get_db_session)):
    """Query airline policies"""
    return await handle_endpoint("query_policy_rag_db", request.dict(), db)

@app.post("/escalate_to_human_agent")
async def escalate_to_human_agent(request: EscalateToHumanAgentRequest, db = Depends(get_db_session)):
    """Escalate to human agent"""
    return await handle_endpoint("escalate_to_human_agent", request.dict(), db)

@app.post("/schedule_callback")
async def schedule_callback(request: ScheduleCallbackRequest, db = Depends(get_db_session)):
    """Schedule customer service callback"""
    return await handle_endpoint("schedule_callback", request.dict(), db)

@app.post("/initiate_refund")
async def initiate_refund(request: InitiateRefundRequest, db = Depends(get_db_session)):
    """Initiate refund process"""
    return await handle_endpoint("initiate_refund", request.dict(), db)

@app.post("/check_refund_eligibility")
async def check_refund_eligibility(request: CheckRefundEligibilityRequest, db = Depends(get_db_session)):
    """Check refund eligibility"""
    return await handle_endpoint("check_refund_eligibility", request.dict(), db)

@app.post("/check_baggage_allowance")
async def check_baggage_allowance(request: CheckBaggageAllowanceRequest, db = Depends(get_db_session)):
    """Check baggage allowance"""
    return await handle_endpoint("check_baggage_allowance", request.dict(), db)

#endregion

# Auto-generate remaining endpoints using service registry 35
remaining_endpoints = [
    "get_trip_cancellation_policy", "cancel_trip", "get_trip_segments",
    "get_excursion_cancellation_policy", "check_excursion_availability", "book_excursion",
    "query_flight_availability", "check_flight_availability_and_fare", "confirm_flight_change",
    "get_airline_checkin_baggage_info", "resend_boarding_pass", "get_check_in_info",
    "query_airport_checkin_info", "get_phone_checkin_info", "retrieve_booking_by_email",
    "get_flight_status", "check_trip_insurance_coverage", "check_trip_plan", "book_activity",
    "check_trip_prices", "search_trip_prices", "change_trip", "cancel_trip", "send_email",
    "get_refund", "query_booking_details", "update_refund_method", "query_compensation_eligibility",
    "issue_travel_credit_voucher", "issue_travel_voucher", "update_flight_date",
    "verify_booking_and_get_boarding_pass", "retrieve_flight_insurance", "check_flight_offers",
    "check_cancellation_fee"
]

# Dynamically create remaining endpoints
for endpoint_name in remaining_endpoints:
    def make_endpoint(name):
        async def endpoint_func(request_data: dict, db = Depends(get_db_session)):
            return await handle_endpoint(name, request_data, db)
        return endpoint_func

    # Register the endpoint
    app.add_api_route(f"/{endpoint_name}", make_endpoint(endpoint_name), methods=["POST"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)