-- HopJetAir Sample Data Inserts

-- Airlines
INSERT INTO airlines (iata_code, icao_code, name, country, alliance, created_at) VALUES ('AA', 'AAL', 'American Airlines', 'United States', 'oneworld', '2023-07-19 18:58:27');
INSERT INTO airlines (iata_code, icao_code, name, country, alliance, created_at) VALUES ('DL', 'DAL', 'Delta Air Lines', 'United States', 'SkyTeam', '2024-12-13 06:08:37');
INSERT INTO airlines (iata_code, icao_code, name, country, alliance, created_at) VALUES ('UA', 'UAL', 'United Airlines', 'United States', 'Star Alliance', '2025-03-14 17:34:37');
INSERT INTO airlines (iata_code, icao_code, name, country, alliance, created_at) VALUES ('LH', 'DLH', 'Lufthansa', 'Germany', 'Star Alliance', '2024-03-11 00:54:32');
INSERT INTO airlines (iata_code, icao_code, name, country, alliance, created_at) VALUES ('BA', 'BAW', 'British Airways', 'United Kingdom', 'oneworld', '2024-11-17 16:00:47');
INSERT INTO airlines (iata_code, icao_code, name, country, alliance, created_at) VALUES ('AF', 'AFR', 'Air France', 'France', 'SkyTeam', '2025-02-06 07:32:12');
INSERT INTO airlines (iata_code, icao_code, name, country, alliance, created_at) VALUES ('KL', 'KLM', 'KLM Royal Dutch Airlines', 'Netherlands', 'SkyTeam', '2023-12-04 20:28:47');
INSERT INTO airlines (iata_code, icao_code, name, country, alliance, created_at) VALUES ('EK', 'UAE', 'Emirates', 'United Arab Emirates', NULL, '2025-01-23 23:18:20');
INSERT INTO airlines (iata_code, icao_code, name, country, alliance, created_at) VALUES ('QR', 'QTR', 'Qatar Airways', 'Qatar', 'oneworld', '2024-12-23 23:23:00');
INSERT INTO airlines (iata_code, icao_code, name, country, alliance, created_at) VALUES ('SQ', 'SIA', 'Singapore Airlines', 'Singapore', 'Star Alliance', '2023-08-12 00:17:17');
INSERT INTO airlines (iata_code, icao_code, name, country, alliance, created_at) VALUES ('HJ', 'HJA', 'HopJetAir', 'United States', 'Star Alliance', '2024-04-08 11:10:22');

-- Aircraft Types
INSERT INTO aircraft_types (manufacturer, model, iata_code, icao_code, seats_economy, seats_premium_economy, seats_business, seats_first, total_seats, range_km, created_at) VALUES ('Boeing', '737-800', '738', 'B738', 162, 12, 0, 0, 174, 5765, '2020-10-30 10:20:46');
INSERT INTO aircraft_types (manufacturer, model, iata_code, icao_code, seats_economy, seats_premium_economy, seats_business, seats_first, total_seats, range_km, created_at) VALUES ('Boeing', '777-300ER', '77W', 'B77W', 296, 24, 42, 8, 370, 11135, '2020-10-24 17:40:31');
INSERT INTO aircraft_types (manufacturer, model, iata_code, icao_code, seats_economy, seats_premium_economy, seats_business, seats_first, total_seats, range_km, created_at) VALUES ('Airbus', 'A320-200', '320', 'A320', 150, 12, 0, 0, 162, 6150, '2022-12-09 17:23:10');
INSERT INTO aircraft_types (manufacturer, model, iata_code, icao_code, seats_economy, seats_premium_economy, seats_business, seats_first, total_seats, range_km, created_at) VALUES ('Airbus', 'A350-900', '359', 'A359', 253, 21, 42, 0, 316, 15000, '2023-04-14 13:51:53');
INSERT INTO aircraft_types (manufacturer, model, iata_code, icao_code, seats_economy, seats_premium_economy, seats_business, seats_first, total_seats, range_km, created_at) VALUES ('Boeing', '787-9', '789', 'B789', 234, 21, 28, 0, 283, 14140, '2023-07-21 23:39:06');
INSERT INTO aircraft_types (manufacturer, model, iata_code, icao_code, seats_economy, seats_premium_economy, seats_business, seats_first, total_seats, range_km, created_at) VALUES ('Airbus', 'A330-300', '333', 'A333', 277, 21, 36, 0, 334, 11750, '2020-12-15 19:15:22');

