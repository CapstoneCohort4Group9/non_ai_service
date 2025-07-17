from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from contextlib import asynccontextmanager
from .database_connection import init_database, close_database, get_db_session
from .database_models import SessionLocal
from .service_registry import execute_service_endpoint, get_service_info, check_service_health

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

# region Request Keep your existing Pydantic models as they are
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

class BookTripRequest(BaseModel):
    origin: str = "Boston"
    destination: str = "Madrid"
    departure_date: str = "2025-09-10"
    return_date: str = "2025-09-17"
    passengers: List[Any] = [{'type': 'adult', 'count': 2}]
    trip_type: str = "round-trip"
    preferences: Dict[str, Any] = {'lodging': 'comfortable', 'budget': 'moderate'}
    activities: List[Any] = ['hiking', 'wildlife watching']
    trip_category: str = "excursion"
    excursion_type: str = "cultural tour - art museums"
    travel_style: str = "relaxing"
    budget: str = "mid-range"
    interests: List[Any] = ['art', 'history']
    experience: str = "relaxing beach vacation"
    accommodation_preference: str = "cozy"
    classname: str = "economy"
    excursion: str = "Colosseum and Roman Forum guided tour"
    budget_per_person: int = 200
    accommodation: str = "hotel"
    package: str = "Madrid Historical Tour"
    experience_type: str = "adventurous nature"
    trip_preferences: Dict[str, Any] = {'type': 'cultural sightseeing', 'activities': ['art museums', 'flamenco show', 'tapas tour']}
    trip_purpose: str = "excursion"
    activity_type: str = "hiking"
    include_hotel: bool = True
    duration: str = "full-day"
    trip_duration_days: int = 5
    special_sites: List[Any] = ['Prado Museum', 'Retiro Park']

class GetTripCancellationPolicyRequest(BaseModel):
    booking_reference: str = "MAD43210"
    booking_date: str = "2023-03-15"
    name: str = "Emily Clark"
    date_of_birth: str = "1985-03-12"

class CancelTripRequest(BaseModel):
    booking_reference: str = "MAD43210"
    trip_dates: Dict[str, Any] = {'arrival': '2024-07-10', 'departure': '2024-07-15'}
    travel_dates: str = "July 10th to July 17th, 2024"
    departure_date: str = "2024-07-20"
    cancellation_reason: str = "personal reasons"
    last_name: str = "Johnson"
    excursion_name: str = "Madrid City Highlights Tour"
    full_name: str = "John Smith"
    departure_city: str = "New York"
    destination: str = "Paris"
    booking_date: str = "2 months ago"
    refund_option: str = "full"
    name: str = "Alex Johnson"
    email: str = "alex.johnson@example.com"

class GetTripSegmentsRequest(BaseModel):
    booking_reference: str = "NYCCH1234"

class GetExcursionCancellationPolicyRequest(BaseModel):
    booking_reference: str = "EXC123456"

class CheckExcursionAvailabilityRequest(BaseModel):
    booking_reference: str = "EXC123456"
    new_departure_date: str = "2024-07-20"

class BookExcursionRequest(BaseModel):
    departure_date: str = "2024-07-20"

class ChangeFlightRequest(BaseModel):
    confirmation_number: str = "DEF456"
    departure_city: str = "New York"
    arrival_city: str = "Los Angeles"
    desired_date_range: str = "next week"
    booking_reference: str = "CHI789"
    new_travel_date: str = "2024-06-XX"
    new_date: str = "2024-06-25"
    new_time: str = "14:00"
    origin: str = "Chicago"
    destination: str = "Madrid"
    new_destination: str = "Chennai"
    airline: str = "Air India"
    new_departure_date: str = "2024-05-20"
    new_arrival_date: str = "2024-05-21"
    new_flight_date: str = "2024-07-18"
    new_flight_time: str = "08:00"
    fare_type: str = "Regular Economy"
    modification_type: str = "cancellation"
    new_classname: str = "business"
    change_type: str = "departure_date"
    flight_number: str = "AA123"
    date: str = "2024-07-10"
    new_flight: str = "IB456"
    change_fee: int = 75
    original_departure: str = "2024-07-10"
    original_arrival: str = "2024-07-11"
    preferred_new_dates: List[Any] = ['2024-07-14', '2024-07-15']
    airline_preference: str = ""
    new_flight_number: str = "NY456"
    new_departure_time: str = "2024-06-20T17:45:00"
    new_departure_date_offset_days: int = 2

