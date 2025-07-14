# HopJetAir Customer Service API

A comprehensive airline customer service system built with FastAPI and PostgreSQL, featuring realistic airline industry data and operations.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip

### Installation

1. **Clone and setup the project:**
```bash
# Run the automated setup script
python setup_script.py
```

2. **Manual installation (alternative):**
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Create database
createdb hopjetair
```

3. **Start the API server:**
```bash
python updated_api_endpoints.py
```

4. **Access the API:**
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- API Base URL: http://localhost:8000

## 📊 Database Schema

The system includes comprehensive airline industry data:

### Core Entities
- **Airlines**: HopJetAir and major carriers
- **Aircraft**: Fleet management with 5 aircraft types
- **Airports**: 16 major international airports
- **Routes**: Flight routes between airports
- **Flights**: Scheduled and actual flight operations
- **Passengers**: Customer data with tier status
- **Bookings**: Reservation management
- **Seats**: Seat maps and assignments

### Advanced Features
- **Trip Packages**: Vacation packages and tours
- **Excursions**: Local activities and experiences
- **Insurance**: Flight and trip protection plans
- **Policies**: Airline rules and fee structures
- **Refunds**: Compensation and refund processing
- **Customer Service**: Interaction logging and escalation

## 🛠 API Endpoints

### Flight Operations
```bash
# Search flights
POST /search_flight
POST /search_flights

# Book flights  
POST /book_flight

# Check status
POST /check_flight_status
POST /check_flight_availability

# Pricing
POST /search_flight_prices
POST /check_flight_prices
```

### Booking Management
```bash
# Booking details
POST /get_booking_details
POST /check_flight_reservation

# Modifications
POST /change_flight
POST /cancel_booking
POST /update_flight_date
```

### Seat Management
```bash
# Seat operations
POST /check_seat_availability
POST /change_seat
POST /choose_seat
```

### Check-in & Boarding
```bash
# Check-in process
POST /check_in_passenger
POST /check_in
POST /check_flight_checkin_status

# Boarding passes
POST /get_boarding_pass
POST /get_boarding_pass_pdf
POST /send_boarding_pass_email
```

### Trip Packages
```bash
# Trip operations
POST /search_trip
POST /book_trip
POST /check_trip_details
POST /change_trip
POST /cancel_trip

# Pricing
POST /check_trip_prices
POST /search_trip_prices
POST /check_trip_offers
```

### Insurance Services
```bash
# Flight insurance
POST /search_flight_insurance
POST /purchase_flight_insurance
POST /check_flight_insurance_coverage

# Trip insurance
POST /search_trip_insurance  
POST /purchase_trip_insurance
POST /check_trip_insurance_coverage
```

### Policies & Fees
```bash
# Policy queries
POST /query_policy_rag_db
POST /check_cancellation_fee
POST /check_baggage_allowance
```

### Customer Service
```bash
# Support
POST /escalate_to_human_agent
POST /schedule_callback

# Refunds
POST /initiate_refund
POST /check_refund_eligibility
POST /get_refund
```

## 📋 Sample Data

The database comes populated with realistic airline industry data:

### Airlines
- **HopJetAir** (Primary carrier)
- American Airlines
- Delta Air Lines  
- United Airlines
- British Airways

### Routes
Popular routes including:
- JFK ↔ LAX (Domestic)
- JFK ↔ LHR (International)
- ORD ↔ MAD (International)
- LAX ↔ NRT (International)

### Aircraft Fleet
- Boeing 737-800 (Domestic)
- Boeing 777-300ER (Long-haul)
- Airbus A320 (Short-haul)
- Airbus A350-900 (Long-haul)
- Boeing 787-9 (Long-haul)

### Trip Packages
- Madrid Cultural Explorer
- Paris Romance Package
- London Heritage Tour
- Tokyo Adventure

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/hopjetair
SYNC_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/hopjetair

# Connection Pool
DB_MIN_CONNECTIONS=5
DB_MAX_CONNECTIONS=20

# Application
DEBUG=True
LOG_LEVEL=INFO
```

### Database Connection Pooling
The system uses `psycopg_pool` for efficient connection management:
- Async connection pooling
- Automatic connection retry
- Health monitoring
- Connection lifecycle management

## 📝 API Examples

### Search Flights
```bash
curl -X POST "http://localhost:8000/search_flight" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "JFK",
    "destination": "LAX", 
    "departure_date": "2025-08-15",
    "passengers": 1,
    "classname": "economy"
  }'
```

### Book Flight
```bash
curl -X POST "http://localhost:8000/book_flight" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "JFK",
    "destination": "LAX",
    "departure_date": "2025-08-15",
    "contact": "passenger@example.com",
    "price": 450,
    "classname": "economy"
  }'
```

### Check Booking
```bash
curl -X POST "http://localhost:8000/get_booking_details" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_reference": "ABC123",
    "passenger_name": "John Doe"
  }'
```

### Check Seat Availability
```bash
curl -X POST "http://localhost:8000/check_seat_availability" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_reference": "ABC123",
    "flight_number": "HJ1234",
    "seat_preference": "aisle"
  }'
```

### Check-in Passenger
```bash
curl -X POST "http://localhost:8000/check_in_passenger" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_reference": "ABC123",
    "last_name": "Doe"
  }'
```

