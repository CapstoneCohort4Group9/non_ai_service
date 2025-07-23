-- ============================================================================
-- Additional Demo Bookings for Cancellation Testing
-- Creates 5 more bookings (DEMO03-DEMO07) with different scenarios
-- ============================================================================

BEGIN;

DO $$
DECLARE
    demo_passenger_id INTEGER;
    airline_id INTEGER;
    aircraft_id INTEGER;
    lhr_cdg_route_id INTEGER;
    lhr_mad_route_id INTEGER;
    ord_mad_route_id INTEGER;
    cdg_lhr_route_id INTEGER;
    mad_lhr_route_id INTEGER;
    booking_id INTEGER;
    flight_id INTEGER;
    
BEGIN
    RAISE NOTICE '🎬 Creating additional demo bookings for cancellation testing...';
    
    -- Get required references
    SELECT id INTO demo_passenger_id FROM passengers WHERE email = 'demo.traveler@hopjetair.com';
    SELECT id INTO airline_id FROM airlines WHERE iata_code = 'JH' LIMIT 1;
    SELECT id INTO aircraft_id FROM aircraft WHERE status = 'active' LIMIT 1;
    
    -- Get route IDs
    SELECT r.id INTO lhr_cdg_route_id FROM routes r
    JOIN airports oa ON r.origin_airport_id = oa.id
    JOIN airports da ON r.destination_airport_id = da.id
    WHERE oa.iata_code = 'LHR' AND da.iata_code = 'CDG';
    
    SELECT r.id INTO cdg_lhr_route_id FROM routes r
    JOIN airports oa ON r.origin_airport_id = oa.id
    JOIN airports da ON r.destination_airport_id = da.id
    WHERE oa.iata_code = 'CDG' AND da.iata_code = 'LHR';
    
    SELECT r.id INTO lhr_mad_route_id FROM routes r
    JOIN airports oa ON r.origin_airport_id = oa.id
    JOIN airports da ON r.destination_airport_id = da.id
    WHERE oa.iata_code = 'LHR' AND da.iata_code = 'MAD';
    
    SELECT r.id INTO mad_lhr_route_id FROM routes r
    JOIN airports oa ON r.origin_airport_id = oa.id
    JOIN airports da ON r.destination_airport_id = da.id
    WHERE oa.iata_code = 'MAD' AND da.iata_code = 'LHR';
    
    SELECT r.id INTO ord_mad_route_id FROM routes r
    JOIN airports oa ON r.origin_airport_id = oa.id
    JOIN airports da ON r.destination_airport_id = da.id
    WHERE oa.iata_code = 'ORD' AND da.iata_code = 'MAD';
    
    -- ========================================================================
    -- DEMO03: High Value Booking - Business Class (July 30)
    -- ========================================================================
    RAISE NOTICE '💼 Creating DEMO03: High value business class booking...';
    
    INSERT INTO bookings (
        booking_reference, passenger_id, booking_date, total_amount,
        currency, status, booking_source, trip_type
    ) VALUES (
        'DEMO03', demo_passenger_id, CURRENT_TIMESTAMP, 1250.00,
        'USD', 'confirmed', 'website', 'one-way'
    ) RETURNING id INTO booking_id;
    
    -- Create flight for DEMO03 (LHR → MAD, July 30)
    INSERT INTO flights (
        flight_number, airline_id, aircraft_id, route_id,
        scheduled_departure, scheduled_arrival, actual_departure, actual_arrival,
        status, gate, terminal
    ) VALUES (
        'DEMO503', airline_id, aircraft_id, lhr_mad_route_id,
        '2025-07-30 14:00:00', '2025-07-30 17:30:00', NULL, NULL,
        'scheduled', 'B20', 'B'
    ) RETURNING id INTO flight_id;
    
    -- Create booking segment for DEMO03
    INSERT INTO booking_segments (
        booking_id, flight_id, passenger_id, class_of_service,
        fare_basis, ticket_number, seat_number, baggage_allowance_kg,
        meal_preference, check_in_status, boarding_pass_issued
    ) VALUES (
        booking_id, flight_id, demo_passenger_id, 'business',
        'C1', 'JH' || LPAD(booking_id::TEXT, 10, '0'), '3A', 32,
        'vegetarian', 'not_checked_in', FALSE
    );
    
    RAISE NOTICE '✅ Created DEMO03: Business class LHR→MAD, $1,250, July 30';
    
    -- ========================================================================
    -- DEMO04: Round-trip Booking (July 29 outbound, Aug 5 return)
    -- ========================================================================
    RAISE NOTICE '🔄 Creating DEMO04: Round-trip booking...';
    
    INSERT INTO bookings (
        booking_reference, passenger_id, booking_date, total_amount,
        currency, status, booking_source, trip_type
    ) VALUES (
        'DEMO04', demo_passenger_id, CURRENT_TIMESTAMP, 680.00,
        'USD', 'confirmed', 'mobile', 'round-trip'
    ) RETURNING id INTO booking_id;
    
    -- Outbound flight (CDG → LHR, July 29)
    INSERT INTO flights (
        flight_number, airline_id, aircraft_id, route_id,
        scheduled_departure, scheduled_arrival, actual_departure, actual_arrival,
        status, gate, terminal
    ) VALUES (
        'DEMO504', airline_id, aircraft_id, cdg_lhr_route_id,
        '2025-07-29 16:00:00', '2025-07-29 17:30:00', NULL, NULL,
        'scheduled', 'A25', 'A'
    ) RETURNING id INTO flight_id;
    
    -- Outbound segment
    INSERT INTO booking_segments (
        booking_id, flight_id, passenger_id, class_of_service,
        fare_basis, ticket_number, seat_number, baggage_allowance_kg,
        meal_preference, check_in_status, boarding_pass_issued
    ) VALUES (
        booking_id, flight_id, demo_passenger_id, 'economy',
        'Y2', 'JH' || LPAD(booking_id::TEXT, 10, '0'), '12F', 23,
        'standard', 'not_checked_in', FALSE
    );
    
    -- Return flight (LHR → CDG, Aug 5)
    INSERT INTO flights (
        flight_number, airline_id, aircraft_id, route_id,
        scheduled_departure, scheduled_arrival, actual_departure, actual_arrival,
        status, gate, terminal
    ) VALUES (
        'DEMO505', airline_id, aircraft_id, lhr_cdg_route_id,
        '2025-08-05 10:00:00', '2025-08-05 12:30:00', NULL, NULL,
        'scheduled', 'A30', 'A'
    ) RETURNING id INTO flight_id;
    
    -- Return segment
    INSERT INTO booking_segments (
        booking_id, flight_id, passenger_id, class_of_service,
        fare_basis, ticket_number, seat_number, baggage_allowance_kg,
        meal_preference, check_in_status, boarding_pass_issued
    ) VALUES (
        booking_id, flight_id, demo_passenger_id, 'economy',
        'Y2', 'JH' || LPAD(booking_id::TEXT, 10, '0'), '12F', 23,
        'standard', 'not_checked_in', FALSE
    );
    
    RAISE NOTICE '✅ Created DEMO04: Round-trip CDG↔LHR, $680, July 29 & Aug 5';
    
    -- ========================================================================
    -- DEMO05: International Long-haul (ORD → MAD, August 1)
    -- ========================================================================
    RAISE NOTICE '🌍 Creating DEMO05: International long-haul booking...';
    
    INSERT INTO bookings (
        booking_reference, passenger_id, booking_date, total_amount,
        currency, status, booking_source, trip_type
    ) VALUES (
        'DEMO05', demo_passenger_id, CURRENT_TIMESTAMP, 950.00,
        'USD', 'confirmed', 'agent', 'one-way'
    ) RETURNING id INTO booking_id;
    
    -- Flight ORD → MAD, August 1
    INSERT INTO flights (
        flight_number, airline_id, aircraft_id, route_id,
        scheduled_departure, scheduled_arrival, actual_departure, actual_arrival,
        status, gate, terminal
    ) VALUES (
        'DEMO506', airline_id, aircraft_id, ord_mad_route_id,
        '2025-08-01 18:00:00', '2025-08-02 12:00:00', NULL, NULL,
        'scheduled', 'C25', 'C'
    ) RETURNING id INTO flight_id;
    
    -- Booking segment
    INSERT INTO booking_segments (
        booking_id, flight_id, passenger_id, class_of_service,
        fare_basis, ticket_number, seat_number, baggage_allowance_kg,
        meal_preference, check_in_status, boarding_pass_issued
    ) VALUES (
        booking_id, flight_id, demo_passenger_id, 'premium_economy',
        'W1', 'JH' || LPAD(booking_id::TEXT, 10, '0'), '18C', 32,
        'kosher', 'not_checked_in', FALSE
    );
    
    RAISE NOTICE '✅ Created DEMO05: Premium Economy ORD→MAD, $950, August 1';
    
    -- ========================================================================
    -- DEMO06: Near-departure Booking (July 27 - Same week as demo)
    -- ========================================================================
    RAISE NOTICE '⏰ Creating DEMO06: Near-departure booking (high cancellation fee)...';
    
    INSERT INTO bookings (
        booking_reference, passenger_id, booking_date, total_amount,
        currency, status, booking_source, trip_type
    ) VALUES (
        'DEMO06', demo_passenger_id, CURRENT_TIMESTAMP, 320.00,
        'USD', 'confirmed', 'website', 'one-way'
    ) RETURNING id INTO booking_id;
    
    -- Flight LHR → CDG, July 27 (day after demo)
    INSERT INTO flights (
        flight_number, airline_id, aircraft_id, route_id,
        scheduled_departure, scheduled_arrival, actual_departure, actual_arrival,
        status, gate, terminal
    ) VALUES (
        'DEMO507', airline_id, aircraft_id, lhr_cdg_route_id,
        '2025-07-27 07:00:00', '2025-07-27 09:30:00', NULL, NULL,
        'scheduled', 'A35', 'A'
    ) RETURNING id INTO flight_id;
    
    -- Booking segment
    INSERT INTO booking_segments (
        booking_id, flight_id, passenger_id, class_of_service,
        fare_basis, ticket_number, seat_number, baggage_allowance_kg,
        meal_preference, check_in_status, boarding_pass_issued
    ) VALUES (
        booking_id, flight_id, demo_passenger_id, 'economy',
        'Y3', 'JH' || LPAD(booking_id::TEXT, 10, '0'), '25B', 23,
        'standard', 'not_checked_in', FALSE
    );
    
    RAISE NOTICE '✅ Created DEMO06: Economy LHR→CDG, $320, July 27 (high fee scenario)';
    
    -- ========================================================================
    -- DEMO07: Premium First Class (August 10)
    -- ========================================================================
    RAISE NOTICE '👑 Creating DEMO07: First class premium booking...';
    
    INSERT INTO bookings (
        booking_reference, passenger_id, booking_date, total_amount,
        currency, status, booking_source, trip_type
    ) VALUES (
        'DEMO07', demo_passenger_id, CURRENT_TIMESTAMP, 2850.00,
        'USD', 'confirmed', 'website', 'one-way'
    ) RETURNING id INTO booking_id;
    
    -- Flight MAD → LHR, August 10
    INSERT INTO flights (
        flight_number, airline_id, aircraft_id, route_id,
        scheduled_departure, scheduled_arrival, actual_departure, actual_arrival,
        status, gate, terminal
    ) VALUES (
        'DEMO508', airline_id, aircraft_id, mad_lhr_route_id,
        '2025-08-10 13:00:00', '2025-08-10 15:30:00', NULL, NULL,
        'scheduled', 'B35', 'B'
    ) RETURNING id INTO flight_id;
    
    -- Booking segment
    INSERT INTO booking_segments (
        booking_id, flight_id, passenger_id, class_of_service,
        fare_basis, ticket_number, seat_number, baggage_allowance_kg,
        meal_preference, check_in_status, boarding_pass_issued
    ) VALUES (
        booking_id, flight_id, demo_passenger_id, 'first',
        'F1', 'JH' || LPAD(booking_id::TEXT, 10, '0'), '1A', 50,
        'gourmet', 'not_checked_in', FALSE
    );
    
    RAISE NOTICE '✅ Created DEMO07: First class MAD→LHR, $2,850, August 10';
    
    -- ========================================================================
    -- Create one ALREADY CANCELLED booking for error demo
    -- ========================================================================
    RAISE NOTICE '❌ Creating DEMO08: Pre-cancelled booking (for error demo)...';
    
    INSERT INTO bookings (
        booking_reference, passenger_id, booking_date, total_amount,
        currency, status, booking_source, trip_type
    ) VALUES (
        'DEMO08', demo_passenger_id, CURRENT_TIMESTAMP, 420.00,
        'USD', 'cancelled', 'website', 'one-way'
    ) RETURNING id INTO booking_id;
    
    -- Flight for already cancelled booking
    INSERT INTO flights (
        flight_number, airline_id, aircraft_id, route_id,
        scheduled_departure, scheduled_arrival, actual_departure, actual_arrival,
        status, gate, terminal
    ) VALUES (
        'DEMO509', airline_id, aircraft_id, lhr_cdg_route_id,
        '2025-07-31 12:00:00', '2025-07-31 14:30:00', NULL, NULL,
        'scheduled', 'A40', 'A'
    ) RETURNING id INTO flight_id;
    
    -- Booking segment for cancelled booking
    INSERT INTO booking_segments (
        booking_id, flight_id, passenger_id, class_of_service,
        fare_basis, ticket_number, seat_number, baggage_allowance_kg,
        meal_preference, check_in_status, boarding_pass_issued
    ) VALUES (
        booking_id, flight_id, demo_passenger_id, 'economy',
        'Y4', 'JH' || LPAD(booking_id::TEXT, 10, '0'), '20A', 23,
        'standard', 'not_checked_in', FALSE
    );
    
    RAISE NOTICE '✅ Created DEMO08: Pre-cancelled booking for error demonstration';
    
    RAISE NOTICE '';
    RAISE NOTICE '🎉 Additional demo bookings created successfully!';
    RAISE NOTICE '';
    RAISE NOTICE '📋 CANCELLATION DEMO SCENARIOS:';
    RAISE NOTICE '  ✅ DEMO01: London→Paris, $450, July 28 (moderate fee ~$100)';
    RAISE NOTICE '  ✅ DEMO02: Chicago→Madrid, $850, July 28 (moderate fee ~$100)';
    RAISE NOTICE '  💼 DEMO03: London→Madrid Business, $1,250, July 30 (moderate fee ~$100)';
    RAISE NOTICE '  🔄 DEMO04: Paris↔London Round-trip, $680, July 29 & Aug 5 (moderate fee ~$100)';
    RAISE NOTICE '  🌍 DEMO05: Chicago→Madrid Premium Economy, $950, August 1 (moderate fee ~$100)';
    RAISE NOTICE '  ⏰ DEMO06: London→Paris, $320, July 27 (HIGH FEE ~$200 - within week)';
    RAISE NOTICE '  👑 DEMO07: Madrid→London First Class, $2,850, August 10 (low fee ~$100)';
    RAISE NOTICE '  ❌ DEMO08: Already cancelled (for error demo)';
    RAISE NOTICE '';
    RAISE NOTICE '🎬 DEMO RECOMMENDATIONS:';
    RAISE NOTICE '  Primary: DEMO01, DEMO03, DEMO05 (different values & classes)';
    RAISE NOTICE '  Advanced: DEMO06 (high fee demo), DEMO08 (error handling)';
    RAISE NOTICE '  Backup: DEMO02, DEMO04, DEMO07';
    