class QueryPolicyRagDbRequest(BaseModel):
    query: str = "change fee and availability for booking DEF789 changing destination from New York to Boston on June 20th"

class SearchFlightsRequest(BaseModel):
    origin: str = "Chicago"
    destination: str = "Madrid"
    date: str = "2024-06-25"
    booking_reference: str = "HJK123"
    new_date: str = "2024-06-20"
    time_preference: str = "morning"
    departure_date_offset_days: int = 5
    date_range: str = "next week"
    origin_airports: List[Any] = ['ORD', 'MDW']
    departure_date_range: str = "2024-06-10 to 2024-06-16"
    earliest_departure_time: str = "15:00"
    frm: str = "Seattle"
    to: str = "Paris"
    start_date: str = "2024-07-10"
    end_date: str = "2024-07-20"
    preferred_time: str = "evening"
    departure_city: str = "Chicago"
    arrival_city: str = "Madrid"
    departure_date: str = "2024-07-10"
    return_date: str = "2024-07-20"
    travel_classname: str = "Economy"
    trip_type: str = "Round-trip"
    passengers: int = 3
    filters: Dict[str, Any] = {'nonstop': False, 'max_layovers': 1}
    budget: int = 700
    classname: str = "economy"
    departure_window: List[Any] = ['2025-10-20', '2025-10-30']
    max_price: int = 700
    preferences: Dict[str, Any] = {'budget_friendly': True}
    return_window: List[Any] = ['2025-09-25', '2025-09-30']
    sort_by: str = "price"

class GetBookingDetailsRequest(BaseModel):
    booking_reference: str = "NX2Z5S"
    passenger_name: str = "John Doe"

class CheckFlightAvailabilityRequest(BaseModel):
    origin: str = "Chicago"
    destination: str = "Madrid"
    date: str = "2024-06-05"
    frm: str = "Chicago"
    to: str = "Madrid"
    classname: str = "business"

class CancelBookingRequest(BaseModel):
    confirmation_number: str = "JD12345"

class QueryFlightAvailabilityRequest(BaseModel):
    origin: str = "Chicago"
    destination: str = "Madrid"
    date: str = "2024-07-20"
    time_of_day: str = "afternoon"

class CheckFlightAvailabilityAndFareRequest(BaseModel):
    booking_reference: str = "SHM456"
    new_date: str = "2024-05-15"

class ConfirmFlightChangeRequest(BaseModel):
    booking_reference: str = "CHI123"
    new_departure_date: str = "2024-07-14"

class CheckSeatAvailabilityRequest(BaseModel):
    booking_reference: str = "XYZ9876"
    flight_number: str = "BA256"
    seat_preference: str = "aisle"
    near_exit: bool = True
    flight_date: str = "2024-07-15"
    flight_time: str = "15:00"
    last_name: str = "Smith"

class ChangeSeatRequest(BaseModel):
    booking_reference: str = "XYZ9876"
    new_seat: str = "14C"

class ChangeTripRequest(BaseModel):
    booking_reference: str = "EXC12345"
    remove_excursion: str = "city tour"
    new_destination: str = "Lisbon"
    new_departure_date: str = "2025-07-20"
    new_return_date: str = "2025-05-12"
    activity_changes: Dict[str, Any] = {'remove': 'Prado Museum tour', 'add': 'cooking class'}
    hotel: str = "Hotel Gran Madrid"
    new_classname: str = "business"
    excursion_type: str = "guided city tour"
    excursion_location: str = "Rome"
    excursion_date: str = "2025-05-15"
    departure_location: str = "New York"
    travelers: int = 2
    remove_activities: List[Any] = ['hiking']
    excursion_name: str = "Jungle Safari Tour"
    new_excursion_date: str = "2024-06-15"
    preferred_flight_time: str = "evening"
    add_excursion: str = "guided city tour"
    hotel_upgrade: str = "5-star"
    new_excursion_destination: str = "Madrid"
    new_excursion_start_date: str = "2025-09-10"
    new_excursion_end_date: str = "2025-09-15"
    add_activities: List[Any] = ['guided city tour']
    excursion: str = "Tuscany countryside tour"
    cancel_trip: bool = True
    cancel: bool = True
    original_date: str = "2025-06-15"
    change_excursion: bool = True
    original_excursion: str = "Madrid City Tour"
    new_excursion: str = "Seville Day Tour"
    cancel_excursion: bool = True
    additional_passengers: int = 1

