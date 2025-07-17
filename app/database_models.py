from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, Time, Boolean, Text, ForeignKey, UniqueConstraint, Numeric
from decimal import Decimal as PyDecimal # Alias Python's Decimal if you still need it for other purposes, to avoid name collision with SQLAlchemy's DECIMAL/Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime, date, time
import os

Base = declarative_base()

class Airline(Base):
    __tablename__ = 'airlines'
    
    id = Column(Integer, primary_key=True)
    iata_code = Column(String(2), unique=True, nullable=False)
    icao_code = Column(String(3), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    country = Column(String(50), nullable=False)
    alliance = Column(String(20))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    aircraft = relationship("Aircraft", back_populates="airline")
    flights = relationship("Flight", back_populates="airline")

class AircraftType(Base):
    __tablename__ = 'aircraft_types'
    
    id = Column(Integer, primary_key=True)
    manufacturer = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    iata_code = Column(String(3))
    icao_code = Column(String(4))
    seats_economy = Column(Integer)
    seats_premium_economy = Column(Integer)
    seats_business = Column(Integer)
    seats_first = Column(Integer)
    total_seats = Column(Integer)
    range_km = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    aircraft = relationship("Aircraft", back_populates="aircraft_type")
    seat_maps = relationship("SeatMap", back_populates="aircraft_type")

class Airport(Base):
    __tablename__ = 'airports'
    
    id = Column(Integer, primary_key=True)
    iata_code = Column(String(3), unique=True, nullable=False)
    icao_code = Column(String(4), unique=True)
    name = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    timezone = Column(String(50))
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    origin_routes = relationship("Route", foreign_keys="Route.origin_airport_id", back_populates="origin_airport")
    destination_routes = relationship("Route", foreign_keys="Route.destination_airport_id", back_populates="destination_airport")

class Aircraft(Base):
    __tablename__ = 'aircraft'
    
    id = Column(Integer, primary_key=True)
    registration = Column(String(10), unique=True, nullable=False)
    aircraft_type_id = Column(Integer, ForeignKey('aircraft_types.id'))
    airline_id = Column(Integer, ForeignKey('airlines.id'))
    status = Column(String(20), default='active')
    delivery_date = Column(Date)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    aircraft_type = relationship("AircraftType", back_populates="aircraft")
    airline = relationship("Airline", back_populates="aircraft")
    flights = relationship("Flight", back_populates="aircraft")

class Route(Base):
    __tablename__ = 'routes'
    
    id = Column(Integer, primary_key=True)
    origin_airport_id = Column(Integer, ForeignKey('airports.id'))
    destination_airport_id = Column(Integer, ForeignKey('airports.id'))
    distance_km = Column(Integer)
    flight_duration_minutes = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (UniqueConstraint('origin_airport_id', 'destination_airport_id'),)
    
    # Relationships
    origin_airport = relationship("Airport", foreign_keys=[origin_airport_id], back_populates="origin_routes")
    destination_airport = relationship("Airport", foreign_keys=[destination_airport_id], back_populates="destination_routes")
    flights = relationship("Flight", back_populates="route")

class FlightSchedule(Base):
    __tablename__ = 'flight_schedules'
    
    id = Column(Integer, primary_key=True)
    flight_number = Column(String(10), nullable=False)
    airline_id = Column(Integer, ForeignKey('airlines.id'))
    route_id = Column(Integer, ForeignKey('routes.id'))
    aircraft_type_id = Column(Integer, ForeignKey('aircraft_types.id'))
    departure_time = Column(Time, nullable=False)
    arrival_time = Column(Time, nullable=False)
    days_of_week = Column(String(7))  # MTWTFSS format
    valid_from = Column(Date)
    valid_to = Column(Date)
    created_at = Column(DateTime, default=func.now())

class Flight(Base):
    __tablename__ = 'flights'
    
    id = Column(Integer, primary_key=True)
    flight_number = Column(String(10), nullable=False)
    airline_id = Column(Integer, ForeignKey('airlines.id'))
    aircraft_id = Column(Integer, ForeignKey('aircraft.id'))
    route_id = Column(Integer, ForeignKey('routes.id'))
    scheduled_departure = Column(DateTime, nullable=False)
    scheduled_arrival = Column(DateTime, nullable=False)
    actual_departure = Column(DateTime)
    actual_arrival = Column(DateTime)
    status = Column(String(20), default='scheduled')
    gate = Column(String(10))
    terminal = Column(String(10))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    airline = relationship("Airline", back_populates="flights")
    aircraft = relationship("Aircraft", back_populates="flights")
    route = relationship("Route", back_populates="flights")
    booking_segments = relationship("BookingSegment", back_populates="flight")
    flight_seats = relationship("FlightSeat", back_populates="flight")
    status_updates = relationship("FlightStatusUpdate", back_populates="flight")

class Passenger(Base):
    __tablename__ = 'passengers'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100))
    phone = Column(String(50))
    date_of_birth = Column(Date)
    nationality = Column(String(100))
    passport_number = Column(String(20))
    passport_expiry = Column(Date)
    frequent_flyer_number = Column(String(20))
    tier_status = Column(String(20), default='basic')
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    bookings = relationship("Booking", back_populates="passenger")
    booking_segments = relationship("BookingSegment", back_populates="passenger")
    trip_bookings = relationship("TripBooking", back_populates="passenger")
    insurance_policies = relationship("InsurancePolicy", back_populates="passenger")

