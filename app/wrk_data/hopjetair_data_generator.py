import psycopg2
import random
from datetime import datetime, timedelta, date, time
from faker import Faker
import string

# Database connection
DB_URL = "postgresql://hopjetair:SecurePass123!@hopjetair-postgres.cepc0wqo22hd.us-east-1.rds.amazonaws.com:5432/hopjetairline_db"
#DB_URL = "postgresql://hopjetair:SecurePass123!@localhost:5432/hopjetairline_db"

# Initialize Faker
fake = Faker(['en_US', 'en_GB', 'en_CA', 'en_AU'])

def connect_db():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(DB_URL)

def generate_booking_reference():
    """Generate a 6-character booking reference"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_flight_number(airline_code):
    """Generate realistic flight number"""
    return f"{airline_code}{random.randint(100, 9999)}"

def generate_seat_number(class_service):
    """Generate realistic seat numbers based on class"""
    if class_service == 'first':
        row = random.randint(1, 3)
        seat = random.choice(['A', 'B', 'E', 'F'])
    elif class_service == 'business':
        row = random.randint(4, 12)
        seat = random.choice(['A', 'B', 'E', 'F'])
    elif class_service == 'premium_economy':
        row = random.randint(13, 20)
        seat = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
    else:  # economy
        row = random.randint(21, 45)
        seat = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
    
    return f"{row}{seat}"

def main():
    conn = connect_db()
    cur = conn.cursor()
    
    print("Starting data generation for HopJetAir database...")
    
    try:
        # 1. Airlines
        print("Generating airlines...")
        airlines_data = [
            ('JH', 'JHA', 'HopJetAir', 'United States', 'Star Alliance'),
            ('AA', 'AAL', 'American Airlines', 'United States', 'Oneworld'),
            ('DL', 'DAL', 'Delta Air Lines', 'United States', 'SkyTeam'),
            ('UA', 'UAL', 'United Airlines', 'United States', 'Star Alliance'),
            ('BA', 'BAW', 'British Airways', 'United Kingdom', 'Oneworld'),
            ('LH', 'DLH', 'Lufthansa', 'Germany', 'Star Alliance'),
            ('AF', 'AFR', 'Air France', 'France', 'SkyTeam'),
            ('KL', 'KLM', 'KLM Royal Dutch Airlines', 'Netherlands', 'SkyTeam'),
            ('AC', 'ACA', 'Air Canada', 'Canada', 'Star Alliance'),
            ('QF', 'QFA', 'Qantas', 'Australia', 'Oneworld')
        ]
        
        for airline in airlines_data:
            cur.execute("""
                INSERT INTO airlines (iata_code, icao_code, name, country, alliance)
                VALUES (%s, %s, %s, %s, %s)
            """, airline)
        
        # 2. Aircraft Types
        print("Generating aircraft types...")
        aircraft_types_data = [
            ('Boeing', '737-800', '738', 'B738', 162, 0, 0, 0, 162, 5400),
            ('Boeing', '737-900', '739', 'B739', 180, 0, 0, 0, 180, 5400),
            ('Boeing', '777-300ER', '77W', 'B77W', 296, 24, 40, 8, 368, 13649),
            ('Boeing', '787-9', '789', 'B789', 254, 28, 30, 0, 312, 14800),
            ('Airbus', 'A320', '320', 'A320', 150, 0, 0, 0, 150, 6100),
            ('Airbus', 'A321', '321', 'A321', 185, 0, 0, 0, 185, 7400),
            ('Airbus', 'A330-300', '333', 'A333', 247, 21, 36, 0, 304, 11750),
            ('Airbus', 'A350-900', '359', 'A359', 253, 24, 42, 0, 319, 15000),
            ('Embraer', 'E-175', 'E75', 'E170', 76, 0, 0, 0, 76, 3889),
            ('Bombardier', 'CRJ-900', 'CR9', 'CRJ9', 90, 0, 0, 0, 90, 2956)
        ]
        
        for aircraft_type in aircraft_types_data:
            cur.execute("""
                INSERT INTO aircraft_types (manufacturer, model, iata_code, icao_code, 
                                          seats_economy, seats_premium_economy, seats_business, 
                                          seats_first, total_seats, range_km)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, aircraft_type)
        
        # 3. Airports
        print("Generating airports...")
        airports_data = [
            ('JFK', 'KJFK', 'John F. Kennedy International Airport', 'New York', 'United States', 'America/New_York', 40.6413, -73.7781),
            ('LAX', 'KLAX', 'Los Angeles International Airport', 'Los Angeles', 'United States', 'America/Los_Angeles', 33.9425, -118.4081),
            ('ORD', 'KORD', 'Chicago O\'Hare International Airport', 'Chicago', 'United States', 'America/Chicago', 41.9742, -87.9073),
            ('MIA', 'KMIA', 'Miami International Airport', 'Miami', 'United States', 'America/New_York', 25.7959, -80.2870),
            ('DFW', 'KDFW', 'Dallas/Fort Worth International Airport', 'Dallas', 'United States', 'America/Chicago', 32.8998, -97.0403),
            ('LHR', 'EGLL', 'London Heathrow Airport', 'London', 'United Kingdom', 'Europe/London', 51.4700, -0.4543),
            ('CDG', 'LFPG', 'Charles de Gaulle Airport', 'Paris', 'France', 'Europe/Paris', 49.0097, 2.5479),
            ('FRA', 'EDDF', 'Frankfurt Airport', 'Frankfurt', 'Germany', 'Europe/Berlin', 50.0379, 8.5622),
            ('AMS', 'EHAM', 'Amsterdam Airport Schiphol', 'Amsterdam', 'Netherlands', 'Europe/Amsterdam', 52.3105, 4.7683),
            ('YYZ', 'CYYZ', 'Toronto Pearson International Airport', 'Toronto', 'Canada', 'America/Toronto', 43.6777, -79.6248),
            ('SYD', 'YSSY', 'Sydney Kingsford Smith Airport', 'Sydney', 'Australia', 'Australia/Sydney', -33.9399, 151.1753),
            ('NRT', 'RJAA', 'Narita International Airport', 'Tokyo', 'Japan', 'Asia/Tokyo', 35.7653, 140.3861),
            ('HKG', 'VHHH', 'Hong Kong International Airport', 'Hong Kong', 'Hong Kong', 'Asia/Hong_Kong', 22.3080, 113.9185),
            ('DUB', 'EIDW', 'Dublin Airport', 'Dublin', 'Ireland', 'Europe/Dublin', 53.4213, -6.2701),
            ('ZUR', 'LSZH', 'Zurich Airport', 'Zurich', 'Switzerland', 'Europe/Zurich', 47.4647, 8.5492)
        ]
        
        for airport in airports_data:
            cur.execute("""
                INSERT INTO airports (iata_code, icao_code, name, city, country, timezone, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, airport)
        
        # Get inserted IDs for foreign key references
        cur.execute("SELECT id, iata_code FROM airlines")
        airlines = {row[1]: row[0] for row in cur.fetchall()}
        
        cur.execute("SELECT id FROM aircraft_types")
        aircraft_type_ids = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT id, iata_code FROM airports")
        airports = {row[1]: row[0] for row in cur.fetchall()}
        
        # 4. Aircraft Fleet
        print("Generating aircraft fleet...")
        aircraft_registrations = []
        cur.execute("SELECT registration FROM aircraft")
        existing_regs = set(row[0] for row in cur.fetchall())
        while len(aircraft_registrations) < 50:
            reg = f"N{random.randint(100, 999)}{random.choice(['JH', 'AA', 'DL', 'UA'])}"
            if reg not in existing_regs and reg not in aircraft_registrations:
                aircraft_registrations.append(reg)
                cur.execute("""
                    INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    reg,
                    random.choice(aircraft_type_ids),
                    random.choice(list(airlines.values())),
                    random.choice(['active', 'maintenance', 'retired']),
                    fake.date_between(start_date='-10y', end_date='today')
                ))
        
        # 5. Routes
        print("Generating routes...")
        route_pairs = []
        airport_codes = list(airports.keys())
        for i in range(30):
            origin = random.choice(airport_codes)
            destination = random.choice([code for code in airport_codes if code != origin])
            if (origin, destination) not in route_pairs and (destination, origin) not in route_pairs:
                route_pairs.append((origin, destination))
                distance = random.randint(500, 15000)
                duration = int(distance / 8)  # Rough estimate
                
                cur.execute("""
                    INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes)
                    VALUES (%s, %s, %s, %s)
                """, (airports[origin], airports[destination], distance, duration))
        
        cur.execute("SELECT id FROM routes")
        route_ids = [row[0] for row in cur.fetchall()]
        
        # 6. Flight Schedules
        print("Generating flight schedules...")
        for i in range(50):
            airline_id = random.choice(list(airlines.values()))
            airline_code = [code for code, id in airlines.items() if id == airline_id][0]
            
            cur.execute("""
                INSERT INTO flight_schedules (flight_number, airline_id, route_id, aircraft_type_id,
                                            departure_time, arrival_time, days_of_week, valid_from, valid_to)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                generate_flight_number(airline_code),
                airline_id,
                random.choice(route_ids),
                random.choice(aircraft_type_ids),
                fake.time(),
                fake.time(),
                ''.join(random.choices(['M', 'T', 'W', 'T', 'F', 'S', 'S'], k=7)),
                fake.date_between(start_date='-1y', end_date='today'),
                fake.date_between(start_date='today', end_date='+1y')
            ))
        
        # 7. Get aircraft IDs
        cur.execute("SELECT id FROM aircraft")
        aircraft_ids = [row[0] for row in cur.fetchall()]
        
        # 8. Flights
        print("Generating flights...")
        flight_ids = []
        for i in range(200):
            scheduled_departure = fake.date_time_between(start_date='-30d', end_date='+60d')
            scheduled_arrival = scheduled_departure + timedelta(hours=random.randint(1, 16))
            
            # Some flights have actual times, some don't (future flights)
            if scheduled_departure < datetime.now():
                actual_departure = scheduled_departure + timedelta(minutes=random.randint(-30, 120))
                actual_arrival = actual_departure + timedelta(hours=random.randint(1, 16))
                status = random.choice(['arrived', 'delayed', 'cancelled'])
            else:
                actual_departure = None
                actual_arrival = None
                status = random.choice(['scheduled', 'boarding'])
            
            airline_id = random.choice(list(airlines.values()))
            airline_code = [code for code, id in airlines.items() if id == airline_id][0]
            
            cur.execute("""
                INSERT INTO flights (flight_number, airline_id, aircraft_id, route_id,
                                   scheduled_departure, scheduled_arrival, actual_departure, actual_arrival,
                                   status, gate, terminal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                generate_flight_number(airline_code),
                airline_id,
                random.choice(aircraft_ids),
                random.choice(route_ids),
                scheduled_departure,
                scheduled_arrival,
                actual_departure,
                actual_arrival,
                status,
                f"A{random.randint(1, 30)}",
                random.choice(['A', 'B', 'C'])
            ))
            flight_ids.append(cur.fetchone()[0])
        
        # 9. Passengers
        print("Generating passengers...")
        passenger_ids = []
        for i in range(100):
            cur.execute("""
                INSERT INTO passengers (first_name, last_name, email, phone, date_of_birth,
                                      nationality, passport_number, passport_expiry,
                                      frequent_flyer_number, tier_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                fake.first_name(),
                fake.last_name(),
                fake.email(),
                fake.phone_number(),
                fake.date_of_birth(minimum_age=18, maximum_age=80),
                fake.country(),
                fake.passport_number(),
                fake.date_between(start_date='today', end_date='+10y'),
                f"JH{random.randint(100000, 999999)}",
                random.choice(['basic', 'silver', 'gold', 'platinum'])
            ))
            passenger_ids.append(cur.fetchone()[0])
        
        # 10. Bookings
        print("Generating bookings...")
        booking_ids = []
        for i in range(150):
            cur.execute("""
                INSERT INTO bookings (booking_reference, passenger_id, booking_date, total_amount,
                                    currency, status, booking_source, trip_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                generate_booking_reference(),
                random.choice(passenger_ids),
                fake.date_time_between(start_date='-60d', end_date=datetime.today()),
                round(random.uniform(200, 2000), 2),
                random.choice(['USD', 'EUR', 'GBP', 'CAD']),
                random.choice(['confirmed', 'cancelled', 'refunded']),
                random.choice(['website', 'mobile', 'phone', 'agent']),
                random.choice(['one-way', 'round-trip', 'multi-city'])
            ))
            booking_ids.append(cur.fetchone()[0])
        
        # 11. Booking Segments
        print("Generating booking segments...")
        booking_segment_ids = []
        for booking_id in booking_ids:
            # Each booking has 1-3 segments
            num_segments = random.randint(1, 3)
            for j in range(num_segments):
                class_service = random.choice(['economy', 'premium_economy', 'business', 'first'])
                
                cur.execute("""
                    INSERT INTO booking_segments (booking_id, flight_id, passenger_id, class_of_service,
                                                fare_basis, ticket_number, seat_number, baggage_allowance_kg,
                                                meal_preference, check_in_status, boarding_pass_issued)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    booking_id,
                    random.choice(flight_ids),
                    random.choice(passenger_ids),
                    class_service,
                    f"{random.choice(['Y', 'M', 'H', 'Q', 'V', 'W', 'S', 'T', 'L', 'A'])}{random.randint(1, 9)}",
                    f"JH{random.randint(100000000000, 999999999999)}",
                    generate_seat_number(class_service),
                    random.choice([23, 32, 40]) if class_service == 'economy' else random.choice([32, 40]),
                    random.choice(['vegetarian', 'kosher', 'halal', 'diabetic', 'standard']),
                    random.choice(['not_checked_in', 'checked_in', 'boarding_pass_issued']),
                    random.choice([True, False])
                ))
                booking_segment_ids.append(cur.fetchone()[0])
        
        # 12. Seat Maps (for each aircraft type)
        print("Generating seat maps...")
        cur.execute("SELECT id, seats_economy, seats_premium_economy, seats_business, seats_first FROM aircraft_types")
        for aircraft_type_id, seats_economy, seats_premium_economy, seats_business, seats_first in cur.fetchall():
            # Generate seats for each class
            classes = [
                ('first', seats_first or 0, 1),
                ('business', seats_business or 0, 4 if seats_first else 1),
                ('premium_economy', seats_premium_economy or 0, 13 if seats_business else 1),
                ('economy', seats_economy or 0, 21)
            ]
            
            for class_name, seat_count, start_row in classes:
                if seat_count > 0:
                    rows_needed = (seat_count + 5) // 6  # 6 seats per row typically
                    for row in range(start_row, start_row + rows_needed):
                        for seat_letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                            if (row - start_row) * 6 + ord(seat_letter) - ord('A') < seat_count:
                                cur.execute("""
                                    INSERT INTO seat_maps (aircraft_type_id, seat_number, seat_type, class_of_service,
                                                         is_exit_row, extra_legroom)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                """, (
                                    aircraft_type_id,
                                    f"{row}{seat_letter}",
                                    'window' if seat_letter in ['A', 'F'] else 'aisle' if seat_letter in ['C', 'D'] else 'middle',
                                    class_name,
                                    random.choice([True, False]) if row % 10 == 0 else False,
                                    random.choice([True, False]) if row % 15 == 0 else False
                                ))
        
        # 13. Flight Seats
        print("Generating flight seats...")
        for flight_id in flight_ids[:50]:  # Only for first 50 flights to avoid too much data
            cur.execute("""
                SELECT sm.seat_number, sm.class_of_service 
                FROM seat_maps sm 
                JOIN flights f ON f.aircraft_id IN (SELECT id FROM aircraft WHERE aircraft_type_id = sm.aircraft_type_id)
                WHERE f.id = %s
                LIMIT 50
            """, (flight_id,))
            
            seats = cur.fetchall()
            for seat_number, class_service in seats:
                # Some seats are occupied, some available
                if random.random() < 0.6:  # 60% occupancy
                    passenger_id = random.choice(passenger_ids)
                    booking_segment_id = random.choice(booking_segment_ids)
                    status = 'occupied'
                    seat_fee = random.uniform(0, 50) if class_service == 'economy' else 0
                else:
                    passenger_id = None
                    booking_segment_id = None
                    status = 'available'
                    seat_fee = 0
                
                cur.execute("""
                    INSERT INTO flight_seats (flight_id, seat_number, passenger_id, booking_segment_id, seat_fee, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (flight_id, seat_number, passenger_id, booking_segment_id, seat_fee, status))
        
        # 14. Baggage
        print("Generating baggage...")
        for segment_id in booking_segment_ids:
            # Each segment can have multiple baggage items
            num_bags = random.randint(1, 3)
            for i in range(num_bags):
                baggage_type = random.choice(['carry_on', 'checked', 'excess'])
                weight = random.uniform(5, 25) if baggage_type == 'carry_on' else random.uniform(15, 50)
                fee = 0 if baggage_type == 'carry_on' else random.uniform(25, 100)
                
                cur.execute("""
                    INSERT INTO baggage (booking_segment_id, baggage_type, weight_kg, fee, tag_number, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    segment_id,
                    baggage_type,
                    round(weight, 1),
                    round(fee, 2),
                    f"JH{random.randint(100000, 999999)}" if baggage_type != 'carry_on' else None,
                    random.choice(['checked_in', 'loaded', 'delivered'])
                ))
        
        # 15. Insurance Policies
        print("Generating insurance policies...")
        for i in range(75):
            booking_id = random.choice(booking_ids)
            cur.execute("""
                INSERT INTO insurance_policies (policy_number, booking_id, passenger_id, policy_type,
                                              coverage_amount, premium, start_date, end_date, status, provider)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                f"INS{random.randint(1000000, 9999999)}",
                booking_id,
                random.choice(passenger_ids),
                random.choice(['flight', 'trip', 'comprehensive']),
                random.uniform(1000, 10000),
                random.uniform(50, 200),
                fake.date_between(start_date='-30d', end_date='today'),
                fake.date_between(start_date='today', end_date='+90d'),
                random.choice(['active', 'expired', 'cancelled']),
                random.choice(['TravelSure', 'GlobalProtect', 'SafeJourney', 'TripGuard'])
            ))
        
        # 16. Trip Packages
        print("Generating trip packages...")

        destinations = [
            ('Paris', 'France'), ('London', 'United Kingdom'), ('Rome', 'Italy'),
            ('Tokyo', 'Japan'), ('Sydney', 'Australia'), ('Dubai', 'UAE'),
            ('New York', 'United States'), ('Amsterdam', 'Netherlands'),
            ('Barcelona', 'Spain'), ('Bangkok', 'Thailand')
        ]

        # 🛡️ Step 1: Fetch existing package codes from the database
        cur.execute("SELECT package_code FROM trip_packages")
        existing_codes = set(row[0] for row in cur.fetchall())

        # 🔄 Step 2: Generate unique codes and insert trip packages
        trip_package_ids = set()
        generated_codes = set()

        while len(trip_package_ids) < 20:
            code = f"PKG{random.randint(100, 999)}"

            # Ensure uniqueness across both DB and current run
            if code in existing_codes or code in generated_codes:
                continue

            generated_codes.add(code)
            destination = random.choice(destinations)

            cur.execute("""
                INSERT INTO trip_packages (
                    package_code, name, description, destination_city, destination_country,
                    duration_days, price_per_person, includes_flight, includes_hotel,
                    includes_activities, category
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                code,
                f"Amazing {destination[0]} Experience",
                f"Discover the wonders of {destination[0]} with our comprehensive travel package.",
                destination[0],
                destination[1],
                random.randint(3, 14),
                round(random.uniform(800, 3000), 2),
                True,
                True,
                random.choice([True, False]),
                random.choice(['leisure', 'business', 'adventure', 'cultural'])
            ))

            trip_package_ids.add(cur.fetchone()[0])

        
        # 17. Trip Bookings
        print("Generating trip bookings...")
        trip_booking_ids = []
        for i in range(40):
            start_date = fake.date_between(start_date='today', end_date='+180d')
            cur.execute("""
                INSERT INTO trip_bookings (booking_reference, passenger_id, trip_package_id, travel_start_date,
                                         travel_end_date, num_passengers, total_amount, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                generate_booking_reference(),
                random.choice(passenger_ids),
                random.choice(list(trip_package_ids)),
                start_date,
                start_date + timedelta(days=random.randint(3, 14)),
                random.randint(1, 4),
                random.uniform(1000, 5000),
                random.choice(['confirmed', 'cancelled', 'completed'])
            ))
            trip_booking_ids.append(cur.fetchone()[0])
        
        # 18. Excursions
        print("Generating excursions...")
        excursion_ids = []
        for destination in destinations:
            for i in range(3):
                cur.execute("""
                    INSERT INTO excursions (name, destination_city, destination_country, description,
                                          duration_hours, price_per_person, category, max_participants,
                                          includes_transport, includes_guide, difficulty_level)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    f"{random.choice(['Historical', 'Cultural', 'Adventure', 'Nature'])} Tour of {destination[0]}",
                    destination[0],
                    destination[1],
                    f"Explore the best of {destination[0]} with our guided tour.",
                    random.randint(2, 8),
                    random.uniform(50, 200),
                    random.choice(['cultural', 'adventure', 'nature', 'historical']),
                    random.randint(10, 30),
                    random.choice([True, False]),
                    True,
                    random.choice(['easy', 'moderate', 'challenging'])
                ))
                excursion_ids.append(cur.fetchone()[0])
        
        # 19. Excursion Bookings
        print("Generating excursion bookings...")
        for i in range(60):
            cur.execute("""
                INSERT INTO excursion_bookings (booking_reference, trip_booking_id, excursion_id,
                                              excursion_date, num_participants, total_amount, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                generate_booking_reference(),
                random.choice(trip_booking_ids),
                random.choice(excursion_ids),
                fake.date_between(start_date='today', end_date='+180d'),
                random.randint(1, 4),
                random.uniform(100, 400),
                random.choice(['confirmed', 'cancelled', 'completed'])
            ))
        
        # 20. Refunds
        print("Generating refunds...")
        for i in range(25):
            cur.execute("""
                INSERT INTO refunds (booking_id, refund_reference, refund_type, amount, reason,
                                   status, refund_method)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                random.choice(booking_ids),
                f"REF{random.randint(1000, 9999)}",
                random.choice(['full', 'partial', 'compensation']),
                random.uniform(100, 1000),
                random.choice(['Flight cancelled', 'Customer request', 'Schedule change', 'Weather delay']),
                random.choice(['pending', 'approved', 'processed', 'rejected']),
                random.choice(['credit_card', 'bank_transfer', 'travel_credit'])
            ))
        
        # 21. Airline Policies
        print("Generating airline policies...")
        policy_types = [
            ('Cancellation Policy', 'cancellation', 'international', 'economy', 'Free cancellation up to 24 hours', 0, 0),
            ('Change Fee', 'change', 'domestic', 'economy', 'Change fee for domestic flights', 75, 0),
            ('Baggage Policy', 'baggage', 'international', 'business', 'Business class baggage allowance', 0, 0),
            ('Refund Policy', 'refund', 'international', 'first', 'Full refund policy for first class', 0, 0),
            ('Excess Baggage', 'baggage', 'domestic', 'economy', 'Excess baggage fees', 25, 0)
        ]
        
        for policy in policy_types:
            cur.execute("""
                INSERT INTO airline_policies (policy_type, policy_category, route_type, class_of_service,
                                            description, fee_amount, fee_percentage, effective_from, effective_to)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                policy[0], policy[1], policy[2], policy[3], policy[4], policy[5], policy[6],
                fake.date_between(start_date='-1y', end_date='today'),
                fake.date_between(start_date='today', end_date='+1y')
            ))
        
        # 22. Flight Status Updates
        print("Generating flight status updates...")
        for i in range(100):
            flight_id = random.choice(flight_ids)
            delay_minutes = random.randint(0, 240) if random.random() < 0.3 else 0
            
            cur.execute("""
                INSERT INTO flight_status_updates (flight_id, status, delay_minutes, reason,
                                                 new_departure_time, new_arrival_time, gate_change)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                flight_id,
                random.choice(['on_time', 'delayed', 'cancelled', 'boarding', 'departed']),
                delay_minutes if delay_minutes > 0 else None,
                random.choice(['Weather', 'Technical', 'Air Traffic Control', 'Crew', 'Airport Operations']) if delay_minutes > 0 else None,
                fake.date_time_between(start_date='-30d', end_date='+60d') if delay_minutes > 0 else None,
                fake.date_time_between(start_date='-30d', end_date='+60d') if delay_minutes > 0 else None,
                f"B{random.randint(1, 25)}" if random.random() < 0.2 else None
            ))
        
        # 23. Customer Service Logs
        print("Generating customer service logs...")
        for i in range(80):
            cur.execute("""
                INSERT INTO customer_service_logs (booking_reference, passenger_id, interaction_type,
                                                 agent_id, summary, resolution, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                generate_booking_reference(),
                random.choice(passenger_ids),
                random.choice(['call', 'chat', 'email', 'escalation']),
                f"AGT{random.randint(100, 999)}",
                random.choice([
                    'Customer inquiring about flight status',
                    'Baggage issue reported',
                    'Seat change request',
                    'Refund request submitted',
                    'Special assistance needed',
                    'Meal preference update',
                    'Flight cancellation inquiry',
                    'Upgrade request'
                ]),
                random.choice([
                    'Issue resolved successfully',
                    'Escalated to supervisor',
                    'Refund processed',
                    'Booking modified',
                    'Information provided',
                    'Callback scheduled'
                ]),
                random.choice(['open', 'resolved', 'escalated'])
            ))
        
        # Commit all changes
        conn.commit()
        print("✅ Data generation completed successfully!")
        print(f"Generated data for:")
        print(f"  - 100 passengers")
        print(f"  - 150 bookings")
        print(f"  - 200 flights")
        print(f"  - 40 trip bookings")
        print(f"  - 60 excursion bookings")
        print(f"  - And many more related records across all tables")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        conn.rollback()
        raise
    
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # Install required packages first
    print("Make sure to install required packages:")
    print("pip install psycopg2-binary faker")
    print()
    
    main()