class CheckArrivalTimeRequest(BaseModel):
    flight_number: str = "BA249"
    date: str = "2025-06-05"
    booking_reference: str = "ABC123"
    last_name: str = "Johnson"
    destination: str = "London Heathrow"
    departure_city: str = "London"
    departure_airport: str = "San Francisco"
    destination_airport: str = "New York"
    airline: str = "British Airways"
    passenger_name: str = "Sarah Johnson"
    arrival_airport: str = "SFO"
    origin_airport: str = "LHR"

class CheckBaggageAllowanceRequest(BaseModel):
    booking_reference: str = "ABC123"
    classname: str = "economy"
    route_type: str = "international"
    airline: str = "JetBlue"
    destination: str = "New York"
    flight_number: str = "BA256"
    origin: str = "JFK"
    passenger_name: str = "John Smith"
    date: str = "2024-07-15"
    departure_city: str = "New York"
    departure_country: str = "USA"
    departure: str = "New York"
    checked_bags: int = 2
    carry_on_bags: int = 1
    extra_checked_bags: int = 1
    membership_status: str = "silver"
    membership: str = "JAL Mileage Bank"
    outbound_flight: str = "UA123"
    return_flight: str = "UA456"
    travel_date: str = "2024-07-15"
    departure_date: str = "2024-07-10"
    return_date: str = "2024-07-20"
    extra_baggage_info: bool = True
    arrival: str = "Los Angeles"

class CheckCancellationFeeRequest(BaseModel):
    booking_reference: str = "ABC123"
    ticket_classname: str = "Economy"
    route: str = "Miami to Dallas"
    booking_date: str = "two weeks ago"
    origin: str = "Miami"
    destination: str = "Paris"
    departure_date: str = "2024-07-15"
    flight_date: str = "2024-07-15"
    last_name: str = "Johnson"
    email: str = "johnson.family@example.com"
    trip_start_date: str = "2024-07-10"
    trip_end_date: str = "2024-07-20"
    trip_status: str = "departing in two days"
    booking_type: str = "hotel"
    departure_airport: str = "Miami"
    query: str = "early termination charges"
    trip_details: str = "Miami to San Francisco on May 10th"
    traveler_name: str = "John Doe"
    trip_type: str = "flight"
    fare_classname: str = "Economy"
    ticket_type: str = "non-refundable"
    early_termination: bool = True
    trip_dates: str = "2024-07-10 to 2024-07-15"
    termination_reason: str = "personal reasons"
    travel_type: str = "hotel"
    fee_type: str = "early termination"
    service_type: str = "rental car"
    query_type: str = "early termination fee"
    change_date: str = "2024-06-26"
    flight_route: str = "San Francisco to Tokyo"
    confirmation_number: str = "ABC123"
    travel_date: str = "2024-06-20"
    reference_number: str = "HTL12345"

class CheckDepartureTimeRequest(BaseModel):
    flight_number: str = "AA123"
    date: str = "2025-06-06"
    booking_reference: str = "ABC12345"
    airline: str = "United Airlines"
    passenger_name: str = "John Smith"
    last_name: str = "Thompson"
    departure_airport: str = "LAX"

class CheckFlightInsuranceCoverageRequest(BaseModel):
    booking_reference: str = "FLT789321"
    name: str = "John Doe"
    trip_type: str = "vacation"
    travel_dates: str = "2024-07-10 to 2024-07-20"
    destination: str = "Paris"
    policy_number: str = "INS789123"
    date: str = "2024-06-17"
    traveler_name: str = "John Doe"
    flight_number: str = "AB1234"
    id_last4: str = "6789"
    full_name: str = "Sarah Smith"
    last_name: str = "Johnson"
    airline: str = "American Airlines"
    flight_date: str = "2024-05-15"
    email: str = "john.doe@example.com"
    travel_start_date: str = "2024-05-10"
    travel_end_date: str = "2024-05-20"
    travel_type: str = "leisure"
    booking_date: str = "last week"
    trip_start_date: str = "2024-07-10"
    trip_end_date: str = "2024-07-20"
    trip_date: str = "2024-07-15"
    itinerary_reference: str = "AB123XYZ"

