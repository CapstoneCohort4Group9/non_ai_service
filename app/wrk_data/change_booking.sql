-- ============================================================================
-- HopJetAir COMPLETE Demo Data Setup - Transactional Script
-- Demo Date: Saturday, July 26, 2025
-- Purpose: Create ALL required data for demo (routes, bookings, flights)
-- ============================================================================

BEGIN;

-- Set the transaction to rollback on any error


DO $$
DECLARE
    demo_passenger_id INTEGER;
    demo_booking_id INTEGER;
    demo_booking2_id INTEGER;
    lhr_airport_id INTEGER;
    cdg_airport_id INTEGER;
    mad_airport_id INTEGER;
    ord_airport_id INTEGER;
    lhr_cdg_route_id INTEGER;
    lhr_mad_route_id INTEGER;
    ord_mad_route_id INTEGER;
    airline_id INTEGER;
    aircraft_id INTEGER;
    demo_flight_id INTEGER;
    segment_count INTEGER;
    
BEGIN
    RAISE NOTICE '🚀 Starting COMPLETE HopJetAir Demo Data Setup...';
    
    -- ========================================================================
    -- STEP 1: ENSURE REQUIRED AIRPORTS EXIST
    -- ========================================================================
    RAISE NOTICE '🏢 Checking required airports...';
    
    -- Get airport IDs
    SELECT id INTO lhr_airport_id FROM airports WHERE iata_code = 'LHR';
    SELECT id INTO cdg_airport_id FROM airports WHERE iata_code = 'CDG';
    SELECT id INTO mad_airport_id FROM airports WHERE iata_code = 'MAD';
    SELECT id INTO ord_airport_id FROM airports WHERE iata_code = 'ORD';
    
    -- Create Madrid airport if it doesn't exist
    IF mad_airport_id IS NULL THEN
        INSERT INTO airports (iata_code, icao_code, name, city, country, timezone, latitude, longitude)
        VALUES ('MAD', 'LEMD', 'Adolfo Suárez Madrid–Barajas Airport', 'Madrid', 'Spain', 'Europe/Madrid', 40.4719, -3.5626)
        RETURNING id INTO mad_airport_id;
        RAISE NOTICE '✅ Created Madrid airport with ID: %', mad_airport_id;
    END IF;
    
    -- Verify all required airports exist
    IF lhr_airport_id IS NULL THEN
        RAISE EXCEPTION 'London Heathrow (LHR) airport not found! Run the original data generator first.';
    END IF;
    IF cdg_airport_id IS NULL THEN
        RAISE EXCEPTION 'Charles de Gaulle (CDG) airport not found! Run the original data generator first.';
    END IF;
    IF ord_airport_id IS NULL THEN
        RAISE EXCEPTION 'Chicago O''Hare (ORD) airport not found! Run the original data generator first.';
    END IF;
    
    RAISE NOTICE '✅ All required airports found - LHR: %, CDG: %, MAD: %, ORD: %', 
                 lhr_airport_id, cdg_airport_id, mad_airport_id, ord_airport_id;
    
    -- ========================================================================
    -- STEP 2: CREATE REQUIRED ROUTES
    -- ========================================================================
    RAISE NOTICE '🛣️  Creating required routes...';
    
    -- Create LHR → CDG route if it doesn't exist
    SELECT id INTO lhr_cdg_route_id FROM routes 
    WHERE origin_airport_id = lhr_airport_id AND destination_airport_id = cdg_airport_id;
    
    IF lhr_cdg_route_id IS NULL THEN
        INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes)
        VALUES (lhr_airport_id, cdg_airport_id, 344, 90)
        RETURNING id INTO lhr_cdg_route_id;
        RAISE NOTICE '✅ Created LHR→CDG route with ID: %', lhr_cdg_route_id;
    ELSE
        RAISE NOTICE '✅ Found existing LHR→CDG route with ID: %', lhr_cdg_route_id;
    END IF;
    
    -- Create CDG → LHR route (return)
    IF NOT EXISTS (SELECT 1 FROM routes WHERE origin_airport_id = cdg_airport_id AND destination_airport_id = lhr_airport_id) THEN
        INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes)
        VALUES (cdg_airport_id, lhr_airport_id, 344, 90);
        RAISE NOTICE '✅ Created CDG→LHR return route';
    END IF;
    
    -- Create LHR → MAD route if it doesn't exist
    SELECT id INTO lhr_mad_route_id FROM routes 
    WHERE origin_airport_id = lhr_airport_id AND destination_airport_id = mad_airport_id;
    
    IF lhr_mad_route_id IS NULL THEN
        INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes)
        VALUES (lhr_airport_id, mad_airport_id, 1264, 150)
        RETURNING id INTO lhr_mad_route_id;
        RAISE NOTICE '✅ Created LHR→MAD route with ID: %', lhr_mad_route_id;
    ELSE
        RAISE NOTICE '✅ Found existing LHR→MAD route with ID: %', lhr_mad_route_id;
    END IF;
    
    -- Create MAD → LHR route (return)
    IF NOT EXISTS (SELECT 1 FROM routes WHERE origin_airport_id = mad_airport_id AND destination_airport_id = lhr_airport_id) THEN
        INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes)
        VALUES (mad_airport_id, lhr_airport_id, 1264, 150);
        RAISE NOTICE '✅ Created MAD→LHR return route';
    END IF;
    
    -- Create ORD → MAD route if it doesn't exist
    SELECT id INTO ord_mad_route_id FROM routes 
    WHERE origin_airport_id = ord_airport_id AND destination_airport_id = mad_airport_id;
    
    IF ord_mad_route_id IS NULL THEN
        INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes)
        VALUES (ord_airport_id, mad_airport_id, 6659, 480)
        RETURNING id INTO ord_mad_route_id;
        RAISE NOTICE '✅ Created ORD→MAD route with ID: %', ord_mad_route_id;
    ELSE
        RAISE NOTICE '✅ Found existing ORD→MAD route with ID: %', ord_mad_route_id;
    END IF;
    
    -- Create MAD → ORD route (return)
    IF NOT EXISTS (SELECT 1 FROM routes WHERE origin_airport_id = mad_airport_id AND destination_airport_id = ord_airport_id) THEN
        INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes)
        VALUES (mad_airport_id, ord_airport_id, 6659, 480);
        RAISE NOTICE '✅ Created MAD→ORD return route';
    END IF;
    
    -- ========================================================================
    -- STEP 3: CREATE DEMO PASSENGER
    -- ========================================================================
    RAISE NOTICE '👤 Creating demo passenger...';
    
    -- Check if demo passenger already exists
    SELECT id INTO demo_passenger_id 
    FROM passengers 
    WHERE email = 'demo.traveler@hopjetair.com';
    
    IF demo_passenger_id IS NULL THEN
        INSERT INTO passengers (
            first_name, last_name, email, phone, date_of_birth, 
            nationality, passport_number, passport_expiry, tier_status
        ) VALUES (
            'Demo', 'Traveler', 'demo.traveler@hopjetair.com', '+1-555-0200', 
            '1985-01-01', 'US', 'P123456789', '2030-01-01', 'gold'
        ) RETURNING id INTO demo_passenger_id;
        
        RAISE NOTICE '✅ Created new demo passenger with ID: %', demo_passenger_id;
    ELSE
        RAISE NOTICE '✅ Found existing demo passenger with ID: %', demo_passenger_id;
    END IF;
    
    -- ========================================================================
    -- STEP 4: GET REQUIRED REFERENCES
    -- ========================================================================
    RAISE NOTICE '🔍 Getting airline and aircraft references...';
    
    -- Get HopJetAir airline ID
    SELECT id INTO airline_id FROM airlines WHERE iata_code = 'JH' LIMIT 1;
    IF airline_id IS NULL THEN
        RAISE EXCEPTION 'HopJetAir airline not found! Run the original data generator first.';
    END IF;
    
    -- Get an active aircraft
    SELECT id INTO aircraft_id FROM aircraft WHERE status = 'active' LIMIT 1;
    IF aircraft_id IS NULL THEN
        RAISE EXCEPTION 'No active aircraft found! Run the original data generator first.';
    END IF;
    
    RAISE NOTICE '✅ Using airline_id: %, aircraft_id: %', airline_id, aircraft_id;
    
    -- ========================================================================
    -- STEP 5: CREATE DEMO BOOKINGS
    -- ========================================================================
    RAISE NOTICE '📋 Creating demo bookings...';
    
    -- Delete existing demo bookings (for clean re-runs)
    DELETE FROM booking_segments WHERE booking_id IN (
        SELECT id FROM bookings WHERE booking_reference IN ('DEMO01', 'DEMO02', 'DEMO03')
    );
    DELETE FROM bookings WHERE booking_reference IN ('DEMO01', 'DEMO02', 'DEMO03');
    
    -- Create DEMO01 booking (London → Paris, July 28)
    INSERT INTO bookings (
        booking_reference, passenger_id, booking_date, total_amount, 
        currency, status, booking_source, trip_type
    ) VALUES (
        'DEMO01', demo_passenger_id, CURRENT_TIMESTAMP, 450.00,
        'USD', 'confirmed', 'website', 'one-way'
    ) RETURNING id INTO demo_booking_id;
    
    RAISE NOTICE '✅ Created booking DEMO01 with ID: %', demo_booking_id;
    
    -- Create DEMO02 booking (Chicago → Madrid, July 28) - for book_flight demo
    INSERT INTO bookings (
        booking_reference, passenger_id, booking_date, total_amount,
        currency, status, booking_source, trip_type
    ) VALUES (
        'DEMO02', demo_passenger_id, CURRENT_TIMESTAMP, 850.00,
        'USD', 'confirmed', 'website', 'round-trip'
    ) RETURNING id INTO demo_booking2_id;
    
    RAISE NOTICE '✅ Created booking DEMO02 with ID: %', demo_booking2_id;
    
    -- ========================================================================
    -- STEP 6: CREATE ORIGINAL FLIGHTS (July 28, 2025)
    -- ========================================================================
    RAISE NOTICE '✈️  Creating original flights for July 28, 2025...';
    
    -- Delete existing demo flights to avoid conflicts
    DELETE FROM booking_segments WHERE flight_id IN (
        SELECT id FROM flights WHERE flight_number LIKE 'DEMO%'
    );
    DELETE FROM flights WHERE flight_number LIKE 'DEMO%';
    
    -- Create original LHR → CDG flight for July 28
    INSERT INTO flights (
        flight_number, airline_id, aircraft_id, route_id,
        scheduled_departure, scheduled_arrival, actual_departure, actual_arrival,
        status, gate, terminal
    ) VALUES (
        'DEMO101', airline_id, aircraft_id, lhr_cdg_route_id,
        '2025-07-28 09:00:00', '2025-07-28 11:30:00', NULL, NULL,
        'scheduled', 'A10', 'A'
    ) RETURNING id INTO demo_flight_id;
    
    RAISE NOTICE '✅ Created original flight DEMO101 (LHR→CDG) with ID: %', demo_flight_id;
    
    -- Create booking segment for DEMO01
    INSERT INTO booking_segments (
        booking_id, flight_id, passenger_id, class_of_service,
        fare_basis, ticket_number, seat_number, baggage_allowance_kg,
        meal_preference, check_in_status, boarding_pass_issued
    ) VALUES (
        demo_booking_id, demo_flight_id, demo_passenger_id, 'economy',
        'Y1', 'JH' || LPAD(demo_booking_id::TEXT, 10, '0'), '15A', 23,
        'standard', 'not_checked_in', FALSE
    );
    
    RAISE NOTICE '✅ Created booking segment for DEMO01';
    
    -- ========================================================================
    -- STEP 7: CREATE ALTERNATIVE FLIGHTS (For change demo)
    -- ========================================================================
    RAISE NOTICE '🔄 Creating alternative flights for change demo...';
    
    -- Create LHR → CDG flights for July 29, 30, 31 (date change options)
    INSERT INTO flights (
        flight_number, airline_id, aircraft_id, route_id,
        scheduled_departure, scheduled_arrival, actual_departure, actual_arrival,
        status, gate, terminal
    ) VALUES 
    -- July 29 options
    ('DEMO201', airline_id, aircraft_id, lhr_cdg_route_id,
     '2025-07-29 08:00:00', '2025-07-29 10:30:00', NULL, NULL,
     'scheduled', 'A11', 'A'),
    ('DEMO202', airline_id, aircraft_id, lhr_cdg_route_id,
     '2025-07-29 14:00:00', '2025-07-29 16:30:00', NULL, NULL,
     'scheduled', 'A12', 'A'),
    ('DEMO203', airline_id, aircraft_id, lhr_cdg_route_id,
     '2025-07-29 18:00:00', '2025-07-29 20:30:00', NULL, NULL,
     'scheduled', 'A13', 'A'),
    -- July 30 options
    ('DEMO204', airline_id, aircraft_id, lhr_cdg_route_id,
     '2025-07-30 09:00:00', '2025-07-30 11:30:00', NULL, NULL,
     'scheduled', 'A14', 'A'),
    ('DEMO205', airline_id, aircraft_id, lhr_cdg_route_id,
     '2025-07-30 15:00:00', '2025-07-30 17:30:00', NULL, NULL,
     'scheduled', 'A15', 'A'),
    -- July 31 options
    ('DEMO206', airline_id, aircraft_id, lhr_cdg_route_id,
     '2025-07-31 10:00:00', '2025-07-31 12:30:00', NULL, NULL,
     'scheduled', 'A16', 'A');
    
    RAISE NOTICE '✅ Created 6 alternative flights for date changes (July 29-31)';
    
    -- Create LHR → MAD flights (destination change options)
    INSERT INTO flights (
        flight_number, airline_id, aircraft_id, route_id,
        scheduled_departure, scheduled_arrival, actual_departure, actual_arrival,
        status, gate, terminal
    ) VALUES 
    ('DEMO301', airline_id, aircraft_id, lhr_mad_route_id,
     '2025-07-28 10:00:00', '2025-07-28 13:30:00', NULL, NULL,
     'scheduled', 'B10', 'B'),
    ('DEMO302', airline_id, aircraft_id, lhr_mad_route_id,
     '2025-07-29 11:00:00', '2025-07-29 14:30:00', NULL, NULL,
     'scheduled', 'B11', 'B');
    
    RAISE NOTICE '✅ Created 2 alternative flights for destination changes (LHR→MAD)';
    
    -- ========================================================================
    -- STEP 8: CREATE CHICAGO → MADRID FLIGHTS (For book_flight demo)
    -- ========================================================================
    RAISE NOTICE '🌍 Creating Chicago → Madrid flights for book_flight demo...';
    
    INSERT INTO flights (
        flight_number, airline_id, aircraft_id, route_id,
        scheduled_departure, scheduled_arrival, actual_departure, actual_arrival,
        status, gate, terminal
    ) VALUES 
    ('DEMO401', airline_id, aircraft_id, ord_mad_route_id,
     '2025-07-27 15:00:00', '2025-07-28 09:00:00', NULL, NULL,
     'scheduled', 'C15', 'C'),
    ('DEMO402', airline_id, aircraft_id, ord_mad_route_id,
     '2025-07-28 16:00:00', '2025-07-29 10:00:00', NULL, NULL,
     'scheduled', 'C16', 'C');
    
    RAISE NOTICE '✅ Created Chicago → Madrid flights for book_flight demo';
    
    -- ========================================================================
    -- STEP 9: VERIFICATION
    -- ========================================================================
    RAISE NOTICE '🔍 Verifying demo data...';
    
    -- Verify routes
    IF lhr_cdg_route_id IS NULL OR lhr_mad_route_id IS NULL OR ord_mad_route_id IS NULL THEN
        RAISE EXCEPTION 'Required routes were not created properly!';
    END IF;
    
    -- Verify bookings
    PERFORM id FROM bookings WHERE booking_reference IN ('DEMO01', 'DEMO02');
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Demo bookings were not created properly!';
    END IF;
    
    -- Verify flights
    PERFORM id FROM flights WHERE flight_number LIKE 'DEMO%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Demo flights were not created properly!';
    END IF;
    
    -- Verify booking segments
    SELECT COUNT(*) INTO segment_count FROM booking_segments bs 
    JOIN bookings b ON bs.booking_id = b.id 
    WHERE b.booking_reference = 'DEMO01';
    
    IF segment_count = 0 THEN
        RAISE EXCEPTION 'Booking segments were not created properly!';
    END IF;
    
    RAISE NOTICE '✅ All verifications passed!';
    
    RAISE NOTICE '🎉 COMPLETE Demo data setup finished successfully!';
    RAISE NOTICE '';
    RAISE NOTICE '🛣️  ROUTES CREATED:';
    RAISE NOTICE '  - LHR ↔ CDG (London ↔ Paris)';
    RAISE NOTICE '  - LHR ↔ MAD (London ↔ Madrid)';
    RAISE NOTICE '  - ORD ↔ MAD (Chicago ↔ Madrid)';
    RAISE NOTICE '';
    RAISE NOTICE '📋 DEMO BOOKINGS CREATED:';
    RAISE NOTICE '  - DEMO01: London → Paris, July 28, 2025 (for change_flight demo)';
    RAISE NOTICE '  - DEMO02: Chicago → Madrid, July 28, 2025 (for book_flight demo)';
    RAISE NOTICE '';
    RAISE NOTICE '✈️  FLIGHTS CREATED:';
    RAISE NOTICE '  - DEMO101: Original LHR→CDG flight (July 28)';
    RAISE NOTICE '  - DEMO201-206: Alternative LHR→CDG flights (July 29-31)';
    RAISE NOTICE '  - DEMO301-302: Alternative LHR→MAD flights (destination change)';
    RAISE NOTICE '  - DEMO401-402: ORD→MAD flights (book_flight demo)';
    RAISE NOTICE '';
    RAISE NOTICE '🎬 READY FOR DEMO!';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 USE THESE FOR YOUR DEMO:';
    RAISE NOTICE '  Change Flight: {"booking_reference": "DEMO01", "new_departure_date": "2025-07-29"}';
    RAISE NOTICE '  Book Flight: {"origin": "Chicago", "destination": "Madrid", "departure_date": "2025-07-27", "contact": "demo.traveler@hopjetair.com"}';
    
