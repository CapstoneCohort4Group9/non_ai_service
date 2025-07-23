import psycopg2
import random
from datetime import datetime, timedelta
import logging

# Database connection
DB_URL = "postgresql://hopjetair:SecurePass123!@hopjetair-postgres.cepc0wqo22hd.us-east-1.rds.amazonaws.com:5432/hopjetairline_db"
#DB_URL = "postgresql://hopjetair:SecurePass123!@localhost:5432/hopjetairline_db"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_db():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(DB_URL)

def fix_booking_segments_relationships(conn):
    """Fix booking segments to ensure proper passenger-booking-flight relationships"""
    cur = conn.cursor()
    
    logger.info("🔧 Fixing booking segments relationships...")
    
    try:
        # First, get all booking segments with their current relationships
        cur.execute("""
            SELECT bs.id, bs.booking_id, bs.flight_id, bs.passenger_id, 
                   b.passenger_id as booking_passenger_id
            FROM booking_segments bs
            JOIN bookings b ON bs.booking_id = b.id
            WHERE bs.passenger_id != b.passenger_id
        """)
        
        mismatched_segments = cur.fetchall()
        logger.info(f"Found {len(mismatched_segments)} booking segments with passenger mismatches")
        
        # Fix passenger mismatches in booking segments
        for segment_id, booking_id, flight_id, segment_passenger_id, booking_passenger_id in mismatched_segments:
            cur.execute("""
                UPDATE booking_segments 
                SET passenger_id = %s 
                WHERE id = %s
            """, (booking_passenger_id, segment_id))
        
        logger.info(f"✅ Fixed {len(mismatched_segments)} passenger mismatches in booking segments")
        
        # Now fix flight seats to match booking segments
        cur.execute("""
            UPDATE flight_seats fs
            SET passenger_id = bs.passenger_id
            FROM booking_segments bs
            WHERE fs.booking_segment_id = bs.id 
            AND fs.passenger_id != bs.passenger_id
        """)
        
        affected_seats = cur.rowcount
        logger.info(f"✅ Fixed {affected_seats} flight seat passenger assignments")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error fixing booking segments: {e}")
        conn.rollback()
        raise

def fix_aircraft_flight_relationships(conn):
    """Ensure aircraft assigned to flights are from the correct airline"""
    cur = conn.cursor()
    
    logger.info("🔧 Fixing aircraft-flight-airline relationships...")
    
    try:
        # Find flights where aircraft doesn't belong to the flight's airline
        cur.execute("""
            SELECT f.id, f.airline_id, f.aircraft_id, a.airline_id as aircraft_airline_id
            FROM flights f
            JOIN aircraft a ON f.aircraft_id = a.id
            WHERE f.airline_id != a.airline_id
        """)
        
        mismatched_flights = cur.fetchall()
        logger.info(f"Found {len(mismatched_flights)} flights with airline-aircraft mismatches")
        
        # For each mismatched flight, assign a correct aircraft
        for flight_id, flight_airline_id, current_aircraft_id, aircraft_airline_id in mismatched_flights:
            # Find a suitable aircraft from the correct airline
            cur.execute("""
                SELECT id FROM aircraft 
                WHERE airline_id = %s AND status = 'active'
                ORDER BY RANDOM() 
                LIMIT 1
            """, (flight_airline_id,))
            
            correct_aircraft = cur.fetchone()
            if correct_aircraft:
                cur.execute("""
                    UPDATE flights 
                    SET aircraft_id = %s 
                    WHERE id = %s
                """, (correct_aircraft[0], flight_id))
            else:
                # If no aircraft available for this airline, create one
                cur.execute("""
                    SELECT id FROM aircraft_types ORDER BY RANDOM() LIMIT 1
                """)
                aircraft_type_id = cur.fetchone()[0]
                
                # Generate a unique registration
                registration = f"N{random.randint(100, 999)}JH"
                cur.execute("""
                    INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date)
                    VALUES (%s, %s, %s, 'active', CURRENT_DATE)
                    RETURNING id
                """, (registration, aircraft_type_id, flight_airline_id))
                
                new_aircraft_id = cur.fetchone()[0]
                
                cur.execute("""
                    UPDATE flights 
                    SET aircraft_id = %s 
                    WHERE id = %s
                """, (new_aircraft_id, flight_id))
        
        logger.info(f"✅ Fixed {len(mismatched_flights)} aircraft-airline mismatches")
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error fixing aircraft relationships: {e}")
        conn.rollback()
        raise