class CheckFlightOffersRequest(BaseModel):
    origin: str = "Chicago"
    destination: str = "Miami"
    start_date: str = "2025-06-20"
    end_date: str = "2025-06-30"
    traveler_count: int = 2
    month: str = "2025-09"
    passengers: int = 1
    preferred_time: str = "morning"
    departure_date: str = "2025-07-15"
    return_date: str = "2025-07-20"
    flight_type: str = "direct"
    cabin_classname: str = "economy"
    travelers: int = 1
    classname: str = "economy"
    max_price: int = 700
    trip_type: str = "round-trip"
    travel_month: str = "2025-09"
    airline_type: str = "budget"
    trip_length_days: int = 7
    passenger_count: int = 2
    price_range: int = 700
    travel_classname: str = "economy"
    budget: int = 700
    flight_classname: str = "economy"
    airline_preference: str = "none"
    stop_preference: str = "non-stop"
    direct_flights: bool = True
    max_budget: int = 700
    flight_preferences: Dict[str, Any] = {'non_stop': True}
    flexible_dates: bool = True
    detailed: bool = True
    date_range: Dict[str, Any] = {'start': '2025-07-10', 'end': '2025-07-20'}
    flexibility: str = "moderate"

class SearchFlightPricesRequest(BaseModel):
    origin: str = "Chicago"
    destination: str = "Madrid"
    departure_date: str = "2025-08-10"
    return_date: str = "2025-08-20"
    departure_date_range: List[Any] = ['2025-07-01', '2025-07-31']
    sort_by: str = "price"
    limit: int = 3
    passengers: Dict[str, Any] = {'adults': 1}
    direct_flight: bool = True
    cabin_classname: str = "economy"
    preferences: Dict[str, Any] = {'direct_flight': True}
    return_date_range: List[Any] = ['2025-08-13', '2025-08-27']
    trip_type: str = "roundtrip"
    nonstop: bool = True
    travel_classname: str = "economy"

class CheckFlightPricesRequest(BaseModel):
    origin: str = "Chicago"
    destination: str = "Amsterdam"
    departure_date: str = "2025-08-10"
    return_date: str = "2025-08-20"
    passengers: Dict[str, Any] = {'adults': 2}
    preferred_airlines: List[Any] = []
    departure_date_range: List[Any] = ['2025-08-08', '2025-08-12']
    return_date_range: List[Any] = ['2025-08-18', '2025-08-22']

class CheckFlightReservationRequest(BaseModel):
    last_name: str = "Anderson"
    departure_city: str = "Chicago"
    arrival_city: str = "Madrid"
    full_name: str = "Sarah Johnson"
    destination_city: str = "Denver"
    booking_reference: str = "CHI78945"
    email: str = "smith.jane@example.com"
    first_name: str = "Emily"
    date_of_birth: str = "1987-03-15"
    flight_number: str = ""
    departure_date: str = "2024-07-10"
    return_date: str = "2024-07-20"
    origin: str = "Chicago"
    destination: str = "Madrid"
    flight_date_range: Dict[str, Any] = {'start_date': '2024-07-10', 'end_date': '2024-07-15'}
    flight_date: str = "2024-07-20"
    travel_date: str = "2024-07-20"
    passenger_count: int = 1
    confirmation_number: str = "CHI7890"
    date_range: Dict[str, Any] = {'start_date': '2024-07-10', 'end_date': '2024-07-20'}
    travel_dates: List[Any] = ['2024-07-10', '2024-07-15']
    travel_start_date: str = "2024-07-05"
    travel_end_date: str = "2024-07-15"
    date_of_travel: str = "2024-07-20"
    travelers: int = 1
    preferences: Dict[str, Any] = {'direct_flight': True}
    travel_month_year: str = "July 2024"
    trip_date: str = "2024-07-20"
    date: str = "next Friday"

class SendItineraryEmailRequest(BaseModel):
    email: str = "anderson.family@email.com"
    booking_reference: str = "CHI789654"

class CheckFlightStatusRequest(BaseModel):
    flight_number: str = "DL4253"
    date: str = "2025-09-13"
    last_name: str = "Smith"
    origin: str = "ATL"
    destination: str = "JFK"
    airline: str = "Delta Airlines"
    confirmation_number: str = "XZ1234"
    departure_airport: str = "JFK"
    booking_reference: str = "FLT1234"
    destination_airport: str = "JFK"
    departure_city: str = "New York"
    arrival_city: str = "Los Angeles"
    arrival_airport: str = "SEA"
    destination_city: str = "Atlanta"

class GetBoardingPassRequest(BaseModel):
    booking_reference: str = "ATL7890"
    flight_number: str = "AA123"
    passenger_name: str = "John Doe"
    airline: str = "American Airlines"
    destination: str = "New York"
    flight_date: str = "2025-07-15"
    passenger_last_name: str = "Johnson"
    email: str = "user@example.com"
    confirmation_email: str = "johnson@example.com"
    departure_airport: str = "JFK"
    departure_datetime: str = "2025-07-15T15:00:00"
    reservation_id: str = "RZ7890"
    departure_city: str = "New York"
    last_name: str = "Johnson"
    departure_location: str = "London"
    arrival_city: str = "Los Angeles"
    departure_time: str = "10:00"
    flight_type: str = "domestic"
    travel_date: str = "2024-07-15"
    origin: str = "London"

