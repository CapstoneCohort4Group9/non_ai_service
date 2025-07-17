-- HopJetAir Database Schema
-- Full-service airline customer service system

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Airlines table
CREATE TABLE airlines (
    id SERIAL PRIMARY KEY,
    iata_code VARCHAR(2) UNIQUE NOT NULL,
    icao_code VARCHAR(3) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL,
    alliance VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aircraft types
CREATE TABLE aircraft_types (
    id SERIAL PRIMARY KEY,
    manufacturer VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    iata_code VARCHAR(3),
    icao_code VARCHAR(4),
    seats_economy INTEGER,
    seats_premium_economy INTEGER,
    seats_business INTEGER,
    seats_first INTEGER,
    total_seats INTEGER,
    range_km INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Airports
CREATE TABLE airports (
    id SERIAL PRIMARY KEY,
    iata_code VARCHAR(3) UNIQUE NOT NULL,
    icao_code VARCHAR(4) UNIQUE,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    timezone VARCHAR(50),
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aircraft fleet
CREATE TABLE aircraft (
    id SERIAL PRIMARY KEY,
    registration VARCHAR(10) UNIQUE NOT NULL,
    aircraft_type_id INTEGER REFERENCES aircraft_types(id),
    airline_id INTEGER REFERENCES airlines(id),
    status VARCHAR(20) DEFAULT 'active',
    delivery_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Flight routes
CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    origin_airport_id INTEGER REFERENCES airports(id),
    destination_airport_id INTEGER REFERENCES airports(id),
    distance_km INTEGER,
    flight_duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(origin_airport_id, destination_airport_id)
);

-- Flight schedules
CREATE TABLE flight_schedules (
    id SERIAL PRIMARY KEY,
    flight_number VARCHAR(10) NOT NULL,
    airline_id INTEGER REFERENCES airlines(id),
    route_id INTEGER REFERENCES routes(id),
    aircraft_type_id INTEGER REFERENCES aircraft_types(id),
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    days_of_week VARCHAR(7), -- MTWTFSS format
    valid_from DATE,
    valid_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Actual flights
CREATE TABLE flights (
    id SERIAL PRIMARY KEY,
    flight_number VARCHAR(10) NOT NULL,
    airline_id INTEGER REFERENCES airlines(id),
    aircraft_id INTEGER REFERENCES aircraft(id),
    route_id INTEGER REFERENCES routes(id),
    scheduled_departure TIMESTAMP NOT NULL,
    scheduled_arrival TIMESTAMP NOT NULL,
    actual_departure TIMESTAMP,
    actual_arrival TIMESTAMP,
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, boarding, departed, arrived, delayed, cancelled
    gate VARCHAR(10),
    terminal VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Passengers
CREATE TABLE passengers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(50),
    date_of_birth DATE,
    nationality VARCHAR(100),
    passport_number VARCHAR(20),
    passport_expiry DATE,
    frequent_flyer_number VARCHAR(20),
    tier_status VARCHAR(20) DEFAULT 'basic', -- basic, silver, gold, platinum
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bookings
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    booking_reference VARCHAR(6) UNIQUE NOT NULL,
    passenger_id INTEGER REFERENCES passengers(id),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'confirmed', -- confirmed, cancelled, refunded
    booking_source VARCHAR(20) DEFAULT 'website',
    trip_type VARCHAR(20), -- one-way, round-trip, multi-city
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Booking segments (individual flights in a booking)
CREATE TABLE booking_segments (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER REFERENCES bookings(id),
    flight_id INTEGER REFERENCES flights(id),
    passenger_id INTEGER REFERENCES passengers(id),
    class_of_service VARCHAR(20), -- economy, premium_economy, business, first
    fare_basis VARCHAR(10),
    ticket_number VARCHAR(15),
    seat_number VARCHAR(5),
    baggage_allowance_kg INTEGER DEFAULT 23,
    meal_preference VARCHAR(20),
    special_requests TEXT,
    check_in_status VARCHAR(20) DEFAULT 'not_checked_in',
    boarding_pass_issued BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seat maps
CREATE TABLE seat_maps (
    id SERIAL PRIMARY KEY,
    aircraft_type_id INTEGER REFERENCES aircraft_types(id),
    seat_number VARCHAR(5) NOT NULL,
    seat_type VARCHAR(20), -- window, aisle, middle
    class_of_service VARCHAR(20),
    is_exit_row BOOLEAN DEFAULT FALSE,
    is_blocked BOOLEAN DEFAULT FALSE,
    extra_legroom BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(aircraft_type_id, seat_number)
);

-- Flight seats (specific to each flight)
CREATE TABLE flight_seats (
    id SERIAL PRIMARY KEY,
    flight_id INTEGER REFERENCES flights(id),
    seat_number VARCHAR(5) NOT NULL,
    passenger_id INTEGER REFERENCES passengers(id),
    booking_segment_id INTEGER REFERENCES booking_segments(id),
    seat_fee DECIMAL(8, 2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'available', -- available, occupied, blocked
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(flight_id, seat_number)
);

-- Baggage
CREATE TABLE baggage (
    id SERIAL PRIMARY KEY,
    booking_segment_id INTEGER REFERENCES booking_segments(id),
    baggage_type VARCHAR(20), -- carry_on, checked, excess
    weight_kg DECIMAL(5, 2),
    fee DECIMAL(8, 2) DEFAULT 0,
    tag_number VARCHAR(15),
    status VARCHAR(20) DEFAULT 'checked_in',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insurance policies
CREATE TABLE insurance_policies (
    id SERIAL PRIMARY KEY,
    policy_number VARCHAR(20) UNIQUE NOT NULL,
    booking_id INTEGER REFERENCES bookings(id),
    passenger_id INTEGER REFERENCES passengers(id),
    policy_type VARCHAR(30), -- flight, trip, comprehensive
    coverage_amount DECIMAL(10, 2),
    premium DECIMAL(8, 2),
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    provider VARCHAR(50),
    terms_conditions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trip packages
CREATE TABLE trip_packages (
    id SERIAL PRIMARY KEY,
    package_code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    destination_city VARCHAR(50),
    destination_country VARCHAR(50),
    duration_days INTEGER,
    price_per_person DECIMAL(10, 2),
    includes_flight BOOLEAN DEFAULT TRUE,
    includes_hotel BOOLEAN DEFAULT TRUE,
    includes_activities BOOLEAN DEFAULT FALSE,
    category VARCHAR(30), -- leisure, business, adventure, cultural
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trip bookings
CREATE TABLE trip_bookings (
    id SERIAL PRIMARY KEY,
    booking_reference VARCHAR(6) UNIQUE NOT NULL,
    passenger_id INTEGER REFERENCES passengers(id),
    trip_package_id INTEGER REFERENCES trip_packages(id),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    travel_start_date DATE,
    travel_end_date DATE,
    num_passengers INTEGER DEFAULT 1,
    total_amount DECIMAL(10, 2),
    status VARCHAR(20) DEFAULT 'confirmed',
    special_requests TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Excursions and activities
CREATE TABLE excursions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    destination_city VARCHAR(50),
    destination_country VARCHAR(50),
    description TEXT,
    duration_hours INTEGER,
    price_per_person DECIMAL(8, 2),
    category VARCHAR(30), -- cultural, adventure, nature, historical
    max_participants INTEGER,
    includes_transport BOOLEAN DEFAULT TRUE,
    includes_guide BOOLEAN DEFAULT TRUE,
    difficulty_level VARCHAR(20), -- easy, moderate, challenging
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Excursion bookings
CREATE TABLE excursion_bookings (
    id SERIAL PRIMARY KEY,
    booking_reference VARCHAR(10) UNIQUE NOT NULL,
    trip_booking_id INTEGER REFERENCES trip_bookings(id),
    excursion_id INTEGER REFERENCES excursions(id),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    excursion_date DATE,
    num_participants INTEGER,
    total_amount DECIMAL(8, 2),
    status VARCHAR(20) DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Refunds and compensation
CREATE TABLE refunds (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER REFERENCES bookings(id),
    trip_booking_id INTEGER REFERENCES trip_bookings(id),
    refund_reference VARCHAR(10) UNIQUE NOT NULL,
    refund_type VARCHAR(30), -- full, partial, compensation
    amount DECIMAL(10, 2),
    reason VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, processed, rejected
    requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_date TIMESTAMP,
    refund_method VARCHAR(20), -- credit_card, bank_transfer, travel_credit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Policies and fees
CREATE TABLE airline_policies (
    id SERIAL PRIMARY KEY,
    policy_type VARCHAR(50) NOT NULL,
    policy_category VARCHAR(30), -- cancellation, change, baggage, refund
    route_type VARCHAR(20), -- domestic, international
    class_of_service VARCHAR(20),
    description TEXT,
    fee_amount DECIMAL(8, 2),
    fee_percentage DECIMAL(5, 2),
    conditions TEXT,
    effective_from DATE,
    effective_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Flight status updates
CREATE TABLE flight_status_updates (
    id SERIAL PRIMARY KEY,
    flight_id INTEGER REFERENCES flights(id),
    status VARCHAR(20),
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delay_minutes INTEGER,
    reason VARCHAR(100),
    new_departure_time TIMESTAMP,
    new_arrival_time TIMESTAMP,
    gate_change VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer service interactions
CREATE TABLE customer_service_logs (
    id SERIAL PRIMARY KEY,
    booking_reference VARCHAR(10),
    passenger_id INTEGER REFERENCES passengers(id),
    interaction_type VARCHAR(30), -- call, chat, email, escalation
    agent_id VARCHAR(20),
    summary TEXT,
    resolution VARCHAR(100),
    status VARCHAR(20), -- open, resolved, escalated
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_bookings_reference ON bookings(booking_reference);
CREATE INDEX idx_bookings_passenger ON bookings(passenger_id);
CREATE INDEX idx_flights_number_date ON flights(flight_number, scheduled_departure);
CREATE INDEX idx_flights_route ON flights(route_id);
CREATE INDEX idx_passengers_email ON passengers(email);
CREATE INDEX idx_trip_bookings_reference ON trip_bookings(booking_reference);
CREATE INDEX idx_excursion_bookings_reference ON excursion_bookings(booking_reference);
CREATE INDEX idx_booking_segments_booking ON booking_segments(booking_id);
CREATE INDEX idx_flight_seats_flight ON flight_seats(flight_id);
CREATE INDEX idx_insurance_policies_booking ON insurance_policies(booking_id);


-- GRANT ALL PRIVILEGES ON DATABASE hopjetairline_db TO hopjetairline_db;
-- GRANT ALL ON SCHEMA public TO hopjetairline_db;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hopjetairline_db;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hopjetairline_db;