-- Airports
INSERT INTO airports (iata_code, icao_code, name, city, country, timezone, latitude, longitude, created_at) VALUES ('JFK', 'KJFK', 'John F. Kennedy International Airport', 'New York', 'United States', 'America/New_York', 40.6413, -73.7781, '2019-06-12 00:56:58');
INSERT INTO airports (iata_code, icao_code, name, city, country, timezone, latitude, longitude, created_at) VALUES ('LAX', 'KLAX', 'Los Angeles International Airport', 'Los Angeles', 'United States', 'America/Los_Angeles', 33.9425, -118.4081, '2020-11-10 06:03:47');
INSERT INTO airports (iata_code, icao_code, name, city, country, timezone, latitude, longitude, created_at) VALUES ('LHR', 'EGLL', 'London Heathrow Airport', 'London', 'United Kingdom', 'Europe/London', 51.47, -0.4543, '2024-05-24 08:40:39');
INSERT INTO airports (iata_code, icao_code, name, city, country, timezone, latitude, longitude, created_at) VALUES ('CDG', 'LFPG', 'Charles de Gaulle Airport', 'Paris', 'France', 'Europe/Paris', 49.0097, 2.5479, '2018-12-03 17:10:18');
INSERT INTO airports (iata_code, icao_code, name, city, country, timezone, latitude, longitude, created_at) VALUES ('FRA', 'EDDF', 'Frankfurt Airport', 'Frankfurt', 'Germany', 'Europe/Berlin', 50.0379, 8.5622, '2023-09-27 18:39:40');
INSERT INTO airports (iata_code, icao_code, name, city, country, timezone, latitude, longitude, created_at) VALUES ('NRT', 'RJAA', 'Narita International Airport', 'Tokyo', 'Japan', 'Asia/Tokyo', 35.7647, 140.3864, '2022-01-12 08:40:16');
INSERT INTO airports (iata_code, icao_code, name, city, country, timezone, latitude, longitude, created_at) VALUES ('SIN', 'WSSS', 'Singapore Changi Airport', 'Singapore', 'Singapore', 'Asia/Singapore', 1.3644, 103.9915, '2022-06-04 09:48:41');
INSERT INTO airports (iata_code, icao_code, name, city, country, timezone, latitude, longitude, created_at) VALUES ('DXB', 'OMDB', 'Dubai International Airport', 'Dubai', 'United Arab Emirates', 'Asia/Dubai', 25.2532, 55.3657, '2016-11-25 11:06:39');
INSERT INTO airports (iata_code, icao_code, name, city, country, timezone, latitude, longitude, created_at) VALUES ('SYD', 'YSSY', 'Sydney Kingsford Smith Airport', 'Sydney', 'Australia', 'Australia/Sydney', -33.9399, 151.1753, '2019-11-20 18:13:35');
INSERT INTO airports (iata_code, icao_code, name, city, country, timezone, latitude, longitude, created_at) VALUES ('ORD', 'KORD', 'Chicago O''Hare International Airport', 'Chicago', 'United States', 'America/Chicago', 41.9742, -87.9073, '2016-09-01 15:49:16');