class CheckInRequest(BaseModel):
    flight_number: str = "AA123"
    departure_airport: str = "JFK"
    airline: str = "American Airlines"
    destination: str = "Los Angeles"
    last_name: str = "Smith"
    confirmation_id: str = "X9Y8Z7"

class CheckInPassengerRequest(BaseModel):
    booking_reference: str = "ABC456"
    last_name: str = "Johnson"
    airline: str = "Delta"
    flight_number: str = "DL123"
    destination: str = "Atlanta"
    check_in_method: str = "phone"
    full_name: str = "Sarah Johnson"
    ssn_last4: str = "6789"
    confirmation_last4: str = "4821"
    travel_date: str = "tomorrow"
    confirmation_number: str = "ABCD45"
    departure_airport: str = "JFK"
    date_of_birth: str = "1985-07-21"

class GetAirlineCheckinBaggageInfoRequest(BaseModel):
    airline: str = "Delta"

class ResendBoardingPassRequest(BaseModel):
    email: str = "smith.j@example.com"

class GetCheckInInfoRequest(BaseModel):
    airport: str = "LAX"
    airline: str = "Delta Airlines"
    travel_date: str = "next Friday"
    booking_reference: str = "AB123C"
    last_name: str = "Johnson"
    departure_airport: str = "Atlanta Hartsfield-Jackson Airport"
    ticket_type: str = "economy"
    flight_number: str = "AB1234"

class QueryAirportCheckinInfoRequest(BaseModel):
    airport_code: str = "JFK"
    info_requested: List[Any] = ['check-in counters', 'baggage drop-off timings']

class ScheduleCallbackRequest(BaseModel):
    phone_number: str = "+1-555-789-1234"
    booking_reference: str = "AB123C"
    last_name: str = "Johnson"
    purpose: str = "phone check-in"

class GetPhoneCheckinInfoRequest(BaseModel):
    airline: str = "American Airlines"
    flight_number: str = "AA1234"

class RetrieveBookingByEmailRequest(BaseModel):
    email: str = "alex.jones@example.com"

class GetFlightStatusRequest(BaseModel):
    confirmation_number: str = "AB123X"

class CheckTripDetailsRequest(BaseModel):
    booking_reference: str = "EXC12345"
    last_name: str = "Garcia"
    destination: str = "Madrid"
    trip_start_date: str = "2024-07-10"
    trip_end_date: str = "2024-07-17"
    email: str = "garcia.family@example.com"
    name: str = "Laura Martinez"
    booking_date: str = "March 2024"
    excursion_name: str = "Adventure Safari"
    start_date: str = "2024-07-10"
    end_date: str = "2024-07-20"
    travel_start_date: str = "2024-09-10"
    travel_end_date: str = "2024-09-15"
    tour_name: str = "Rainforest Adventure"
    travel_dates: str = "2024-09-10 to 2024-09-17"

class CheckTripInsuranceCoverageRequest(BaseModel):
    booking_reference: str = "TRIP4567"
    last_name: str = "Johnson"
    policy_number: str = "TRIP456789"
    trip_itinerary: Dict[str, Any] = {'origin': 'New York', 'destination': 'Paris', 'start_date': '2024-06-10', 'end_date': '2024-06-20'}
    name: str = "Sarah Johnson"
    travel_dates: Dict[str, Any] = {'start': '2024-07-10', 'end': '2024-07-20'}
    full_name: str = "Sarah Johnson"
    booking_date: str = "2024-03-15"
    destination: str = "Bali"
    traveler_name: str = "Sarah Johnson"
    travel_start_date: str = "2024-03-10"
    travel_end_date: str = "2024-03-20"
    trip_start_date: str = "2024-07-10"
    trip_end_date: str = "2024-07-20"
    insurance_company: str = "SafeTravel"
    email: str = "jane.doe@example.com"
    start_date: str = "2024-07-10"
    end_date: str = "2024-07-24"
    trip_type: str = "vacation"
    trip_date: str = "2024-07-15"
    trip_dates: Dict[str, Any] = {'start': '2024-07-10', 'end': '2024-07-25'}
    policy_name: str = "Explorer Plus"
    purchase_date: str = "2024-03-15"
    issuer: str = "Global Travel Insurance"
    date_of_birth: str = "1990-05-15"
    departure_city: str = "New York"
    arrival_city: str = "Paris"
    travel_date: str = "2024-07-10"
    insurance_plan: str = "Premium Travel Shield"
    departure_date: str = "2024-08-15"
    return_date: str = "2024-08-30"

