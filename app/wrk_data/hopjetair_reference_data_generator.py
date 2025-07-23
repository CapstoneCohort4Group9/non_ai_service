#!/usr/bin/env python3
"""
HopJetAir Reference Data Generator
Creates realistic reference data for the airline database using Faker.
Idempotent - can be run multiple times safely.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from faker import Faker
import random
from datetime import datetime, timedelta
import logging

# Database configuration
DB_URL = "postgresql://hopjetair:SecurePass123!@localhost:5432/hopjetairline_db"

# Initialize Faker
fake = Faker()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReferenceDataGenerator:
    def __init__(self, db_url):
        self.db_url = db_url
        self.conn = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.conn.autocommit = False
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute query with error handling"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                self.conn.commit()
                return cur.rowcount
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Query execution failed: {e}")
            raise
    
    def create_airlines(self):
        """Create airlines reference data"""
        logger.info("Creating airlines reference data...")
        
        # Predefined airlines including required ones
        airlines_data = [
            ('AI', 'AIC', 'Air India', 'India', 'Star Alliance'),
            ('HJ', 'HJA', 'HopJetAir', 'United States', None),
            ('AA', 'AAL', 'American Airlines', 'United States', 'Oneworld'),
            ('DL', 'DAL', 'Delta Air Lines', 'United States', 'SkyTeam'),
            ('UA', 'UAL', 'United Airlines', 'United States', 'Star Alliance'),
            ('BA', 'BAW', 'British Airways', 'United Kingdom', 'Oneworld'),
            ('LH', 'DLH', 'Lufthansa', 'Germany', 'Star Alliance'),
            ('AF', 'AFR', 'Air France', 'France', 'SkyTeam'),
            ('KL', 'KLM', 'KLM Royal Dutch Airlines', 'Netherlands', 'SkyTeam'),
            ('EK', 'UAE', 'Emirates', 'United Arab Emirates', None),
            ('QR', 'QTR', 'Qatar Airways', 'Qatar', 'Oneworld'),
            ('SQ', 'SIA', 'Singapore Airlines', 'Singapore', 'Star Alliance'),
            ('CX', 'CPA', 'Cathay Pacific', 'Hong Kong', 'Oneworld'),
            ('JL', 'JAL', 'Japan Airlines', 'Japan', 'Oneworld'),
            ('NH', 'ANA', 'All Nippon Airways', 'Japan', 'Star Alliance'),
            ('TK', 'THY', 'Turkish Airlines', 'Turkey', 'Star Alliance'),
            ('6E', 'IGO', 'IndiGo', 'India', None),
            ('SG', 'SEJ', 'SpiceJet', 'India', None),
            ('G8', 'GOW', 'GoAir', 'India', None),
            ('I5', 'IAD', 'AirAsia India', 'India', None),
        ]
        
        # Check existing airlines
        existing_query = "SELECT iata_code FROM airlines"
        existing_airlines = {row['iata_code'] for row in self.execute_query(existing_query, fetch=True)}
        
        insert_query = """
        INSERT INTO airlines (iata_code, icao_code, name, country, alliance)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (iata_code) DO NOTHING
        """
        
        inserted_count = 0
        for airline_data in airlines_data:
            if airline_data[0] not in existing_airlines:
                self.execute_query(insert_query, airline_data)
                inserted_count += 1
        
        logger.info(f"Airlines: {inserted_count} new records inserted, {len(existing_airlines)} already existed")
    
    def create_airports(self):
        """Create airports reference data"""
        logger.info("Creating airports reference data...")
        
        # Predefined airports including Indian ones
        airports_data = [
            # Indian Airports
            ('DEL', 'VIDP', 'Indira Gandhi International Airport', 'Delhi', 'India', 'Asia/Kolkata', 28.5665, 77.1031),
            ('BOM', 'VABB', 'Chhatrapati Shivaji Maharaj International Airport', 'Mumbai', 'India', 'Asia/Kolkata', 19.0896, 72.8656),
            ('BLR', 'VOBL', 'Kempegowda International Airport', 'Bangalore', 'India', 'Asia/Kolkata', 13.1986, 77.7066),
            ('MAA', 'VOMM', 'Chennai International Airport', 'Chennai', 'India', 'Asia/Kolkata', 12.9941, 80.1709),
            ('CCU', 'VECC', 'Netaji Subhas Chandra Bose International Airport', 'Kolkata', 'India', 'Asia/Kolkata', 22.6546, 88.4467),
            ('HYD', 'VOHS', 'Rajiv Gandhi International Airport', 'Hyderabad', 'India', 'Asia/Kolkata', 17.2403, 78.4294),
            ('COK', 'VOCI', 'Cochin International Airport', 'Kochi', 'India', 'Asia/Kolkata', 10.1520, 76.4019),
            ('GOI', 'VOGO', 'Goa International Airport', 'Panaji', 'India', 'Asia/Kolkata', 15.3808, 73.8314),
            
            # Major International Airports
            ('JFK', 'KJFK', 'John F. Kennedy International Airport', 'New York', 'United States', 'America/New_York', 40.6413, -73.7781),
            ('LAX', 'KLAX', 'Los Angeles International Airport', 'Los Angeles', 'United States', 'America/Los_Angeles', 33.9425, -118.4081),
            ('LHR', 'EGLL', 'London Heathrow Airport', 'London', 'United Kingdom', 'Europe/London', 51.4700, -0.4543),
            ('CDG', 'LFPG', 'Charles de Gaulle Airport', 'Paris', 'France', 'Europe/Paris', 49.0097, 2.5479),
            ('FRA', 'EDDF', 'Frankfurt Airport', 'Frankfurt', 'Germany', 'Europe/Berlin', 50.0379, 8.5622),
            ('DXB', 'OMDB', 'Dubai International Airport', 'Dubai', 'United Arab Emirates', 'Asia/Dubai', 25.2532, 55.3657),
            ('SIN', 'WSSS', 'Singapore Changi Airport', 'Singapore', 'Singapore', 'Asia/Singapore', 1.3644, 103.9915),
            ('NRT', 'RJAA', 'Narita International Airport', 'Tokyo', 'Japan', 'Asia/Tokyo', 35.7720, 140.3929),
            ('SYD', 'YSSY', 'Sydney Kingsford Smith Airport', 'Sydney', 'Australia', 'Australia/Sydney', -33.9399, 151.1753),
            ('YYZ', 'CYYZ', 'Toronto Pearson International Airport', 'Toronto', 'Canada', 'America/Toronto', 43.6777, -79.6248),
            ('ORD', 'KORD', 'O\'Hare International Airport', 'Chicago', 'United States', 'America/Chicago', 41.9742, -87.9073),
            ('ATL', 'KATL', 'Hartsfield-Jackson Atlanta International Airport', 'Atlanta', 'United States', 'America/New_York', 33.6407, -84.4277),
        ]
        
        # Check existing airports
        existing_query = "SELECT iata_code FROM airports"
        existing_airports = {row['iata_code'] for row in self.execute_query(existing_query, fetch=True)}
        
        insert_query = """
        INSERT INTO airports (iata_code, icao_code, name, city, country, timezone, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (iata_code) DO NOTHING
        """
        
        inserted_count = 0
        for airport_data in airports_data:
            if airport_data[0] not in existing_airports:
                self.execute_query(insert_query, airport_data)
                inserted_count += 1
        
        logger.info(f"Airports: {inserted_count} new records inserted, {len(existing_airports)} already existed")
    
    def create_aircraft_types(self):
        """Create aircraft types reference data"""
        logger.info("Creating aircraft types reference data...")
        
        aircraft_types_data = [
            ('Boeing', '737-800', '738', 'B738', 162, 0, 16, 0, 178, 5765),
            ('Boeing', '737-900', '739', 'B739', 177, 0, 20, 0, 197, 5083),
            ('Boeing', '777-300ER', '77W', 'B77W', 296, 28, 42, 8, 374, 14594),
            ('Boeing', '787-8', '788', 'B788', 234, 28, 28, 0, 290, 15750),
            ('Boeing', '787-9', '789', 'B789', 254, 21, 30, 0, 305, 16745),
            ('Airbus', 'A320-200', '320', 'A320', 150, 0, 12, 0, 162, 6150),
            ('Airbus', 'A321-200', '321', 'A321', 185, 0, 16, 0, 201, 5950),
            ('Airbus', 'A330-300', '333', 'A333', 277, 24, 36, 0, 337, 11750),
            ('Airbus', 'A350-900', '359', 'A359', 253, 56, 42, 0, 351, 15372),
            ('Airbus', 'A380-800', '388', 'A388', 399, 76, 60, 14, 549, 15700),
            ('Embraer', 'E175', 'E75', 'E170', 76, 0, 12, 0, 88, 3334),
            ('Embraer', 'E190', 'E90', 'E190', 97, 0, 8, 0, 105, 4537),
            ('Boeing', '757-200', '752', 'B752', 178, 0, 16, 0, 194, 7222),
            ('Boeing', '767-300ER', '763', 'B763', 218, 18, 30, 0, 266, 11093),
            ('Airbus', 'A319-100', '319', 'A319', 124, 0, 8, 0, 132, 6850),
        ]
        
        # Check existing aircraft types
        existing_query = "SELECT manufacturer, model FROM aircraft_types"
        existing_types = {(row['manufacturer'], row['model']) for row in self.execute_query(existing_query, fetch=True)}
        
        insert_query = """
        INSERT INTO aircraft_types (manufacturer, model, iata_code, icao_code, seats_economy, 
                                  seats_premium_economy, seats_business, seats_first, total_seats, range_km)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (manufacturer, model) DO NOTHING
        """
        
        inserted_count = 0
        for aircraft_data in aircraft_types_data:
            if (aircraft_data[0], aircraft_data[1]) not in existing_types:
                self.execute_query(insert_query, aircraft_data)
                inserted_count += 1
        
        logger.info(f"Aircraft Types: {inserted_count} new records inserted, {len(existing_types)} already existed")
    
    def create_routes(self):
        """Create flight routes between airports"""
        logger.info("Creating flight routes...")
        
        # Get all airports
        airports_query = "SELECT id, iata_code FROM airports ORDER BY id"
        airports = self.execute_query(airports_query, fetch=True)
        
        if len(airports) < 2:
            logger.warning("Not enough airports to create routes")
            return
        
        # Check existing routes
        existing_query = "SELECT origin_airport_id, destination_airport_id FROM routes"
        existing_routes = {(row['origin_airport_id'], row['destination_airport_id']) 
                          for row in self.execute_query(existing_query, fetch=True)}
        
        insert_query = """
        INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (origin_airport_id, destination_airport_id) DO NOTHING
        """
        
        inserted_count = 0
        # Create routes between major hubs and popular destinations
        popular_routes = [
            # India domestic routes
            ('DEL', 'BOM'), ('DEL', 'BLR'), ('DEL', 'MAA'), ('DEL', 'CCU'),
            ('BOM', 'BLR'), ('BOM', 'MAA'), ('BOM', 'COK'), ('BOM', 'GOI'),
            
            # India international routes
            ('DEL', 'DXB'), ('BOM', 'DXB'), ('DEL', 'LHR'), ('BOM', 'LHR'),
            ('DEL', 'SIN'), ('BOM', 'SIN'), ('DEL', 'JFK'), ('BOM', 'JFK'),
            
            # Major international routes
            ('JFK', 'LHR'), ('LAX', 'NRT'), ('LHR', 'CDG'), ('FRA', 'SIN'),
            ('DXB', 'SIN'), ('SYD', 'SIN'), ('ORD', 'LHR'), ('ATL', 'CDG'),
        ]
        
        airport_lookup = {apt['iata_code']: apt['id'] for apt in airports}
        
        for origin_code, dest_code in popular_routes:
            if origin_code in airport_lookup and dest_code in airport_lookup:
                origin_id = airport_lookup[origin_code]
                dest_id = airport_lookup[dest_code]
                
                if (origin_id, dest_id) not in existing_routes:
                    # Calculate approximate distance and duration (simplified)
                    distance = random.randint(500, 8000)  # km
                    duration = int(distance / 8.5)  # rough flight speed approximation
                    
                    self.execute_query(insert_query, (origin_id, dest_id, distance, duration))
                    inserted_count += 1
                
                # Create return route
                if (dest_id, origin_id) not in existing_routes:
                    self.execute_query(insert_query, (dest_id, origin_id, distance, duration))
                    inserted_count += 1
        
        logger.info(f"Routes: {inserted_count} new records inserted")
    
    def create_trip_packages(self):
        """Create trip packages"""
        logger.info("Creating trip packages...")
        
        # Get some destination cities from airports
        destinations_query = """
        SELECT DISTINCT city, country FROM airports 
        WHERE country IN ('India', 'United Kingdom', 'France', 'Japan', 'Singapore', 'United Arab Emirates')
        LIMIT 15
        """
        destinations = self.execute_query(destinations_query, fetch=True)
        
        # Check existing packages
        existing_query = "SELECT package_code FROM trip_packages"
        existing_packages = {row['package_code'] for row in self.execute_query(existing_query, fetch=True)}
        
        insert_query = """
        INSERT INTO trip_packages (package_code, name, description, destination_city, destination_country,
                                 duration_days, price_per_person, includes_flight, includes_hotel, 
                                 includes_activities, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (package_code) DO NOTHING
        """
        
        categories = ['leisure', 'business', 'adventure', 'cultural']
        inserted_count = 0
        
        for i, dest in enumerate(destinations):
            package_code = f"PKG{i+1:03d}"
            if package_code not in existing_packages:
                package_data = (
                    package_code,
                    f"{dest['city']} {random.choice(['Explorer', 'Adventure', 'Getaway', 'Discovery'])}",
                    f"Explore the beautiful city of {dest['city']} with our curated travel experience.",
                    dest['city'],
                    dest['country'],
                    random.choice([3, 5, 7, 10, 14]),
                    random.randint(800, 3500),
                    True,
                    True,
                    random.choice([True, False]),
                    random.choice(categories)
                )
                self.execute_query(insert_query, package_data)
                inserted_count += 1
        
        logger.info(f"Trip Packages: {inserted_count} new records inserted")
    
    def create_excursions(self):
        """Create excursions and activities"""
        logger.info("Creating excursions...")
        
        # Get destination cities
        destinations_query = "SELECT DISTINCT city, country FROM airports LIMIT 10"
        destinations = self.execute_query(destinations_query, fetch=True)
        
        excursion_templates = [
            ('City Walking Tour', 'cultural', 4, 45, 'easy'),
            ('Food Tasting Experience', 'cultural', 3, 65, 'easy'),
            ('Historical Sites Visit', 'historical', 6, 85, 'moderate'),
            ('Adventure Hiking', 'adventure', 8, 120, 'challenging'),
            ('Museum Guided Tour', 'cultural', 3, 35, 'easy'),
            ('Sunset Photography Tour', 'nature', 4, 75, 'moderate'),
            ('Local Market Experience', 'cultural', 2, 25, 'easy'),
            ('Wildlife Safari', 'nature', 10, 200, 'moderate'),
        ]
        
        # Check existing excursions
        existing_query = "SELECT name, destination_city FROM excursions"
        existing_excursions = {(row['name'], row['destination_city']) 
                              for row in self.execute_query(existing_query, fetch=True)}
        
        insert_query = """
        INSERT INTO excursions (name, destination_city, destination_country, description,
                              duration_hours, price_per_person, category, max_participants,
                              includes_transport, includes_guide, difficulty_level)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        inserted_count = 0
        for dest in destinations:
            for template in excursion_templates:
                excursion_name = f"{dest['city']} {template[0]}"
                
                if (excursion_name, dest['city']) not in existing_excursions:
                    excursion_data = (
                        excursion_name,
                        dest['city'],
                        dest['country'],
                        f"Experience {template[0].lower()} in the beautiful city of {dest['city']}.",
                        template[2],  # duration_hours
                        template[3],  # price_per_person
                        template[1],  # category
                        random.randint(8, 25),  # max_participants
                        True,  # includes_transport
                        template[1] in ['cultural', 'historical'],  # includes_guide
                        template[4]  # difficulty_level
                    )
                    self.execute_query(insert_query, excursion_data)
                    inserted_count += 1
        
        logger.info(f"Excursions: {inserted_count} new records inserted")
    
    def create_aircraft_fleet(self):
        """Create aircraft fleet"""
        logger.info("Creating aircraft fleet...")
        
        # Get airlines and aircraft types
        airlines_query = "SELECT id, iata_code FROM airlines"
        aircraft_types_query = "SELECT id, manufacturer, model FROM aircraft_types"
        
        airlines = self.execute_query(airlines_query, fetch=True)
        aircraft_types = self.execute_query(aircraft_types_query, fetch=True)
        
        if not airlines or not aircraft_types:
            logger.warning("No airlines or aircraft types found")
            return
        
        # Check existing aircraft
        existing_query = "SELECT registration FROM aircraft"
        existing_aircraft = {row['registration'] for row in self.execute_query(existing_query, fetch=True)}
        
        insert_query = """
        INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (registration) DO NOTHING
        """
        
        inserted_count = 0
        target_fleet_size = 50
        
        for i in range(target_fleet_size):
            # Generate registration number
            airline = random.choice(airlines)
            registration = f"VT-{fake.lexify('???').upper()}"  # Indian style registration
            
            if registration not in existing_aircraft:
                aircraft_data = (
                    registration,
                    random.choice(aircraft_types)['id'],
                    airline['id'],
                    'active',
                    fake.date_between(start_date='-10y', end_date='-1y')
                )
                self.execute_query(insert_query, aircraft_data)
                inserted_count += 1
                existing_aircraft.add(registration)
        
        logger.info(f"Aircraft Fleet: {inserted_count} new records inserted")
    
    def create_seat_maps(self):
        """Create seat maps for aircraft types"""
        logger.info("Creating seat maps...")
        
        # Get aircraft types
        aircraft_types_query = "SELECT id, seats_economy, seats_business, seats_first FROM aircraft_types"
        aircraft_types = self.execute_query(aircraft_types_query, fetch=True)
        
        # Check existing seat maps
        existing_query = "SELECT DISTINCT aircraft_type_id FROM seat_maps"
        existing_seat_maps = {row['aircraft_type_id'] for row in self.execute_query(existing_query, fetch=True)}
        
        insert_query = """
        INSERT INTO seat_maps (aircraft_type_id, seat_number, seat_type, class_of_service, 
                             is_exit_row, extra_legroom)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        inserted_count = 0
        
        for aircraft_type in aircraft_types:
            if aircraft_type['id'] in existing_seat_maps:
                continue
                
            aircraft_type_id = aircraft_type['id']
            
            # Generate seats for economy class
            row = 1
            for _ in range(aircraft_type['seats_economy'] // 6):  # 6 seats per row (3-3 config)
                for seat_letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                    seat_number = f"{row}{seat_letter}"
                    seat_type = 'window' if seat_letter in ['A', 'F'] else ('aisle' if seat_letter in ['C', 'D'] else 'middle')
                    is_exit_row = row % 8 == 0  # Every 8th row is exit row
                    
                    seat_data = (aircraft_type_id, seat_number, seat_type, 'economy', is_exit_row, is_exit_row)
                    self.execute_query(insert_query, seat_data)
                    inserted_count += 1
                row += 1
            
            # Generate seats for business class if applicable
            if aircraft_type['seats_business'] > 0:
                for _ in range(aircraft_type['seats_business'] // 4):  # 4 seats per row (2-2 config)
                    for seat_letter in ['A', 'B', 'E', 'F']:
                        seat_number = f"{row}{seat_letter}"
                        seat_type = 'window' if seat_letter in ['A', 'F'] else 'aisle'
                        
                        seat_data = (aircraft_type_id, seat_number, seat_type, 'business', False, True)
                        self.execute_query(insert_query, seat_data)
                        inserted_count += 1
                    row += 1
        
        logger.info(f"Seat Maps: {inserted_count} new records inserted")
    
    def create_flight_schedules(self):
        """Create flight schedules"""
        logger.info("Creating flight schedules...")
        
        # Get airlines, routes, and aircraft types
        airlines_query = "SELECT id, iata_code FROM airlines"
        routes_query = "SELECT id, origin_airport_id, destination_airport_id FROM routes LIMIT 20"
        aircraft_types_query = "SELECT id FROM aircraft_types"
        
        airlines = self.execute_query(airlines_query, fetch=True)
        routes = self.execute_query(routes_query, fetch=True)
        aircraft_types = self.execute_query(aircraft_types_query, fetch=True)
        
        if not airlines or not routes or not aircraft_types:
            logger.warning("Missing required data for flight schedules")
            return
        
        # Check existing schedules
        existing_query = "SELECT flight_number, airline_id FROM flight_schedules"
        existing_schedules = {(row['flight_number'], row['airline_id']) 
                            for row in self.execute_query(existing_query, fetch=True)}
        
        insert_query = """
        INSERT INTO flight_schedules (flight_number, airline_id, route_id, aircraft_type_id,
                                    departure_time, arrival_time, days_of_week, valid_from, valid_to)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        inserted_count = 0
        
        for i, route in enumerate(routes):
            airline = random.choice(airlines)
            flight_number = f"{airline['iata_code']}{random.randint(100, 9999)}"
            
            if (flight_number, airline['id']) not in existing_schedules:
                departure_time = fake.time_object()
                # Add random flight duration (1-8 hours)
                arrival_time = (datetime.combine(datetime.today(), departure_time) + 
                              timedelta(hours=random.randint(1, 8))).time()
                
                schedule_data = (
                    flight_number,
                    airline['id'],
                    route['id'],
                    random.choice(aircraft_types)['id'],
                    departure_time,
                    arrival_time,
                    'MTWTFSS',  # Daily flights
                    datetime.now().date(),
                    datetime.now().date() + timedelta(days=365)
                )
                self.execute_query(insert_query, schedule_data)
                inserted_count += 1
        
        logger.info(f"Flight Schedules: {inserted_count} new records inserted")
    
    def generate_all_reference_data(self):
        """Generate all reference data"""
        try:
            self.connect()
            
            # Create reference data in dependency order
            self.create_airlines()
            self.create_airports()
            self.create_aircraft_types()
            self.create_routes()
            self.create_trip_packages()
            self.create_excursions()
            self.create_aircraft_fleet()
            self.create_seat_maps()
            self.create_flight_schedules()
            
            logger.info("All reference data creation completed successfully!")
            
        except Exception as e:
            logger.error(f"Failed to generate reference data: {e}")
            raise
        finally:
            self.disconnect()

def main():
    """Main function"""
    generator = ReferenceDataGenerator(DB_URL)
    generator.generate_all_reference_data()

if __name__ == "__main__":
    main()
