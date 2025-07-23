-- 1. First, check if ORD (Chicago) and MAD (Madrid) airports exist
SELECT iata_code, name, city FROM airports WHERE iata_code IN ('ORD', 'MAD');

-- 2. If Madrid doesn't exist, add it
INSERT INTO airports (iata_code, icao_code, name, city, country, timezone, latitude, longitude)
VALUES ('MAD', 'LEMD', 'Adolfo Suárez Madrid–Barajas Airport', 'Madrid', 'Spain', 'Europe/Madrid', 40.4719, -3.5626);

-- 3. Create Chicago → Madrid route (if it doesn't exist)
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes)
SELECT 
    (SELECT id FROM airports WHERE iata_code = 'ORD'),
    (SELECT id FROM airports WHERE iata_code = 'MAD'),
    6659,  -- Approximate distance
    480    -- 8 hours flight time
WHERE NOT EXISTS (
    SELECT 1 FROM routes r
    JOIN airports oa ON r.origin_airport_id = oa.id
    JOIN airports da ON r.destination_airport_id = da.id
    WHERE oa.iata_code = 'ORD' AND da.iata_code = 'MAD'
);

-- 4. Create return route Madrid → Chicago
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes)
SELECT 
    (SELECT id FROM airports WHERE iata_code = 'MAD'),
    (SELECT id FROM airports WHERE iata_code = 'ORD'),
    6659,
    480
WHERE NOT EXISTS (
    SELECT 1 FROM routes r
    JOIN airports oa ON r.origin_airport_id = oa.id
    JOIN airports da ON r.destination_airport_id = da.id
    WHERE oa.iata_code = 'MAD' AND da.iata_code = 'ORD'
);

-- 5. Create demo flights for July 27, 2025 (ORD → MAD)
INSERT INTO flights (flight_number, airline_id, aircraft_id, route_id, scheduled_departure, scheduled_arrival, status, gate, terminal)
SELECT 
    'JH1847',
    (SELECT id FROM airlines WHERE iata_code = 'JH' LIMIT 1),
    (SELECT id FROM aircraft WHERE status = 'active' LIMIT 1),
    (SELECT r.id FROM routes r 
     JOIN airports oa ON r.origin_airport_id = oa.id 
     JOIN airports da ON r.destination_airport_id = da.id 
     WHERE oa.iata_code = 'ORD' AND da.iata_code = 'MAD'),
    '2025-07-27 09:00:00',
    '2025-07-27 23:00:00',  -- 8 hour flight + time difference
    'scheduled',
    'B12',
    'B';

-- 6. Create return flight for July 29, 2025 (MAD → ORD)
INSERT INTO flights (flight_number, airline_id, aircraft_id, route_id, scheduled_departure, scheduled_arrival, status, gate, terminal)
SELECT 
    'JH1848',
    (SELECT id FROM airlines WHERE iata_code = 'JH' LIMIT 1),
    (SELECT id FROM aircraft WHERE status = 'active' LIMIT 1),
    (SELECT r.id FROM routes r 
     JOIN airports oa ON r.origin_airport_id = oa.id 
     JOIN airports da ON r.destination_airport_id = da.id 
     WHERE oa.iata_code = 'MAD' AND da.iata_code = 'ORD'),
    '2025-07-29 11:00:00',
    '2025-07-29 17:00:00',  -- Arrives same day due to time zones
    'scheduled',
    'A15',
    'A';