-- Aircraft
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('VH-6Z3', 5, 1, 'retired', '2022-04-18', '2024-07-27 14:06:40');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('N637BD', 1, 7, 'active', '2017-07-18', '2020-02-23 21:19:03');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('VH-WAA', 1, 2, 'maintenance', '2017-06-07', '2016-10-14 06:11:21');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('D-QKZQ', 6, 6, 'active', '2022-03-03', '2021-05-02 14:20:47');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('9V-IH7', 6, 2, 'active', '2024-11-15', '2024-06-07 21:32:06');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('A6-9NH', 1, 11, 'retired', '2019-08-30', '2017-01-23 09:54:48');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('VH-I7V', 5, 9, 'retired', '2020-10-15', '2022-01-21 13:44:48');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('A6-T0S', 1, 2, 'maintenance', '2016-05-09', '2022-08-11 22:13:37');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('VH-2FO', 2, 7, 'retired', '2017-09-16', '2023-05-08 02:23:24');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('9V-K30', 1, 9, 'maintenance', '2017-11-08', '2021-07-22 02:31:44');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('JA0JA', 2, 11, 'retired', '2016-05-23', '2019-08-03 00:46:37');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('G-EYPW', 4, 5, 'active', '2024-02-27', '2016-11-30 17:48:41');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('G-RFVB', 3, 3, 'retired', '2024-09-07', '2020-10-05 11:40:00');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('F-MHTW', 4, 8, 'retired', '2018-01-12', '2018-08-02 08:10:38');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('F-GXGQ', 5, 2, 'retired', '2017-12-23', '2017-10-13 20:00:59');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('JAEQ9', 2, 1, 'retired', '2022-02-22', '2018-02-22 03:43:34');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('F-BCLB', 6, 11, 'maintenance', '2024-11-14', '2017-04-06 21:43:48');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('D-IMSO', 4, 4, 'retired', '2020-08-19', '2021-01-27 15:48:51');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('F-BHEH', 2, 5, 'retired', '2023-01-23', '2019-08-01 22:06:31');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('A6-R1U', 1, 9, 'active', '2023-02-16', '2019-01-20 08:07:27');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('N893UZ', 4, 10, 'maintenance', '2017-04-20', '2018-05-08 17:59:37');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('9V-5XU', 3, 10, 'active', '2024-02-03', '2015-12-26 10:00:19');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('9V-SRL', 3, 3, 'active', '2018-05-26', '2024-02-12 01:57:58');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('JAK9W', 3, 8, 'maintenance', '2022-03-17', '2020-10-05 10:34:33');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('VH-XIJ', 4, 2, 'retired', '2022-11-29', '2025-06-20 00:42:39');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('VH-S4M', 1, 7, 'retired', '2019-08-04', '2025-04-13 08:08:28');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('N544EI', 3, 11, 'maintenance', '2023-05-21', '2023-02-15 16:35:35');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('D-PVWE', 2, 1, 'active', '2021-11-22', '2021-12-12 20:30:19');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('9V-86B', 4, 3, 'retired', '2021-08-13', '2021-05-04 16:17:04');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('F-BJPG', 3, 3, 'retired', '2025-02-22', '2019-07-17 12:51:42');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('JA56I', 4, 4, 'retired', '2015-11-09', '2018-10-23 20:07:58');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('JABWJ', 3, 4, 'retired', '2024-08-30', '2020-11-22 08:39:16');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('G-WAMN', 4, 3, 'maintenance', '2024-08-30', '2019-04-25 14:55:43');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('F-PLJY', 2, 1, 'maintenance', '2018-02-13', '2025-02-06 10:06:26');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('JAH89', 2, 11, 'maintenance', '2023-02-12', '2019-07-09 01:56:25');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('N949OP', 1, 4, 'active', '2017-11-14', '2019-07-09 08:22:27');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('VH-DD3', 3, 11, 'retired', '2024-11-08', '2025-02-03 02:10:48');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('F-LNFE', 1, 4, 'retired', '2015-11-19', '2017-03-26 19:07:43');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('VH-TR0', 2, 5, 'maintenance', '2016-07-27', '2018-06-08 11:02:07');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('9V-G4F', 4, 9, 'maintenance', '2019-04-15', '2016-03-27 23:32:05');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('JA6DO', 3, 4, 'active', '2020-11-11', '2022-02-02 02:28:15');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('9V-53M', 6, 1, 'retired', '2021-07-12', '2018-07-25 02:02:15');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('VH-JTR', 2, 5, 'maintenance', '2020-04-24', '2022-02-14 02:39:21');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('F-CQOK', 1, 6, 'retired', '2015-09-14', '2025-07-07 12:29:41');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('G-QIEJ', 6, 10, 'active', '2024-11-01', '2021-06-16 19:29:43');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('VH-V1I', 5, 4, 'maintenance', '2025-07-08', '2019-01-02 12:50:55');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('D-VOGL', 5, 11, 'active', '2018-09-27', '2022-10-22 23:11:30');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('F-NRKO', 4, 11, 'active', '2024-01-28', '2016-05-16 03:38:37');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('D-CIPZ', 2, 8, 'maintenance', '2020-11-19', '2019-11-12 05:04:15');
INSERT INTO aircraft (registration, aircraft_type_id, airline_id, status, delivery_date, created_at) VALUES ('F-AOIA', 5, 9, 'maintenance', '2019-09-22', '2020-01-22 15:17:36');