class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True)
    booking_reference = Column(String(6), unique=True, nullable=False)
    passenger_id = Column(Integer, ForeignKey('passengers.id'))
    booking_date = Column(DateTime, default=func.now())
    total_amount = Column(Numeric(10, 2))
    currency = Column(String(3), default='USD')
    status = Column(String(20), default='confirmed')
    booking_source = Column(String(20), default='website')
    trip_type = Column(String(20))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    passenger = relationship("Passenger", back_populates="bookings")
    booking_segments = relationship("BookingSegment", back_populates="booking")
    insurance_policies = relationship("InsurancePolicy", back_populates="booking")
    refunds = relationship("Refund", back_populates="booking")

class BookingSegment(Base):
    __tablename__ = 'booking_segments'
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('bookings.id'))
    flight_id = Column(Integer, ForeignKey('flights.id'))
    passenger_id = Column(Integer, ForeignKey('passengers.id'))
    class_of_service = Column(String(20))
    fare_basis = Column(String(10))
    ticket_number = Column(String(15))
    seat_number = Column(String(5))
    baggage_allowance_kg = Column(Integer, default=23)
    meal_preference = Column(String(20))
    special_requests = Column(Text)
    check_in_status = Column(String(20), default='not_checked_in')
    boarding_pass_issued = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    booking = relationship("Booking", back_populates="booking_segments")
    flight = relationship("Flight", back_populates="booking_segments")
    passenger = relationship("Passenger", back_populates="booking_segments")
    baggage = relationship("Baggage", back_populates="booking_segment")

class SeatMap(Base):
    __tablename__ = 'seat_maps'
    
    id = Column(Integer, primary_key=True)
    aircraft_type_id = Column(Integer, ForeignKey('aircraft_types.id'))
    seat_number = Column(String(5), nullable=False)
    seat_type = Column(String(20))  # window, aisle, middle
    class_of_service = Column(String(20))
    is_exit_row = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    extra_legroom = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (UniqueConstraint('aircraft_type_id', 'seat_number'),)
    
    # Relationships
    aircraft_type = relationship("AircraftType", back_populates="seat_maps")

class FlightSeat(Base):
    __tablename__ = 'flight_seats'
    
    id = Column(Integer, primary_key=True)
    flight_id = Column(Integer, ForeignKey('flights.id'))
    seat_number = Column(String(5), nullable=False)
    passenger_id = Column(Integer, ForeignKey('passengers.id'))
    booking_segment_id = Column(Integer, ForeignKey('booking_segments.id'))
    seat_fee = Column(Numeric(8, 2), default=0)
    status = Column(String(20), default='available')
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (UniqueConstraint('flight_id', 'seat_number'),)
    
    # Relationships
    flight = relationship("Flight", back_populates="flight_seats")

class Baggage(Base):
    __tablename__ = 'baggage'
    
    id = Column(Integer, primary_key=True)
    booking_segment_id = Column(Integer, ForeignKey('booking_segments.id'))
    baggage_type = Column(String(20))  # carry_on, checked, excess
    weight_kg = Column(Numeric(5, 2))
    fee = Column(Numeric(8, 2), default=0)
    tag_number = Column(String(15))
    status = Column(String(20), default='checked_in')
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    booking_segment = relationship("BookingSegment", back_populates="baggage")

class InsurancePolicy(Base):
    __tablename__ = 'insurance_policies'
    
    id = Column(Integer, primary_key=True)
    policy_number = Column(String(20), unique=True, nullable=False)
    booking_id = Column(Integer, ForeignKey('bookings.id'))
    passenger_id = Column(Integer, ForeignKey('passengers.id'))
    policy_type = Column(String(30))  # flight, trip, comprehensive
    coverage_amount = Column(Numeric(10, 2))
    premium = Column(Numeric(8, 2))
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(20), default='active')
    provider = Column(String(50))
    terms_conditions = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    booking = relationship("Booking", back_populates="insurance_policies")
    passenger = relationship("Passenger", back_populates="insurance_policies")

class TripPackage(Base):
    __tablename__ = 'trip_packages'
    
    id = Column(Integer, primary_key=True)
    package_code = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    destination_city = Column(String(50))
    destination_country = Column(String(50))
    duration_days = Column(Integer)
    price_per_person = Column(Numeric(10, 2))
    includes_flight = Column(Boolean, default=True)
    includes_hotel = Column(Boolean, default=True)
    includes_activities = Column(Boolean, default=False)
    category = Column(String(30))  # leisure, business, adventure, cultural
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    trip_bookings = relationship("TripBooking", back_populates="trip_package")