END $$;

-- ============================================================================
-- VERIFICATION QUERIES (Run these to confirm setup)
-- ============================================================================

-- Check demo routes
SELECT 
    r.id,
    oa.iata_code || ' (' || oa.city || ')' as origin,
    da.iata_code || ' (' || da.city || ')' as destination,
    r.distance_km || ' km' as distance,
    r.flight_duration_minutes || ' min' as duration
FROM routes r
JOIN airports oa ON r.origin_airport_id = oa.id
JOIN airports da ON r.destination_airport_id = da.id
WHERE (oa.iata_code = 'LHR' AND da.iata_code IN ('CDG', 'MAD'))
   OR (oa.iata_code = 'ORD' AND da.iata_code = 'MAD')
   OR (oa.iata_code IN ('CDG', 'MAD') AND da.iata_code = 'LHR')
   OR (oa.iata_code = 'MAD' AND da.iata_code = 'ORD')
ORDER BY oa.iata_code, da.iata_code;

-- Check demo bookings
SELECT 
    booking_reference,
    total_amount,
    currency,
    status,
    trip_type,
    p.first_name || ' ' || p.last_name as passenger_name
FROM bookings b
JOIN passengers p ON b.passenger_id = p.id
WHERE booking_reference LIKE 'DEMO%'
ORDER BY booking_reference;

-- Check demo flights with routes
SELECT 
    f.flight_number,
    f.scheduled_departure,
    f.scheduled_arrival,
    f.status,
    oa.iata_code || ' (' || oa.city || ')' as origin,
    da.iata_code || ' (' || da.city || ')' as destination,
    f.gate,
    f.terminal
FROM flights f
JOIN routes r ON f.route_id = r.id
JOIN airports oa ON r.origin_airport_id = oa.id
JOIN airports da ON r.destination_airport_id = da.id
WHERE f.flight_number LIKE 'DEMO%'
ORDER BY f.flight_number;

-- Check booking segments
SELECT 
    b.booking_reference,
    f.flight_number,
    bs.class_of_service,
    bs.seat_number,
    bs.check_in_status,
    p.first_name || ' ' || p.last_name as passenger_name
FROM booking_segments bs
JOIN bookings b ON bs.booking_id = b.id
JOIN flights f ON bs.flight_id = f.id
JOIN passengers p ON bs.passenger_id = p.id
WHERE b.booking_reference LIKE 'DEMO%'
ORDER BY b.booking_reference;

-- ============================================================================
-- COMMIT (Script will commit automatically if all succeeds)
-- ============================================================================
COMMIT;