class CheckTripOffersRequest(BaseModel):
    category: str = "excursion"
    subcategory: str = "adventure"
    location: str = "Costa Rica"
    region: str = "Caribbean"
    date_range: Dict[str, Any] = {'start': '2024-07-20', 'end': '2024-07-31'}
    travelers: int = 2
    destination: str = "Jamaica"
    type: str = "beach"
    duration: int = 7
    travel_classname: str = "economy"
    categories: List[Any] = ['historical sites', 'art museums']
    budget: str = "moderate"
    city: str = "Madrid"
    interests: List[Any] = ['museums', 'flamenco']
    duration_days: int = 4
    group_size: int = 3
    excursion_name: str = "tapas and wine tasting"
    excursion_type: str = "historical, cultural"
    climate: str = "warm"
    destinations: List[Any] = ['Caribbean', 'Hawaii']
    travel_month: str = "September"
    travel_style: str = "budget"
    transportation: str = "flight"
    activities: List[Any] = ['cultural experiences', 'historical sites']
    package_type: str = "spa_resort"
    excursion: str = "Royal Palace guided tour"
    preferences: List[Any] = ['historical', 'cultural']
    traveler_type: str = "solo"
    budget_per_person: int = 1500
    hotel_type: str = "boutique"
    travel_dates: Dict[str, Any] = {'start': '2025-07-10', 'end': '2025-07-20'}
    budget_per_day: int = 150
    destination_type: str = "tropical"
    trip_length_days: int = 7
    duration_nights: int = 5
    budget_per_night: int = 150
    types: List[Any] = ['historical sites', 'cultural tours']
    activity_type: str = "guided city tour"
    offer_type: str = "bundle"
    offer_types: List[Any] = ['flight', 'hotel']
    max_budget: int = 200
    date: str = "2024-08-12"
    activity: str = "Prado Museum skip-the-line tickets"
    month: str = "2024-09"
    trip_type: str = "round_trip"
    travel_time: str = "next_month"
    sub_category: List[Any] = ['nature', 'adventure']
    traveler_count: int = 1
    travel_window: Dict[str, Any] = {'start': '2024-06-01', 'end': '2024-08-01'}
    travel_companions: str = "couple"
    season: str = "summer"
    price_range: str = "affordable"
    hotel_rating: str = "4-star"
    hotel_category: str = "mid_range"

class CheckTripPlanRequest(BaseModel):
    booking_reference: str = "EXC20249"
    traveler_name: str = "Alex Johnson"
    trip_start_date: str = "2024-05-10"
    trip_end_date: str = "2024-05-15"
    destination: str = "Madrid"
    last_name: str = "Garcia"
    travel_start_date: str = "2024-05-10"
    travel_end_date: str = "2024-05-17"
    booking_month: str = "March 2024"
    email: str = "johndoe@example.com"
    start_date: str = "2024-09-05"
    end_date: str = "2024-09-12"
    booking_name: str = "John Doe"
    travel_dates: Dict[str, Any] = {'start': '2024-07-10', 'end': '2024-07-17'}
    traveler_id: str = "XYZ12345678"
    departure_city: str = "New York"
    destination_city: str = "Madrid"
    travel_month: str = "next month"
    name: str = "John Doe"
    trip_dates: str = "September 12th to 15th"

class BookActivityRequest(BaseModel):
    booking_reference: str = "MAD2024X"
    activity: str = "guided walking tour"
    location: str = "Madrid"
    date: str = "July 12"

class CheckTripPricesRequest(BaseModel):
    destination: str = "Madrid"
    start_date: str = "2025-09-15"
    end_date: str = "2025-09-22"
    include: List[Any] = ['historical tours', 'cultural experiences']
    excursions: List[Any] = ['Colosseum tour', 'Roman food walking tour']
    origin: str = "New York"
    passengers: Dict[str, Any] = {'adults': 2}
    trip_type: str = "beach vacation"
    accommodation_preference: str = "comfort and affordability"
    excursion_types: List[Any] = ['city tours', 'cultural']
    travel_classname: str = "economy"
    activity: str = "hiking tour"
    flexible_dates: bool = True
    departure_city: str = "New York"

