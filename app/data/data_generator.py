import random
import string
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from faker import Faker
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database_models import *

fake = Faker()

class HopJetAirDataGenerator:
    def __init__(self, database_url):
        self.engine = create_async_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine, class_=AsyncSession)
        
    def generate_booking_reference(self):
        """Generate airline-style booking reference"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def generate_flight_number(self, airline_code):
        """Generate realistic flight numbers"""
        return f"{airline_code}{random.randint(100, 9999)}"
    
    def generate_aircraft_registration(self):
        """Generate aircraft registration"""
        country_codes = ['N', 'G-', 'D-', 'F-', 'JA', 'VH-']
        country = random.choice(country_codes)
        if country in ['N']:
            return f"{country}{random.randint(100, 999)}{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}"
        else:
            return f"{country}{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}"
    
    def create_airlines_data(self):
        """Create airline data"""
        airlines_data = [
            {
                'iata_code': 'HJ',
                'icao_code': 'HJA',
                'name': 'HopJetAir',
                'country': 'United States',
                'alliance': 'Star Alliance'
            },
            {
                'iata_code': 'AA',
                'icao_code': 'AAL',
                'name': 'American Airlines',
                'country': 'United States',
                'alliance': 'Oneworld'
            },
            {
                'iata_code': 'DL',
                'icao_code': 'DAL',
                'name': 'Delta Air Lines',
                'country': 'United States',
                'alliance': 'SkyTeam'
            },
            {
                'iata_code': 'UA',
                'icao_code': 'UAL',
                'name': 'United Airlines',
                'country': 'United States',
                'alliance': 'Star Alliance'
            },
            {
                'iata_code': 'BA',
                'icao_code': 'BAW',
                'name': 'British Airways',
                'country': 'United Kingdom',
                'alliance': 'Oneworld'
            }
        ]
        return airlines_data
    
    def create_aircraft_types_data(self):
        """Create aircraft types data"""
        aircraft_types = [
            {
                'manufacturer': 'Boeing',
                'model': '737-800',
                'iata_code': '738',
                'icao_code': 'B738',
                'seats_economy': 162,
                'seats_premium_economy': 0,
                'seats_business': 16,
                'seats_first': 0,
                'total_seats': 178,
                'range_km': 5765
            },
            {
                'manufacturer': 'Boeing',
                'model': '777-300ER',
                'iata_code': '77W',
                'icao_code': 'B77W',
                'seats_economy': 296,
                'seats_premium_economy': 24,
                'seats_business': 42,
                'seats_first': 8,
                'total_seats': 370,
                'range_km': 13649
            },
            {
                'manufacturer': 'Airbus',
                'model': 'A320',
                'iata_code': '320',
                'icao_code': 'A320',
                'seats_economy': 150,
                'seats_premium_economy': 0,
                'seats_business': 12,
                'seats_first': 0,
                'total_seats': 162,
                'range_km': 6150
            },
            {
                'manufacturer': 'Airbus',
                'model': 'A350-900',
                'iata_code': '359',
                'icao_code': 'A359',
                'seats_economy': 253,
                'seats_premium_economy': 21,
                'seats_business': 36,
                'seats_first': 0,
                'total_seats': 310,
                'range_km': 15000
            },
            {
                'manufacturer': 'Boeing',
                'model': '787-9',
                'iata_code': '789',
                'icao_code': 'B789',
                'seats_economy': 216,
                'seats_premium_economy': 28,
                'seats_business': 30,
                'seats_first': 0,
                'total_seats': 274,
                'range_km': 14140
            }
        ]
        return aircraft_types
    
    def create_airports_data(self):
        """Create major airports data"""
        airports_data = [
            # US Airports
            {'iata_code': 'JFK', 'icao_code': 'KJFK', 'name': 'John F. Kennedy International', 'city': 'New York', 'country': 'United States', 'timezone': 'America/New_York', 'latitude': 40.6413, 'longitude': -73.7781},
            {'iata_code': 'LAX', 'icao_code': 'KLAX', 'name': 'Los Angeles International', 'city': 'Los Angeles', 'country': 'United States', 'timezone': 'America/Los_Angeles', 'latitude': 33.9425, 'longitude': -118.4081},
            {'iata_code': 'ORD', 'icao_code': 'KORD', 'name': "O'Hare International", 'city': 'Chicago', 'country': 'United States', 'timezone': 'America/Chicago', 'latitude': 41.9742, 'longitude': -87.9073},
            {'iata_code': 'MIA', 'icao_code': 'KMIA', 'name': 'Miami International', 'city': 'Miami', 'country': 'United States', 'timezone': 'America/New_York', 'latitude': 25.7959, 'longitude': -80.2870},
            {'iata_code': 'DFW', 'icao_code': 'KDFW', 'name': 'Dallas/Fort Worth International', 'city': 'Dallas', 'country': 'United States', 'timezone': 'America/Chicago', 'latitude': 32.8998, 'longitude': -97.0403},
            {'iata_code': 'SEA', 'icao_code': 'KSEA', 'name': 'Seattle-Tacoma International', 'city': 'Seattle', 'country': 'United States', 'timezone': 'America/Los_Angeles', 'latitude': 47.4502, 'longitude': -122.3088},
            {'iata_code': 'ATL', 'icao_code': 'KATL', 'name': 'Hartsfield-Jackson Atlanta International', 'city': 'Atlanta', 'country': 'United States', 'timezone': 'America/New_York', 'latitude': 33.6407, 'longitude': -84.4277},
            {'iata_code': 'BOS', 'icao_code': 'KBOS', 'name': 'Logan International', 'city': 'Boston', 'country': 'United States', 'timezone': 'America/New_York', 'latitude': 42.3656, 'longitude': -71.0096},
            # International Airports
            {'iata_code': 'LHR', 'icao_code': 'EGLL', 'name': 'Heathrow', 'city': 'London', 'country': 'United Kingdom', 'timezone': 'Europe/London', 'latitude': 51.4700, 'longitude': -0.4543},
            {'iata_code': 'CDG', 'icao_code': 'LFPG', 'name': 'Charles de Gaulle', 'city': 'Paris', 'country': 'France', 'timezone': 'Europe/Paris', 'latitude': 49.0097, 'longitude': 2.5479},
            {'iata_code': 'FRA', 'icao_code': 'EDDF', 'name': 'Frankfurt am Main', 'city': 'Frankfurt', 'country': 'Germany', 'timezone': 'Europe/Berlin', 'latitude': 50.0379, 'longitude': 8.5622},
            {'iata_code': 'MAD', 'icao_code': 'LEMD', 'name': 'Madrid-Barajas', 'city': 'Madrid', 'country': 'Spain', 'timezone': 'Europe/Madrid', 'latitude': 40.4839, 'longitude': -3.5680},
            {'iata_code': 'AMS', 'icao_code': 'EHAM', 'name': 'Amsterdam Airport Schiphol', 'city': 'Amsterdam', 'country': 'Netherlands', 'timezone': 'Europe/Amsterdam', 'latitude': 52.3105, 'longitude': 4.7683},
            {'iata_code': 'NRT', 'icao_code': 'RJAA', 'name': 'Narita International', 'city': 'Tokyo', 'country': 'Japan', 'timezone': 'Asia/Tokyo', 'latitude': 35.7720, 'longitude': 140.3929},
            {'iata_code': 'SYD', 'icao_code': 'YSSY', 'name': 'Sydney Kingsford Smith', 'city': 'Sydney', 'country': 'Australia', 'timezone': 'Australia/Sydney', 'latitude': -33.9399, 'longitude': 151.1753},
            {'iata_code': 'YYZ', 'icao_code': 'CYYZ', 'name': 'Toronto Pearson International', 'city': 'Toronto', 'country': 'Canada', 'timezone': 'America/Toronto', 'latitude': 43.6777, 'longitude': -79.6248}
        ]
        return airports_data
    
    def create_trip_packages_data(self):
        """Create trip packages"""
        packages = [
            {
                'package_code': 'MAD001',
                'name': 'Madrid Cultural Explorer',
                'description': 'Discover the rich history and culture of Madrid with museum tours, flamenco shows, and traditional tapas experiences.',
                'destination_city': 'Madrid',
                'destination_country': 'Spain',
                'duration_days': 5,
                'price_per_person': 1299.00,
                'category': 'cultural'
            },
            {
                'package_code': 'PAR002',
                'name': 'Paris Romance Package',
                'description': 'Experience the city of love with Seine river cruises, Michelin dining, and iconic landmark tours.',
                'destination_city': 'Paris',
                'destination_country': 'France',
                'duration_days': 4,
                'price_per_person': 1599.00,
                'category': 'leisure'
            },
            {
                'package_code': 'LON003',
                'name': 'London Heritage Tour',
                'description': 'Explore British history with palace tours, afternoon tea, and West End shows.',
                'destination_city': 'London',
                'destination_country': 'United Kingdom',
                'duration_days': 6,
                'price_per_person': 1899.00,
                'category': 'cultural'
            },
            {
                'package_code': 'TKY004',
                'name': 'Tokyo Adventure',
                'description': 'Modern meets traditional in this exciting journey through Japan\'s capital.',
                'destination_city': 'Tokyo',
                'destination_country': 'Japan',
                'duration_days': 7,
                'price_per_person': 2299.00,
                'category': 'adventure'
            }
        ]
        return packages
    
    def create_excursions_data(self):
        """Create excursions"""
        excursions = [
            {
                'name': 'Prado Museum Guided Tour',
                'destination_city': 'Madrid',
                'destination_country': 'Spain',
                'description': 'Skip-the-line access to world-famous art collection',
                'duration_hours': 3,
                'price_per_person': 45.00,
                'category': 'cultural',
                'max_participants': 25,
                'difficulty_level': 'easy'
            },
            {
                'name': 'Flamenco Show with Dinner',
                'destination_city': 'Madrid',
                'destination_country': 'Spain',
                'description': 'Authentic flamenco performance with traditional Spanish cuisine',
                'duration_hours': 4,
                'price_per_person': 89.00,
                'category': 'cultural',
                'max_participants': 50,
                'difficulty_level': 'easy'
            },
            {
                'name': 'Versailles Palace Day Trip',
                'destination_city': 'Paris',
                'destination_country': 'France',
                'description': 'Full day trip to the magnificent Palace of Versailles',
                'duration_hours': 8,
                'price_per_person': 120.00,
                'category': 'historical',
                'max_participants': 30,
                'difficulty_level': 'moderate'
            }
        ]
        return excursions
    
    def create_policies_data(self):
        """Create airline policies"""
        policies = [
            {
                'policy_type': 'Flight Change Fee',
                'policy_category': 'change',
                'route_type': 'domestic',
                'class_of_service': 'economy',
                'description': 'Fee for changing flight date/time for domestic economy flights',
                'fee_amount': 75.00,
                'conditions': 'Changes allowed up to 24 hours before departure'
            },
            {
                'policy_type': 'Cancellation Fee',
                'policy_category': 'cancellation',
                'route_type': 'international',
                'class_of_service': 'economy',
                'description': 'Cancellation fee for international economy flights',
                'fee_amount': 200.00,
                'conditions': 'Non-refundable tickets. Cancellation allowed with fee.'
            },
            {
                'policy_type': 'Checked Baggage',
                'policy_category': 'baggage',
                'route_type': 'domestic',
                'description': 'First checked bag fee for domestic flights',
                'fee_amount': 35.00,
                'conditions': 'Up to 50 lbs (23 kg)'
            }
        ]
        return policies
    
    def generate_passengers(self, count=300):
        """Generate passenger data"""
        passengers = []
        tier_statuses = ['basic', 'silver', 'gold', 'platinum']
        
        for _ in range(count):
            passenger = {
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'email': fake.email(),
                'phone': fake.phone_number(),
                'date_of_birth': fake.date_of_birth(minimum_age=18, maximum_age=80),
                'nationality': fake.country(),
                'passport_number': fake.bothify(text='??#######'),
                'passport_expiry': fake.date_between(start_date='today', end_date='+10y'),
                'frequent_flyer_number': fake.bothify(text='HJ#######'),
                'tier_status': random.choice(tier_statuses)
            }
            passengers.append(passenger)
        
        return passengers
    
    async def populate_database(self):
        """Populate database with all data"""
        # --- CHANGE 4: Use async with for session ---
        async with self.SessionLocal() as db:
            try:
                print("Creating tables...")
                # --- CHANGE 5: Run DDL operations asynchronously ---
                async with self.engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                
                print("Inserting airlines...")
                airlines_data = self.create_airlines_data()
                for airline_data in airlines_data:
                    airline = Airline(**airline_data)
                    db.add(airline)
                await db.commit() # Use await db.commit()
                
                print("Inserting aircraft types...")
                aircraft_types_data = self.create_aircraft_types_data()
                for aircraft_type_data in aircraft_types_data:
                    aircraft_type = AircraftType(**aircraft_type_data)
                    db.add(aircraft_type)
                await db.commit()
                
                print("Inserting airports...")
                airports_data = self.create_airports_data()
                for airport_data in airports_data:
                    airport = Airport(**airport_data)
                    db.add(airport)
                await db.commit()
                
                print("Inserting passengers...")
                passengers_data = self.generate_passengers(300)
                for passenger_data in passengers_data:
                    passenger = Passenger(**passenger_data)
                    db.add(passenger)
                await db.commit()
                
                print("Inserting trip packages...")
                packages_data = self.create_trip_packages_data()
                for package_data in packages_data:
                    package = TripPackage(**package_data)
                    db.add(package)
                await db.commit()
                
                print("Inserting excursions...")
                excursions_data = self.create_excursions_data()
                for excursion_data in excursions_data:
                    excursion = Excursion(**excursion_data)
                    db.add(excursion)
                await db.commit()
                
                print("Inserting policies...")
                policies_data = self.create_policies_data()
                for policy_data in policies_data:
                    policy = AirlinePolicy(**policy_data)
                    db.add(policy)
                await db.commit()
                
                # Get IDs for further data generation (needs to be async queries)
                # --- CHANGE 6: Use await db.execute() for queries ---
                airlines_result = await db.execute(select(Airline))
                airlines = airlines_result.scalars().all()

                aircraft_types_result = await db.execute(select(AircraftType))
                aircraft_types = aircraft_types_result.scalars().all()

                airports_result = await db.execute(select(Airport))
                airports = airports_types_result.scalars().all()
                
                passengers_result = await db.execute(select(Passenger))
                passengers = passengers_result.scalars().all()
                
                print("Generating aircraft...")
                await self.generate_aircraft(db, airlines, aircraft_types, 50) # Keep async
                
                print("Generating routes...")
                await self.generate_routes(db, airports, 100) # Keep async
                
                print("Generating flights...")
                routes_result = await db.execute(select(Route))
                routes = routes_result.scalars().all()

                aircraft_result = await db.execute(select(Aircraft))
                aircraft = aircraft_result.scalars().all()

                await self.generate_flights(db, airlines, routes, aircraft, 400) # Keep async
                
                print("Generating bookings...")
                flights_result = await db.execute(select(Flight))
                flights = flights_result.scalars().all()

                await self.generate_bookings(db, passengers, flights, 500) # Keep async
                
                print("Generating seat maps...")
                await self.generate_seat_maps(db, aircraft_types) # Keep async
                
                print("Database populated successfully!")
                
            except Exception as e:
                print(f"Error populating database: {e}")
                await db.rollback() # Use await db.rollback()
                raise
            # finally: (No db.close() needed with async with db: )
            #    db.close() # No longer needed

        """Populate database with all data"""
        async with self.SessionLocal() as db:
            try:
                print("Creating tables...")
                async with self.engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                
                print("Inserting airlines...")
                airlines_data = self.create_airlines_data()
                for airline_data in airlines_data:
                    airline = Airline(**airline_data)
                    db.add(airline)
                db.commit()
                
                print("Inserting aircraft types...")
                aircraft_types_data = self.create_aircraft_types_data()
                for aircraft_type_data in aircraft_types_data:
                    aircraft_type = AircraftType(**aircraft_type_data)
                    db.add(aircraft_type)
                db.commit()
                
                print("Inserting airports...")
                airports_data = self.create_airports_data()
                for airport_data in airports_data:
                    airport = Airport(**airport_data)
                    db.add(airport)
                db.commit()
                
                print("Inserting passengers...")
                passengers_data = self.generate_passengers(300)
                for passenger_data in passengers_data:
                    passenger = Passenger(**passenger_data)
                    db.add(passenger)
                db.commit()
                
                print("Inserting trip packages...")
                packages_data = self.create_trip_packages_data()
                for package_data in packages_data:
                    package = TripPackage(**package_data)
                    db.add(package)
                db.commit()
                
                print("Inserting excursions...")
                excursions_data = self.create_excursions_data()
                for excursion_data in excursions_data:
                    excursion = Excursion(**excursion_data)
                    db.add(excursion)
                db.commit()
                
                print("Inserting policies...")
                policies_data = self.create_policies_data()
                for policy_data in policies_data:
                    policy = AirlinePolicy(**policy_data)
                    db.add(policy)
                db.commit()
                
                # Get IDs for further data generation
                airlines = db.query(Airline).all()
                aircraft_types = db.query(AircraftType).all()
                airports = db.query(Airport).all()
                passengers = db.query(Passenger).all()
                
                print("Generating aircraft...")
                self.generate_aircraft(db, airlines, aircraft_types, 50)
                
                print("Generating routes...")
                self.generate_routes(db, airports, 100)
                
                print("Generating flights...")
                routes = db.query(Route).all()
                aircraft = db.query(Aircraft).all()
                self.generate_flights(db, airlines, routes, aircraft, 400)
                
                print("Generating bookings...")
                flights = db.query(Flight).all()
                self.generate_bookings(db, passengers, flights, 500)
                
                print("Generating seat maps...")
                self.generate_seat_maps(db, aircraft_types)
                
                print("Database populated successfully!")
                
            except Exception as e:
                print(f"Error populating database: {e}")
                db.rollback()
                raise
            finally:
                db.close()
    
    async def generate_aircraft(self, db, airlines, aircraft_types, count):
        """Generate aircraft fleet"""
        for _ in range(count):
            aircraft = Aircraft(
                registration=self.generate_aircraft_registration(),
                aircraft_type_id=random.choice(aircraft_types).id,
                airline_id=random.choice(airlines).id,
                status=random.choice(['active', 'maintenance', 'retired']),
                delivery_date=fake.date_between(start_date='-10y', end_date='today')
            )
            db.add(aircraft)
        await db.commit()
    
    async def generate_routes(self, db, airports, count):
        """Generate flight routes"""
        created_routes = set()
        
        for _ in range(count):
            origin = random.choice(airports)
            destination = random.choice([a for a in airports if a.id != origin.id])
            
            route_key = (origin.id, destination.id)
            if route_key in created_routes:
                continue
            
            distance = random.randint(500, 8000)  # km
            duration = int(distance / 8)  # rough flight duration calculation
            
            route = Route(
                origin_airport_id=origin.id,
                destination_airport_id=destination.id,
                distance_km=distance,
                flight_duration_minutes=duration
            )
            db.add(route)
            created_routes.add(route_key)
        
        await db.commit()
    
    async def generate_flights(self, db, airlines, routes, aircraft, count):
        """Generate flights"""
        statuses = ['scheduled', 'boarding', 'departed', 'arrived', 'delayed', 'cancelled']
        
        for _ in range(count):
            airline = random.choice(airlines)
            route = random.choice(routes)
            flight_aircraft = random.choice(aircraft)
            
            # Generate flight for next 6 months
            base_date = datetime.now() + timedelta(days=random.randint(-90, 180))
            departure_time = base_date.replace(
                hour=random.randint(6, 23),
                minute=random.choice([0, 15, 30, 45]),
                second=0,
                microsecond=0
            )
            arrival_time = departure_time + timedelta(minutes=route.flight_duration_minutes)
            
            flight = Flight(
                flight_number=self.generate_flight_number(airline.iata_code),
                airline_id=airline.id,
                aircraft_id=flight_aircraft.id,
                route_id=route.id,
                scheduled_departure=departure_time,
                scheduled_arrival=arrival_time,
                status=random.choice(statuses),
                gate=f"{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 50)}",
                terminal=str(random.randint(1, 4))
            )
            db.add(flight)
        
        await db.commit()
    
    async def generate_bookings(self, db, passengers, flights, count):
        """Generate bookings and booking segments"""
        classes = ['economy', 'premium_economy', 'business', 'first']
        trip_types = ['one-way', 'round-trip', 'multi-city']
        
        for _ in range(count):
            passenger = random.choice(passengers)
            booking_ref = self.generate_booking_reference()
            
            # Ensure unique booking reference
            while db.query(Booking).filter_by(booking_reference=booking_ref).first():
                booking_ref = self.generate_booking_reference()
            
            trip_type = random.choice(trip_types)
            num_segments = 1 if trip_type == 'one-way' else 2 if trip_type == 'round-trip' else random.randint(2, 4)
            
            total_amount = Decimal(str(random.uniform(200, 3000)))
            
            booking = Booking(
                booking_reference=booking_ref,
                passenger_id=passenger.id,
                booking_date=fake.date_time_between(start_date='-6m', end_date='now'),
                total_amount=total_amount,
                currency='USD',
                status=random.choice(['confirmed', 'cancelled']),
                booking_source=random.choice(['website', 'mobile_app', 'call_center', 'travel_agent']),
                trip_type=trip_type
            )
            db.add(booking)
            db.flush()  # Get the booking ID
            
            # Create booking segments
            selected_flights = random.sample(flights, min(num_segments, len(flights)))
            for flight in selected_flights:
                class_of_service = random.choice(classes)
                
                segment = BookingSegment(
                    booking_id=booking.id,
                    flight_id=flight.id,
                    passenger_id=passenger.id,
                    class_of_service=class_of_service,
                    fare_basis=f"{class_of_service[0].upper()}{random.randint(10, 99)}",
                    ticket_number=fake.bothify(text='##########'),
                    seat_number=f"{random.randint(1, 40)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}",
                    baggage_allowance_kg=23 if class_of_service == 'economy' else 32,
                    meal_preference=random.choice(['standard', 'vegetarian', 'vegan', 'kosher', 'halal']),
                    check_in_status=random.choice(['not_checked_in', 'checked_in', 'boarded']),
                    boarding_pass_issued=random.choice([True, False])
                )
                db.add(segment)
        
        await db.commit()
    
    async def generate_seat_maps(self, db, aircraft_types):
        """Generate seat maps for aircraft types"""
        for aircraft_type in aircraft_types:
            # Economy seats
            for row in range(1, 31):  # Rows 1-30 for economy
                for seat_letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                    seat_type = 'window' if seat_letter in ['A', 'F'] else 'aisle' if seat_letter in ['C', 'D'] else 'middle'
                    
                    seat_map = SeatMap(
                        aircraft_type_id=aircraft_type.id,
                        seat_number=f"{row}{seat_letter}",
                        seat_type=seat_type,
                        class_of_service='economy',
                        is_exit_row=(row in [12, 13]),
                        extra_legroom=(row in [1, 12, 13])
                    )
                    db.add(seat_map)
            
            # Business class seats (if applicable)
            if aircraft_type.seats_business > 0:
                for row in range(1, 6):  # Rows 1-5 for business
                    for seat_letter in ['A', 'C', 'H', 'K']:  # 2-2 configuration
                        seat_type = 'window' if seat_letter in ['A', 'K'] else 'aisle'
                        
                        seat_map = SeatMap(
                            aircraft_type_id=aircraft_type.id,
                            seat_number=f"{row}{seat_letter}",
                            seat_type=seat_type,
                            class_of_service='business',
                            extra_legroom=True
                        )
                        db.add(seat_map)
        
        await db.commit()

# Usage example
async def main():
    DATABASE_URL = "postgresql+asyncpg://hopjetair:SecurePass123!@localhost:5432/hopjetair"
    generator = HopJetAirDataGenerator(DATABASE_URL)
    await generator.populate_database()

if __name__ == "__main__":
    asyncio.run(main())