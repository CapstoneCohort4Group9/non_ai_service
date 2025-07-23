import psycopg2
import random
from datetime import datetime, timedelta
import math

# Database connection
DB_URL = "postgresql://hopjetair:SecurePass123!@hopjetair-postgres.cepc0wqo22hd.us-east-1.rds.amazonaws.com:5432/hopjetairline_db"
#DB_URL = "postgresql://hopjetair:SecurePass123!@localhost:5432/hopjetairline_db"

def connect_db():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(DB_URL)

def check_missing_routes():
    """Check what routes are missing and create them"""
    conn = connect_db()
    cur = conn.cursor()
    
    try:
        print("🔍 Checking for missing routes...")
        
        # Get all airports
        cur.execute("SELECT id, iata_code, name, city, latitude, longitude FROM airports ORDER BY id")
        airports = cur.fetchall()
        
        print(f"Found {len(airports)} airports")
        
        # Check specific LHR to CDG route
        cur.execute("""
            SELECT r.id, oa.iata_code as origin, da.iata_code as dest
            FROM routes r
            JOIN airports oa ON r.origin_airport_id = oa.id  
            JOIN airports da ON r.destination_airport_id = da.id
            WHERE oa.id = 6 AND da.id = 7
        """)
        
        lhr_cdg_route = cur.fetchone()
        if lhr_cdg_route:
            print(f"✅ Route LHR→CDG exists: Route ID {lhr_cdg_route[0]}")
        else:
            print("❌ Route LHR→CDG missing!")
            
        # Check reverse route CDG to LHR  
        cur.execute("""
            SELECT r.id, oa.iata_code as origin, da.iata_code as dest
            FROM routes r
            JOIN airports oa ON r.origin_airport_id = oa.id
            JOIN airports da ON r.destination_airport_id = da.id  
            WHERE oa.id = 7 AND da.id = 6
        """)
        
        cdg_lhr_route = cur.fetchone()
        if cdg_lhr_route:
            print(f"✅ Route CDG→LHR exists: Route ID {cdg_lhr_route[0]}")
        else:
            print("❌ Route CDG→LHR missing!")
            
        # Show what routes DO exist
        cur.execute("""
            SELECT COUNT(*) FROM routes
        """)
        total_routes = cur.fetchone()[0]
        print(f"📊 Total routes in database: {total_routes}")
        
        # Show sample of existing routes
        cur.execute("""
            SELECT oa.iata_code as origin, da.iata_code as dest, r.distance_km
            FROM routes r
            JOIN airports oa ON r.origin_airport_id = oa.id
            JOIN airports da ON r.destination_airport_id = da.id
            LIMIT 10
        """)
        
        sample_routes = cur.fetchall()
        print("\n📋 Sample existing routes:")
        for route in sample_routes:
            print(f"  {route[0]} → {route[1]} ({route[2]}km)")
            
        return airports, lhr_cdg_route is None, cdg_lhr_route is None
        
    except Exception as e:
        print(f"❌ Error checking routes: {e}")
        return [], True, True
    finally:
        cur.close()
        conn.close()

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers"""
    # Convert latitude and longitude to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    return c * r

def create_missing_routes():
    """Create missing routes between major airports"""
    conn = connect_db()
    cur = conn.cursor()
    
    try:
        print("🛠️  Creating missing routes...")
        
        # Get airports with coordinates
        cur.execute("SELECT id, iata_code, name, city, latitude, longitude FROM airports")
        airports = cur.fetchall()
        
        # Major airport pairs that should have routes
        major_pairs = [
            ('LHR', 'CDG'),  # London Heathrow ↔ Paris CDG
            ('LHR', 'JFK'),  # London Heathrow ↔ New York JFK  
            ('CDG', 'JFK'),  # Paris CDG ↔ New York JFK
            ('LHR', 'LAX'),  # London Heathrow ↔ Los Angeles
            ('CDG', 'LAX'),  # Paris CDG ↔ Los Angeles
            ('JFK', 'LAX'),  # New York JFK ↔ Los Angeles
            ('ORD', 'LHR'),  # Chicago ↔ London Heathrow
            ('ORD', 'CDG'),  # Chicago ↔ Paris CDG
            ('DFW', 'LHR'),  # Dallas ↔ London Heathrow
            ('MIA', 'LHR'),  # Miami ↔ London Heathrow
        ]
        
        # Create airport lookup
        airport_lookup = {airport[1]: airport for airport in airports}
        
        routes_created = 0
        
        for origin_code, dest_code in major_pairs:
            if origin_code not in airport_lookup or dest_code not in airport_lookup:
                print(f"⚠️  Skipping {origin_code}→{dest_code}: Airport not found")
                continue
                
            origin_airport = airport_lookup[origin_code]
            dest_airport = airport_lookup[dest_code]
            
            # Check if route already exists (both directions)
            cur.execute("""
                SELECT id FROM routes 
                WHERE (origin_airport_id = %s AND destination_airport_id = %s)
                   OR (origin_airport_id = %s AND destination_airport_id = %s)
            """, (origin_airport[0], dest_airport[0], dest_airport[0], origin_airport[0]))
            
            existing_route = cur.fetchone()
            
            if existing_route:
                print(f"✅ Route {origin_code}↔{dest_code} already exists")
                continue
            
            # Calculate distance
            distance = calculate_distance(
                origin_airport[4], origin_airport[5],  # origin lat, lon
                dest_airport[4], dest_airport[5]       # dest lat, lon
            )
            
            # Calculate approximate flight duration (rough estimate)
            # Average commercial speed ~900 km/h, plus taxi/climb time
            duration_minutes = int((distance / 900) * 60) + random.randint(30, 60)
            
            # Create both directions
            for orig, dest in [(origin_airport, dest_airport), (dest_airport, origin_airport)]:
                cur.execute("""
                    INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes)
                    VALUES (%s, %s, %s, %s)
                """, (orig[0], dest[0], int(distance), duration_minutes))
                
                routes_created += 1
                print(f"➕ Created route: {orig[1]} → {dest[1]} ({int(distance)}km, {duration_minutes}min)")
        
        # Also create some additional routes between existing airports
        print("\n🌐 Creating additional routes between all major airports...")
        
        major_airports = [a for a in airports if a[1] in ['LHR', 'CDG', 'JFK', 'LAX', 'ORD', 'DFW', 'MIA', 'FRA', 'AMS', 'YYZ']]
        
        for i, origin in enumerate(major_airports):
            for dest in major_airports[i+1:]:  # Avoid duplicates
                # Check if route exists
                cur.execute("""
                    SELECT id FROM routes 
                    WHERE (origin_airport_id = %s AND destination_airport_id = %s)
                       OR (origin_airport_id = %s AND destination_airport_id = %s)
                """, (origin[0], dest[0], dest[0], origin[0]))
                
                if cur.fetchone():
                    continue  # Route already exists
                
                # Calculate distance
                distance = calculate_distance(origin[4], origin[5], dest[4], dest[5])
                duration_minutes = int((distance / 900) * 60) + random.randint(30, 60)
                
                # Create both directions
                for orig, dst in [(origin, dest), (dest, origin)]:
                    cur.execute("""
                        INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes)
                        VALUES (%s, %s, %s, %s)
                    """, (orig[0], dst[0], int(distance), duration_minutes))
                    
                    routes_created += 1
        
        conn.commit()
        print(f"\n✅ Created {routes_created} new routes successfully!")
        
        # Verify the specific LHR→CDG route now exists
        cur.execute("""
            SELECT r.id, oa.iata_code, da.iata_code, r.distance_km, r.flight_duration_minutes
            FROM routes r
            JOIN airports oa ON r.origin_airport_id = oa.id
            JOIN airports da ON r.destination_airport_id = da.id
            WHERE (oa.id = 6 AND da.id = 7) OR (oa.id = 7 AND da.id = 6)
        """)
        
        lhr_cdg_routes = cur.fetchall()
        print(f"\n🎯 LHR↔CDG routes now available:")
        for route in lhr_cdg_routes:
            print(f"  Route ID {route[0]}: {route[1]} → {route[2]} ({route[3]}km, {route[4]}min)")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating routes: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def verify_flight_search_data():
    """Verify we have all the data needed for flight searches"""
    conn = connect_db()
    cur = conn.cursor()
    
    try:
        print("\n🔍 Verifying flight search data...")
        
        # Check routes
        cur.execute("SELECT COUNT(*) FROM routes")
        route_count = cur.fetchone()[0]
        print(f"📊 Routes: {route_count}")
        
        # Check flights
        cur.execute("SELECT COUNT(*) FROM flights")
        flight_count = cur.fetchone()[0]
        print(f"✈️  Flights: {flight_count}")
        
        # Check flights on LHR→CDG route
        cur.execute("""
            SELECT COUNT(*) 
            FROM flights f
            JOIN routes r ON f.route_id = r.id
            JOIN airports oa ON r.origin_airport_id = oa.id
            JOIN airports da ON r.destination_airport_id = da.id
            WHERE oa.id = 6 AND da.id = 7
        """)
        lhr_cdg_flights = cur.fetchone()[0]
        print(f"🎯 LHR→CDG flights: {lhr_cdg_flights}")
        
        if lhr_cdg_flights == 0:
            print("⚠️  No flights exist on LHR→CDG route. Creating some...")
            create_sample_flights()
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def create_sample_flights():
    """Create sample flights on the LHR→CDG route"""
    conn = connect_db()
    cur = conn.cursor()
    
    try:
        # Get the LHR→CDG route
        cur.execute("""
            SELECT r.id
            FROM routes r
            JOIN airports oa ON r.origin_airport_id = oa.id
            JOIN airports da ON r.destination_airport_id = da.id
            WHERE oa.id = 6 AND da.id = 7
            LIMIT 1
        """)
        
        route = cur.fetchone()
        if not route:
            print("❌ No LHR→CDG route found!")
            return
            
        route_id = route[0]
        
        # Get airline and aircraft
        cur.execute("SELECT id FROM airlines LIMIT 1")
        airline_id = cur.fetchone()[0]
        
        cur.execute("SELECT id FROM aircraft WHERE status = 'active' LIMIT 1")
        aircraft_id = cur.fetchone()[0]
        
        # Create flights for next few days
        flights_created = 0
        for days_ahead in range(0, 7):  # Next 7 days
            flight_date = datetime.now() + timedelta(days=days_ahead)
            
            # Create 2-3 flights per day
            for flight_num in range(1, 4):
                departure_time = flight_date.replace(
                    hour=random.randint(6, 22), 
                    minute=random.choice([0, 15, 30, 45]),
                    second=0, 
                    microsecond=0
                )
                arrival_time = departure_time + timedelta(hours=2, minutes=30)  # ~2.5 hour flight
                
                cur.execute("""
                    INSERT INTO flights (
                        flight_number, airline_id, aircraft_id, route_id,
                        scheduled_departure, scheduled_arrival, status, 
                        gate, terminal
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    f"JH{random.randint(1000, 9999)}",
                    airline_id,
                    aircraft_id,
                    route_id,
                    departure_time,
                    arrival_time,
                    'scheduled',
                    f"A{random.randint(1, 20)}",
                    'A'
                ))
                
                flights_created += 1
        
        conn.commit()
        print(f"✅ Created {flights_created} sample flights on LHR→CDG route")
        
    except Exception as e:
        print(f"❌ Error creating sample flights: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def main():
    """Main function to fix route issues"""
    print("🚀 Starting route database fix...")
    
    # Step 1: Check what's missing
    airports, need_lhr_cdg, need_cdg_lhr = check_missing_routes()
    
    # Step 2: Create missing routes
    if need_lhr_cdg or need_cdg_lhr:
        print("\n📝 Creating missing routes...")
        success = create_missing_routes()
        if not success:
            print("❌ Failed to create routes")
            return
    else:
        print("✅ All major routes already exist")
    
    # Step 3: Verify we have flights
    verify_flight_search_data()
    
    print("\n🎉 Route fix completed! You should now be able to search LHR→CDG flights.")
    print("\n🧪 Test your flight search again with:")
    print("   Origin: London (or LHR)")
    print("   Destination: Paris (or CDG)")
    print("   Date: Today or tomorrow")

if __name__ == "__main__":
    main()