### Search Trip Packages
```bash
curl -X POST "http://localhost:8000/search_trip" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Madrid",
    "budget": 1500,
    "interests": ["history", "culture"],
    "duration_days": 5
  }'
```

### Purchase Insurance
```bash
curl -X POST "http://localhost:8000/purchase_flight_insurance" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Paris",
    "start_date": "2025-08-15",
    "end_date": "2025-08-22",
    "plan": "comprehensive",
    "travelers": 2
  }'
```

## 🏗 Architecture

### Project Structure
```
hopjetair/
├── database_models.py          # SQLAlchemy models
├── database_connection.py      # Connection pooling & management
├── airline_services.py         # Business logic services
├── updated_api_endpoints.py    # FastAPI endpoints
├── data_generator.py          # Database population script
├── setup_script.py           # Automated setup
├── requirements.txt          # Python dependencies
├── .env                     # Environment configuration
└── README.md               # Documentation
```

### Service Layer Architecture
- **FlightService**: Flight search, booking, status
- **BookingService**: Reservation management
- **SeatService**: Seat maps and assignments
- **TripService**: Package tours and excursions
- **PolicyService**: Rules and fee queries
- **InsuranceService**: Coverage and claims
- **CheckInService**: Check-in and boarding passes
- **RefundService**: Refunds and compensation
- **CustomerServiceService**: Support escalation
- **BaggageService**: Allowance and fees
- **PricingService**: Price search and comparison

### Database Design Principles
- **Normalized schema** following airline industry standards
- **Referential integrity** with proper foreign keys
- **Indexing strategy** for performance optimization
- **Audit trails** for booking and transaction history
- **Flexible policies** supporting different fare types and routes

## 🧪 Testing

### Manual Testing
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs

# Interactive testing
open http://localhost:8000/redoc
```

### Database Queries
```sql
-- Check data population
SELECT 
  (SELECT COUNT(*) FROM airlines) as airlines,
  (SELECT COUNT(*) FROM airports) as airports,
  (SELECT COUNT(*) FROM passengers) as passengers,
  (SELECT COUNT(*) FROM bookings) as bookings,
  (SELECT COUNT(*) FROM flights) as flights;

-- Sample booking with passenger info
SELECT 
  b.booking_reference,
  p.first_name || ' ' || p.last_name as passenger_name,
  b.total_amount,
  b.status,
  b.booking_date
FROM bookings b
JOIN passengers p ON b.passenger_id = p.id
LIMIT 5;

-- Flight availability
SELECT 
  f.flight_number,
  ao.iata_code as origin,
  ad.iata_code as destination,
  f.scheduled_departure,
  f.status
FROM flights f
JOIN routes r ON f.route_id = r.id
JOIN airports ao ON r.origin_airport_id = ao.id
JOIN airports ad ON r.destination_airport_id = ad.id
WHERE f.scheduled_departure > NOW()
LIMIT 10;
```

## 🚀 Production Deployment

### Docker Setup
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "updated_api_endpoints:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration
```bash
# Production environment variables
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/hopjetair
DB_MIN_CONNECTIONS=10
DB_MAX_CONNECTIONS=50
DEBUG=False
LOG_LEVEL=WARNING
```

### Database Migration
```bash
# Using Alembic for schema migrations
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 📈 Scaling Considerations

### Performance Optimization
- **Connection pooling** with configurable pool sizes
- **Database indexing** on frequently queried columns
- **Async operations** for non-blocking I/O
- **Caching layer** for frequently accessed data
- **Query optimization** with proper JOIN strategies

### Monitoring
- Health check endpoints for load balancers
- Database connection monitoring
- API response time tracking
- Error rate monitoring
- Resource usage metrics

### Security
- Input validation with Pydantic models
- SQL injection prevention with parameterized queries
- Rate limiting for API endpoints
- Authentication and authorization (ready for implementation)
- Data encryption for sensitive information

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd hopjetair

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest

# Code formatting
black .
flake8 .
```

### Adding New Endpoints
1. Add Pydantic request model
2. Implement business logic in appropriate service
3. Add endpoint in `updated_api_endpoints.py`
4. Update documentation
5. Add tests

### Database Schema Changes
1. Modify models in `database_models.py`
2. Create Alembic migration
3. Update data generator if needed
4. Test with sample data

## 📚 Additional Resources

### Industry Standards
- **IATA standards** for airport and airline codes
- **EDIFACT** messaging for airline reservations
- **NDC (New Distribution Capability)** for modern airline retailing
- **GDPR compliance** for passenger data protection

### Related Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Airline Industry Data Standards](https://www.iata.org/en/publications/)

## 📞 Support

### Troubleshooting
- **Database connection issues**: Check PostgreSQL service and credentials
- **Import errors**: Verify all dependencies are installed
- **Performance issues**: Monitor connection pool and query performance
- **Data consistency**: Check foreign key constraints and data integrity

### Contact
- **Technical Issues**: Create GitHub issue
- **Feature Requests**: Submit feature request
- **Documentation**: Contribute to README improvements

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**HopJetAir Customer Service API** - A comprehensive solution for modern airline customer service operations.
  