def fix_flight_seats_relationships(conn):
    """Fix flight seats to match aircraft seat maps"""
    cur = conn.cursor()
    
    logger.info("🔧 Fixing flight seats to match aircraft configurations...")
    
    try:
        # Delete flight seats that don't match the aircraft's seat map
        cur.execute("""
            DELETE FROM flight_seats fs
            WHERE NOT EXISTS (
                SELECT 1 FROM seat_maps sm
                JOIN flights f ON f.aircraft_id IN (
                    SELECT id FROM aircraft WHERE aircraft_type_id = sm.aircraft_type_id
                )
                WHERE f.id = fs.flight_id 
                AND sm.seat_number = fs.seat_number
            )
        """)
        
        deleted_invalid_seats = cur.rowcount
        logger.info(f"✅ Removed {deleted_invalid_seats} invalid flight seats")
        
        # Add missing flight seats for flights that don't have complete seat maps
        cur.execute("""
            INSERT INTO flight_seats (flight_id, seat_number, passenger_id, booking_segment_id, seat_fee, status)
            SELECT DISTINCT f.id, sm.seat_number, NULL::integer, NULL::integer, 0, 'available'
            FROM flights f
            JOIN aircraft a ON f.aircraft_id = a.id
            JOIN seat_maps sm ON a.aircraft_type_id = sm.aircraft_type_id
            WHERE NOT EXISTS (
                SELECT 1 FROM flight_seats fs 
                WHERE fs.flight_id = f.id AND fs.seat_number = sm.seat_number
            )
        """)
        
        added_seats = cur.rowcount
        logger.info(f"✅ Added {added_seats} missing flight seats")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error fixing flight seats: {e}")
        conn.rollback()
        raise

def fix_baggage_relationships(conn):
    """Ensure baggage belongs to valid booking segments"""
    cur = conn.cursor()
    
    logger.info("🔧 Fixing baggage relationships...")
    
    try:
        # Delete baggage records that reference non-existent booking segments
        cur.execute("""
            DELETE FROM baggage 
            WHERE booking_segment_id NOT IN (SELECT id FROM booking_segments)
        """)
        
        deleted_orphaned_baggage = cur.rowcount
        logger.info(f"✅ Removed {deleted_orphaned_baggage} orphaned baggage records")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error fixing baggage relationships: {e}")
        conn.rollback()
        raise

def fix_insurance_relationships(conn):
    """Fix insurance policy relationships"""
    cur = conn.cursor()
    
    logger.info("🔧 Fixing insurance policy relationships...")
    
    try:
        # Ensure insurance passenger matches booking passenger
        cur.execute("""
            UPDATE insurance_policies ip
            SET passenger_id = b.passenger_id
            FROM bookings b
            WHERE ip.booking_id = b.id 
            AND ip.passenger_id != b.passenger_id
        """)
        
        fixed_insurance = cur.rowcount
        logger.info(f"✅ Fixed {fixed_insurance} insurance policy passenger mismatches")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error fixing insurance relationships: {e}")
        conn.rollback()
        raise

def fix_trip_bookings_relationships(conn):
    """Fix trip booking relationships"""
    cur = conn.cursor()
    
    logger.info("🔧 Fixing trip booking relationships...")
    
    try:
        # Ensure excursion bookings reference valid trip bookings
        cur.execute("""
            DELETE FROM excursion_bookings 
            WHERE trip_booking_id NOT IN (SELECT id FROM trip_bookings)
        """)
        
        deleted_orphaned_excursions = cur.rowcount
        logger.info(f"✅ Removed {deleted_orphaned_excursions} orphaned excursion bookings")
        
        # Fix excursion bookings to match destination
        cur.execute("""
            UPDATE excursion_bookings eb
            SET excursion_id = (
                SELECT e.id FROM excursions e
                JOIN trip_bookings tb ON eb.trip_booking_id = tb.id
                JOIN trip_packages tp ON tb.trip_package_id = tp.id
                WHERE e.destination_city = tp.destination_city
                ORDER BY RANDOM() LIMIT 1
            )
            WHERE EXISTS (
                SELECT 1 FROM trip_bookings tb
                JOIN trip_packages tp ON tb.trip_package_id = tp.id
                JOIN excursions e ON eb.excursion_id = e.id
                WHERE eb.trip_booking_id = tb.id
                AND e.destination_city != tp.destination_city
            )
        """)
        
        fixed_destinations = cur.rowcount
        logger.info(f"✅ Fixed {fixed_destinations} excursion destination mismatches")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error fixing trip booking relationships: {e}")
        conn.rollback()
        raise

def fix_refund_relationships(conn):
    """Fix refund relationships"""
    cur = conn.cursor()
    
    logger.info("🔧 Fixing refund relationships...")
    
    try:
        # Delete refunds for non-existent bookings
        cur.execute("""
            DELETE FROM refunds 
            WHERE booking_id NOT IN (SELECT id FROM bookings)
        """)
        
        deleted_orphaned_refunds = cur.rowcount
        logger.info(f"✅ Removed {deleted_orphaned_refunds} orphaned refund records")
        
        # Ensure refund amounts don't exceed booking amounts
        cur.execute("""
            UPDATE refunds r
            SET amount = LEAST(r.amount, b.total_amount)
            FROM bookings b
            WHERE r.booking_id = b.id 
            AND r.amount > b.total_amount
        """)
        
        fixed_amounts = cur.rowcount
        logger.info(f"✅ Fixed {fixed_amounts} refund amounts exceeding booking totals")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error fixing refund relationships: {e}")
        conn.rollback()
        raise