class SearchTripPricesRequest(BaseModel):
    destination: str = "Madrid"
    start_date: str = "2025-09-15"
    end_date: str = "2025-09-22"
    passengers: Dict[str, Any] = {'adults': 1}
    trip_type: str = "solo adventure"
    include: List[Any] = ['flight', 'hotel']
    preferences: Dict[str, Any] = {'hotel_type': 'mid-range', 'family_friendly': True}
    destination_type: str = "beach"
    excursion_types: List[Any] = ['sightseeing', 'food tasting']
    package_type: str = "beach_vacation"
    hotel_category: str = "mid-range"
    origin: str = "New York"
    hotel_rating: int = 4
    interests: List[Any] = ['food']
    excursion_preferences: Dict[str, Any] = {'types': ['historical sightseeing', 'museum visits'], 'guided': True}
    excursion_type: str = "guided historical tours"
    budget: str = "moderate"
    accommodation_type: str = "resort"
    departure_city: str = "Boston"

class ChooseSeatRequest(BaseModel):
    booking_reference: str = "XYZ12345"
    seat_number: str = "12A"

class SendBoardingPassEmailRequest(BaseModel):
    booking_reference: str = "DL7890"
    passenger_name: str = "Michael Thompson"
    flight_date: str = "2025-07-15"
    airline: str = "Delta"
    flight_number: str = "DL2345"
    reservation_id: str = "RZ7890"
    destination: str = "New York"
    last_name: str = "Johnson"
    travel_date: str = "2024-07-15"

class SendEmailRequest(BaseModel):
    passenger_name: str = "John Smith"
    flight_number: str = "BA4567"
    flight_date: str = "2025-07-15"
    document: str = "boarding_pass"

class CheckFlightCheckinStatusRequest(BaseModel):
    booking_reference: str = "AB1234"
    flight_number: str = "UA123"
    last_name: str = "Smith"
    airline: str = "Delta Airlines"
    confirmation_number: str = "ZX7890"

class InitiateRefundRequest(BaseModel):
    booking_reference: str = "NYLA123"
    last_name: str = "Thompson"
    compensation_type: str = "direct"
    compensation_only: bool = True
    document_type: str = "expense_receipts"
    expense_types: List[Any] = ['hotel', 'taxi']
    expenses: Dict[str, Any] = {'flight': 450, 'hotel': 600}
    refund_method: str = "credit card"
    expense_type: str = "hotel"
    amount: int = 150
    trip_type: str = "business"
    trip_dates: Dict[str, Any] = {'start': '2024-03-10', 'end': '2024-03-15'}
    transaction_date: str = "2024-03-10"
    reason: str = "flight canceled"
    original_flight_date: str = "2024-07-15"
    cancelled_flight_date: str = "2024-07-15"
    contact_method: str = "email"
    flight_number: str = "AA1234"
    cancellation_date: str = "2024-04-20"
    travel_dates: List[Any] = ['2024-06-10', '2024-06-15']
    mode_of_travel: str = "flight"
    destination: str = "New York"
    issue: str = "overbooking"
    documents: List[Any] = ['receipt']

class GetRefundRequest(BaseModel):
    booking_reference: str = "XY1234"
    last_name: str = "Thompson"
    purchase_date: str = "2024-03-15"

class QueryBookingDetailsRequest(BaseModel):
    booking_reference: str = "FL12345"
    last_name: str = "Johnson"

class CheckRefundEligibilityRequest(BaseModel):
    booking_reference: str = "DEL459"
    last_name: str = "Thompson"
    flight_number: str = "AA123"
    delay_hours: int = 5

class UpdateRefundMethodRequest(BaseModel):
    booking_reference: str = "ABC123"
    last_name: str = "Smith"
    refund_method: str = "bank_transfer"

class QueryCompensationEligibilityRequest(BaseModel):
    booking_reference: str = "TX1234"
    last_name: str = "Johnson"

class IssueTravelCreditVoucherRequest(BaseModel):
    booking_reference: str = "TX1234"
    last_name: str = "Johnson"
    amount_percentage: int = 50

class IssueTravelVoucherRequest(BaseModel):
    booking_reference: str = "XYZ123"

class EscalateToHumanAgentRequest(BaseModel):
    reason: str = "User requested live chat with human agent"
    booking_reference: str = "ABC123"
    phone_number: str = "+1-555-123-4567"
    preferred_time: str = "after 4 PM today"
    name: str = "John Doe"
    preferred_channel: str = "chat"
    callback_number: str = "+1-555-123-4567"

class UpdateFlightDateRequest(BaseModel):
    booking_reference: str = "ABC123"
    new_return_date: str = "2024-07-20"