-- Routes
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (7, 3, 17094, 1244, '2025-03-30 15:36:41');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (2, 3, 14985, 1082, '2024-08-23 17:27:41');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (9, 4, 25641, 1832, '2025-03-09 03:53:54');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (8, 1, 15984, 1162, '2025-06-18 11:43:07');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (2, 9, 37407, 2669, '2023-10-09 14:43:08');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (6, 5, 16206, 1180, '2024-02-05 16:28:21');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (9, 5, 25086, 1805, '2023-12-01 00:31:18');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (3, 2, 14985, 1085, '2025-04-14 10:55:16');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (10, 6, 25974, 1872, '2025-02-18 00:53:12');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (3, 8, 9102, 679, '2024-12-26 14:55:35');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (8, 5, 7881, 577, '2023-12-14 01:17:59');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (2, 4, 15096, 1094, '2024-03-28 02:01:18');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (9, 7, 9102, 676, '2023-11-14 17:44:26');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (10, 9, 34854, 2485, '2025-06-27 15:04:28');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (4, 3, 555, 64, '2025-02-18 06:12:50');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (3, 7, 17094, 1241, '2023-10-09 06:20:25');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (7, 1, 24087, 1729, '2025-04-10 13:36:48');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (4, 5, 777, 103, '2023-09-16 19:15:39');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (1, 5, 10101, 755, '2025-05-29 03:42:01');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (2, 6, 28860, 2085, '2024-03-02 12:00:25');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (6, 9, 8880, 659, '2025-02-04 14:34:34');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (4, 6, 16761, 1205, '2024-06-14 20:42:33');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (1, 7, 24087, 1723, '2023-12-31 19:14:33');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (8, 10, 17649, 1289, '2025-06-16 07:38:40');
INSERT INTO routes (origin_airport_id, destination_airport_id, distance_km, flight_duration_minutes, created_at) VALUES (1, 9, 33189, 2373, '2024-07-23 10:06:48');

-- Passengers
INSERT INTO passengers (first_name, last_name, email, phone, date_of_birth, nationality, passport_number, passport_expiry, frequent_flyer_number, tier_status, created_at) VALUES ('Elliot', 'Lucas', 'daniloaraujo@example.org', '(0141) 4960238', '1967-11-22', 'South Korea', 'X26412357', '2027-10-16', NULL, 'basic', '2023-08-09 20:07:37');
INSERT INTO passengers (first_name, last_name, email, phone, date_of_birth, nationality, passport_number, passport_expiry, frequent_flyer_number, tier_status, created_at) VALUES ('Astrid', 'Vieira', 'paulo16@example.com', '+7 (651) 510-1224', '1967-03-03', 'Netherlands', '963822762', '2033-03-19', NULL, 'basic', '2024-08-27 15:05:35');
INSERT INTO passengers (first_name, last_name, email, phone, date_of_birth, nationality, passport_number, passport_expiry, frequent_flyer_number, tier_status, created_at) VALUES ('Antony', 'Jacobs', 'kopilovsavva@example.org', '317-422-2086', '1984-03-21', 'Brazil', '457128197', '2030-03-19', NULL, 'basic', '2024-09-23 09:11:46');
INSERT INTO passengers (first_name, last_name, email, phone, date_of_birth, nationality, passport_number, passport_expiry, frequent_flyer_number, tier_status, created_at) VALUES ('Fortunato', 'Heidrich', 'carrillotimothy@example.com', '+55 (061) 7907 7019', '1960-08-09', 'Australia', '086024837', '2032-12-03', 'HJ98160591', 'silver', '2024-02-02 06:49:52');