def fix_customer_service_relationships(conn):
    """Fix customer service log relationships"""
    cur = conn.cursor()
    
    logger.info("🔧 Fixing customer service relationships...")
    
    try:
        # Delete customer service logs for non-existent passengers
        cur.execute("""
            DELETE FROM customer_service_logs 
            WHERE passenger_id NOT IN (SELECT id FROM passengers)
        """)
        
        deleted_orphaned_logs = cur.rowcount
        logger.info(f"✅ Removed {deleted_orphaned_logs} orphaned customer service logs")
        
        # Update booking references to actual booking references
        cur.execute("""
            UPDATE customer_service_logs csl
            SET booking_reference = b.booking_reference
            FROM bookings b
            WHERE csl.passenger_id = b.passenger_id
            AND csl.booking_reference NOT IN (SELECT booking_reference FROM bookings)
        """)
        
        fixed_references = cur.rowcount
        logger.info(f"✅ Fixed {fixed_references} invalid booking references in customer service logs")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error fixing customer service relationships: {e}")
        conn.rollback()
        raise

def validate_data_integrity(conn):
    """Validate data integrity after fixes"""
    cur = conn.cursor()
    
    logger.info("🔍 Validating data integrity...")
    
    validation_queries = [
        ("Booking segments with passenger mismatch", """
            SELECT COUNT(*) FROM booking_segments bs
            JOIN bookings b ON bs.booking_id = b.id
            WHERE bs.passenger_id != b.passenger_id
        """),
        ("Flights with wrong airline aircraft", """
            SELECT COUNT(*) FROM flights f
            JOIN aircraft a ON f.aircraft_id = a.id
            WHERE f.airline_id != a.airline_id
        """),
        ("Flight seats without matching seat map", """
            SELECT COUNT(*) FROM flight_seats fs
            WHERE NOT EXISTS (
                SELECT 1 FROM seat_maps sm
                JOIN flights f ON f.aircraft_id IN (
                    SELECT id FROM aircraft WHERE aircraft_type_id = sm.aircraft_type_id
                )
                WHERE f.id = fs.flight_id AND sm.seat_number = fs.seat_number
            )
        """),
        ("Orphaned baggage records", """
            SELECT COUNT(*) FROM baggage 
            WHERE booking_segment_id NOT IN (SELECT id FROM booking_segments)
        """),
        ("Insurance with passenger mismatch", """
            SELECT COUNT(*) FROM insurance_policies ip
            JOIN bookings b ON ip.booking_id = b.id
            WHERE ip.passenger_id != b.passenger_id
        """),
        ("Orphaned excursion bookings", """
            SELECT COUNT(*) FROM excursion_bookings 
            WHERE trip_booking_id NOT IN (SELECT id FROM trip_bookings)
        """),
        ("Orphaned refunds", """
            SELECT COUNT(*) FROM refunds 
            WHERE booking_id NOT IN (SELECT id FROM bookings)
        """),
        ("Orphaned customer service logs", """
            SELECT COUNT(*) FROM customer_service_logs 
            WHERE passenger_id NOT IN (SELECT id FROM passengers)
        """)
    ]
    
    all_good = True
    for description, query in validation_queries:
        cur.execute(query)
        count = cur.fetchone()[0]
        if count > 0:
            logger.warning(f"⚠️  {description}: {count}")
            all_good = False
        else:
            logger.info(f"✅ {description}: 0 (Good)")
    
    if all_good:
        logger.info("🎉 All data integrity checks passed!")
    else:
        logger.warning("⚠️  Some data integrity issues remain")
    
    return all_good

def main():
    """Main function to fix all data integrity issues"""
    logger.info("🚀 Starting HopJetAir database integrity fix...")
    
    conn = connect_db()
    
    try:
        # Run all fixes in order
        fix_booking_segments_relationships(conn)
        fix_aircraft_flight_relationships(conn)
        fix_flight_seats_relationships(conn)
        fix_baggage_relationships(conn)
        fix_insurance_relationships(conn)
        fix_trip_bookings_relationships(conn)
        fix_refund_relationships(conn)
        fix_customer_service_relationships(conn)
        
        # Validate everything is fixed
        is_valid = validate_data_integrity(conn)
        
        if is_valid:
            logger.info("🎉 Database integrity fix completed successfully!")
        else:
            logger.warning("⚠️  Some issues may require manual review")
            
    except Exception as e:
        logger.error(f"❌ Critical error during fix: {e}")
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()