END $$;

-- ============================================================================
-- VERIFICATION - Show all demo bookings with cancellation fee estimates
-- ============================================================================

-- Show all demo bookings with flight details
SELECT 
    b.booking_reference,
    b.total_amount,
    b.currency,
    b.status,
    b.trip_type,
    f.scheduled_departure,
    oa.iata_code || '→' || da.iata_code as route,
    bs.class_of_service,
    CASE 
        WHEN b.status = 'cancelled' THEN 'Already Cancelled'
        WHEN EXTRACT(EPOCH FROM (f.scheduled_departure - CURRENT_TIMESTAMP))/86400 < 1 THEN 'Same Day (50% fee)'
        WHEN EXTRACT(EPOCH FROM (f.scheduled_departure - CURRENT_TIMESTAMP))/86400 < 7 THEN 'Within Week ($200 fee)'
        WHEN EXTRACT(EPOCH FROM (f.scheduled_departure - CURRENT_TIMESTAMP))/86400 < 30 THEN 'Within Month ($100 fee)'
        ELSE 'Advance (No fee)'
    END as estimated_cancellation_policy
FROM bookings b
JOIN booking_segments bs ON b.id = bs.booking_id
JOIN flights f ON bs.flight_id = f.id
JOIN routes r ON f.route_id = r.id
JOIN airports oa ON r.origin_airport_id = oa.id
JOIN airports da ON r.destination_airport_id = da.id
WHERE b.booking_reference LIKE 'DEMO%'
ORDER BY b.booking_reference;

COMMIT;