class TripBooking(Base):
    __tablename__ = 'trip_bookings'
    
    id = Column(Integer, primary_key=True)
    booking_reference = Column(String(6), unique=True, nullable=False)
    passenger_id = Column(Integer, ForeignKey('passengers.id'))
    trip_package_id = Column(Integer, ForeignKey('trip_packages.id'))
    booking_date = Column(DateTime, default=func.now())
    travel_start_date = Column(Date)
    travel_end_date = Column(Date)
    num_passengers = Column(Integer, default=1)
    total_amount = Column(Numeric(10, 2))
    status = Column(String(20), default='confirmed')
    special_requests = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    passenger = relationship("Passenger", back_populates="trip_bookings")
    trip_package = relationship("TripPackage", back_populates="trip_bookings")
    excursion_bookings = relationship("ExcursionBooking", back_populates="trip_booking")
    refunds = relationship("Refund", back_populates="trip_booking")

class Excursion(Base):
    __tablename__ = 'excursions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    destination_city = Column(String(50))
    destination_country = Column(String(50))
    description = Column(Text)
    duration_hours = Column(Integer)
    price_per_person = Column(Numeric(8, 2))
    category = Column(String(30))  # cultural, adventure, nature, historical
    max_participants = Column(Integer)
    includes_transport = Column(Boolean, default=True)
    includes_guide = Column(Boolean, default=True)
    difficulty_level = Column(String(20))  # easy, moderate, challenging
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    excursion_bookings = relationship("ExcursionBooking", back_populates="excursion")

class ExcursionBooking(Base):
    __tablename__ = 'excursion_bookings'
    
    id = Column(Integer, primary_key=True)
    booking_reference = Column(String(10), unique=True, nullable=False)
    trip_booking_id = Column(Integer, ForeignKey('trip_bookings.id'))
    excursion_id = Column(Integer, ForeignKey('excursions.id'))
    booking_date = Column(DateTime, default=func.now())
    excursion_date = Column(Date)
    num_participants = Column(Integer)
    total_amount = Column(Numeric(8, 2))
    status = Column(String(20), default='confirmed')
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    trip_booking = relationship("TripBooking", back_populates="excursion_bookings")
    excursion = relationship("Excursion", back_populates="excursion_bookings")

class Refund(Base):
    __tablename__ = 'refunds'
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('bookings.id'))
    trip_booking_id = Column(Integer, ForeignKey('trip_bookings.id'))
    refund_reference = Column(String(10), unique=True, nullable=False)
    refund_type = Column(String(30))  # full, partial, compensation
    amount = Column(Numeric(10, 2))
    reason = Column(String(100))
    status = Column(String(20), default='pending')
    requested_date = Column(DateTime, default=func.now())
    processed_date = Column(DateTime)
    refund_method = Column(String(20))  # credit_card, bank_transfer, travel_credit
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    booking = relationship("Booking", back_populates="refunds")
    trip_booking = relationship("TripBooking", back_populates="refunds")

class AirlinePolicy(Base):
    __tablename__ = 'airline_policies'
    
    id = Column(Integer, primary_key=True)
    policy_type = Column(String(50), nullable=False)
    policy_category = Column(String(30))  # cancellation, change, baggage, refund
    route_type = Column(String(20))  # domestic, international
    class_of_service = Column(String(20))
    description = Column(Text)
    fee_amount = Column(Numeric(8, 2))
    fee_percentage = Column(Numeric(5, 2))
    conditions = Column(Text)
    effective_from = Column(Date)
    effective_to = Column(Date)
    created_at = Column(DateTime, default=func.now())

class FlightStatusUpdate(Base):
    __tablename__ = 'flight_status_updates'
    
    id = Column(Integer, primary_key=True)
    flight_id = Column(Integer, ForeignKey('flights.id'))
    status = Column(String(20))
    update_time = Column(DateTime, default=func.now())
    delay_minutes = Column(Integer)
    reason = Column(String(100))
    new_departure_time = Column(DateTime)
    new_arrival_time = Column(DateTime)
    gate_change = Column(String(10))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    flight = relationship("Flight", back_populates="status_updates")

class CustomerServiceLog(Base):
    __tablename__ = 'customer_service_logs'
    
    id = Column(Integer, primary_key=True)
    booking_reference = Column(String(10))
    passenger_id = Column(Integer, ForeignKey('passengers.id'))
    interaction_type = Column(String(30))  # call, chat, email, escalation
    agent_id = Column(String(20))
    summary = Column(Text)
    resolution = Column(String(100))
    status = Column(String(20))  # open, resolved, escalated
    created_at = Column(DateTime, default=func.now())


# # Database configuration
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://username:password@localhost/hopjetair")

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# def create_tables():
#     Base.metadata.create_all(bind=engine)