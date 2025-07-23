-- !! WARNING: This script will permanently delete all data from these tables. !!
-- !! Please ensure you have a full backup of your database before proceeding. !!

-- Start a transaction for safety, though TRUNCATE's behavior with transactions
-- can vary by database (e.g., PostgreSQL supports transactional TRUNCATE).
BEGIN;

-- Disable foreign key checks temporarily if your database supports it
-- (e.g., SET session_replication_role = 'replica'; for PostgreSQL,
-- or SET FOREIGN_KEY_CHECKS = 0; for MySQL).
-- Use with caution, and re-enable them afterwards!

-- Purge records from tables, starting with those that might be referenced by others,
-- or tables that have foreign keys pointing to them.
-- Adjust the order based on your actual foreign key dependencies.

TRUNCATE TABLE public.trip_packages RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.trip_bookings RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.seat_maps RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.routes RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.refunds RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.passengers RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.langchain_pg_embedding RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.langchain_pg_collection RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.insurance_policies RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.flights RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.flight_status_updates RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.flight_seats RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.flight_schedules RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.excursions RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.excursion_bookings RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.customer_service_logs RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.bookings RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.booking_segments RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.baggage RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.airports RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.airlines RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.airline_policies RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.aircraft_types RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.aircraft RESTART IDENTITY CASCADE; -- This is the parent 'aircraft' table

-- Re-enable foreign key checks if you disabled them.
-- (e.g., SET session_replication_role = 'origin'; for PostgreSQL,
-- or SET FOREIGN_KEY_CHECKS = 1; for MySQL).

COMMIT;

-- After running this script, all tables listed will be empty, and
-- auto-incrementing primary keys will be reset.