class GetBoardingPassPdfRequest(BaseModel):
    flight_number: str = "UA123"
    last_name: str = "Smith"
    booking_reference: str = "XY1234"
    email: str = "traveler@example.com"
    print_location: str = "home"
    passenger_name: str = "John Doe"
    airline: str = "Delta Airlines"
    email_hint: str = "123"

class VerifyBookingAndGetBoardingPassRequest(BaseModel):
    flight_number: str = "BA249"
    last_name: str = "Smith"
    first_initial: str = "J"

class PurchaseFlightInsuranceRequest(BaseModel):
    destination: str = "Los Angeles"
    start_date: str = "2025-08-15"
    end_date: str = "2025-08-20"
    plan: str = "full"
    origin: str = "Los Angeles"
    ticket_price: int = 850
    travelers: int = 1
    booking_reference: str = "AB1234"
    reservation_number: str = "R123456789"
    name_on_policy: str = "John Doe"
    airline: str = "Delta Airlines"
    confirmation_number: str = "ABC12345"
    last_name: str = "Johnson"
    departure: str = "New York"

class RetrieveFlightInsuranceRequest(BaseModel):
    booking_reference: str = "ABC123"

class PurchaseTripInsuranceRequest(BaseModel):
    destination: str = "Paris"
    start_date: str = "2025-09-10"
    end_date: str = "2025-09-20"
    plan: str = "standard"
    coverage: List[Any] = ['medical emergencies', 'trip cancellations']
    travelers: int = 1
    activities: List[Any] = ['hiking']
    medical_conditions: str = "none"
    pre_existing_conditions: bool = False
    trip_type: str = "family vacation"

class SearchFlightInsuranceRequest(BaseModel):
    destination: str = "Miami"
    start_date: str = "2025-07-15"
    end_date: str = "2025-07-20"
    origin: str = "New York"
    coverage: str = "medical assistance"
    departure: str = "New York"
    coverage_needs: List[Any] = ['trip cancellations', 'baggage loss']
    medical_conditions: str = "none"
    type: str = "multi-trip"
    trip_type: str = "family vacation"
    departure_city: str = "New York"
    airline: str = "British Airways"
    pre_existing_conditions: bool = False
    trip_cost: int = 500
    travelers: int = 2

class SearchTripRequest(BaseModel):
    origin: str = "New York"
    destination: str = "Madrid"
    departure_date: str = "2025-09-10"
    return_date: str = "2025-09-15"
    passengers: int = 1
    budget: int = 1500
    interests: List[Any] = ['history', 'art']
    destination_type: str = "beach"
    departure_window: List[Any] = ['2025-08-20', '2025-08-31']
    trip_length_days: int = 7
    excursion_types: List[Any] = ['historical', 'foodie']
    activity_type: List[Any] = ['history', 'culture']
    preferences: List[Any] = ['cultural', 'food']
    activities: List[Any] = ['history', 'art', 'museums', 'local cuisine']
    duration_days: int = 4
    return_window: List[Any] = ['2025-09-20', '2025-09-30']
    excursion_type: str = "history, art museums"
    trip_type: str = "cultural"
    budget_per_person: int = 1500
    package_type: str = "flight_hotel_activities"
    budget_max: int = 1500
    duration_nights: int = 5
    duration: str = "full_day"
    accommodation: str = "cozy Airbnb"
    hotel_location: str = "city center"
    include_hotel: bool = True
    max_budget: int = 1200
    experience_type: str = "cultural immersion"
    trip_duration: str = "day"
    interest: str = "historical landmarks"
    must_see: List[Any] = ['Prado Museum']
    cuisine_preference: str = "traditional Spanish"

class SearchTripInsuranceRequest(BaseModel):
    destination: str = "Spain"
    start_date: str = "2025-09-10"
    end_date: str = "2025-09-20"
    travelers: Dict[str, Any] = {'adults': 2, 'children': [8, 12]}
    trip_type: str = "sightseeing and leisure"
    coverage_types: List[Any] = ['medical emergencies', 'trip cancellation']
    activities: List[Any] = ['hiking']
    medical_conditions: str = "none"
    coverage: List[Any] = ['medical emergencies', 'hiking']
    budget: int = 50
    pre_existing_conditions: bool = False
    coverage_needs: List[Any] = ['medical emergencies', 'trip cancellations']
    coverage_type: str = "comprehensive"

# endregion

# Helper function to get sync database session
# def get_sync_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

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
    uvicorn.run(app, host="0.0.0.0", port=8000)

