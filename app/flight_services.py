from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
import random
import string
from sqlalchemy.orm import joinedload
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from .database_models import *
from .database_connection import DatabaseError, BookingNotFoundError, FlightNotFoundError, PassengerNotFoundError
#done
class FlightSearchService:
    @staticmethod
    async def search_flight(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for available flights"""
        try:
            origin = params.get('origin', 'Chicago')
            destination = params.get('destination', 'Madrid')
            departure_date = params.get('departure_date', params.get('date'))

            # Get airports
            origin_stmt = select(Airport).where(
                or_(Airport.iata_code == origin, Airport.city.ilike(f"%{origin}%"))
            )
            dest_stmt = select(Airport).where(
                or_(Airport.iata_code == destination, Airport.city.ilike(f"%{destination}%"))
            )

            origin_airport = (await db.execute(origin_stmt)).scalars().first()
            dest_airport = (await db.execute(dest_stmt)).scalars().first()
            
            print(f"DEBUG: Origin airport found: {origin_airport.name if origin_airport else 'None'}")
            print(f"DEBUG: Destination airport found: {dest_airport.name if dest_airport else 'None'}")            
            
            print(f"DEBUG: Origin airport id found: {origin_airport.id if origin_airport else 'None'}")
            print(f"DEBUG: Destination airport id found: {dest_airport.id if dest_airport else 'None'}")                   
            
            

            if not origin_airport or not dest_airport:
                return {
                    "status": "error",
                    "message": "Origin or destination airport not found",
                    "flights": []
                }

            # Parse date
            if isinstance(departure_date, str):
                try:
                    search_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
                except:
                    search_date = datetime.now().date()
            else:
                search_date = departure_date

            # Find route
            route_stmt = select(Route).where(
                Route.origin_airport_id == origin_airport.id,
                Route.destination_airport_id == dest_airport.id
            )
            route = (await db.execute(route_stmt)).scalars().first()

            print(f"DEBUG: Route found: {route is not None}")

            if not route:
                return {
                    "status": "success",
                    "message": "No direct flights available",
                    "flights": []
                }

            # Search flights with joinedload to avoid lazy-loading errors
            flight_stmt = (
                select(Flight)
                .options(
                    joinedload(Flight.airline),
                    joinedload(Flight.aircraft).joinedload(Aircraft.aircraft_type),
                    joinedload(Flight.route)
                )
                .where(
                    Flight.route_id == route.id,
                    func.date(Flight.scheduled_departure) == search_date,
                    Flight.status.in_(['scheduled', 'boarding'])
                )
            )
            flights = (await db.execute(flight_stmt)).scalars().all()

            flight_results = []
            for flight in flights:
                # Calculate available seats
                booked_stmt = select(func.count()).where(
                    BookingSegment.flight_id == flight.id
                )
                booked_seats = (await db.execute(booked_stmt)).scalar()

                available_seats = flight.aircraft.aircraft_type.total_seats - booked_seats

                flight_info = {
                    "flight_id": flight.id,
                    "flight_number": flight.flight_number,
                    "airline": flight.airline.name,
                    "aircraft_type": f"{flight.aircraft.aircraft_type.manufacturer} {flight.aircraft.aircraft_type.model}",
                    "departure_time": flight.scheduled_departure.isoformat(),
                    "arrival_time": flight.scheduled_arrival.isoformat(),
                    "duration_minutes": route.flight_duration_minutes,
                    "available_seats": available_seats,
                    "price_economy": float(Decimal(str(random.uniform(200, 800)))),
                    "price_business": float(Decimal(str(random.uniform(800, 2000)))),
                    "status": flight.status,
                    "gate": flight.gate,
                    "terminal": flight.terminal
                }
                flight_results.append(flight_info)

            return {
                "status": "success",
                "origin": {
                    "code": origin_airport.iata_code,
                    "name": origin_airport.name,
                    "city": origin_airport.city
                },
                "destination": {
                    "code": dest_airport.iata_code,
                    "name": dest_airport.name,
                    "city": dest_airport.city
                },
                "date": search_date.isoformat(),
                "flights": flight_results,
                "total_results": len(flight_results)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Flight search failed: {str(e)}",
                "flights": []
            }
    @staticmethod
    async def search_flights(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search flights with advanced filters"""
        try:
            # Similar to search_flight but with more filtering options
            result = await FlightSearchService.search_flight(db, params)
            
            # Add advanced filtering
            if result["status"] == "success" and result["flights"]:
                flights = result["flights"]
                
                # Filter by budget
                max_price = params.get('max_price', params.get('budget', 10000))
                if max_price:
                    flights = [f for f in flights if f["price_economy"] <= max_price]
                
                # Filter by time preference
                preferred_time = params.get('preferred_time', params.get('preferred_departure_time'))
                if preferred_time:
                    if preferred_time.lower() == 'morning':
                        flights = [f for f in flights if 6 <= datetime.fromisoformat(f["departure_time"]).hour <= 11]
                    elif preferred_time.lower() == 'afternoon':
                        flights = [f for f in flights if 12 <= datetime.fromisoformat(f["departure_time"]).hour <= 17]
                    elif preferred_time.lower() == 'evening':
                        flights = [f for f in flights if 18 <= datetime.fromisoformat(f["departure_time"]).hour <= 23]
                
                # Sort by preference
                sort_by = params.get('sort_by', 'price')
                if sort_by == 'price':
                    flights.sort(key=lambda x: x["price_economy"])
                elif sort_by == 'time':
                    flights.sort(key=lambda x: x["departure_time"])
                
                result["flights"] = flights
                result["total_results"] = len(flights)
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Advanced flight search failed: {str(e)}",
                "flights": []
            }

class FlightStatusService:
    @staticmethod
    async def check_flight_status(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check flight status"""
        try:
            flight_number = params.get('flight_number')
            date_str = params.get('date')

            search_date = (
                datetime.strptime(date_str, '%Y-%m-%d').date()
                if date_str else datetime.now().date()
            )

            # Query flight
            stmt = (
                select(Flight)
                .options(
                    joinedload(Flight.route).joinedload(Route.origin_airport),
                    joinedload(Flight.route).joinedload(Route.destination_airport),
                    joinedload(Flight.airline)
                )
                .where(
                    and_(
                        Flight.flight_number == flight_number,
                        func.date(Flight.scheduled_departure) == search_date
                    )
                )
            )
            flight = (await db.execute(stmt)).scalars().first()

            if not flight:
                raise FlightNotFoundError(f"Flight {flight_number} not found for {search_date}")

            # Query latest status update
            update_stmt = (
                select(FlightStatusUpdate)
                .where(FlightStatusUpdate.flight_id == flight.id)
                .order_by(FlightStatusUpdate.update_time.desc())
            )
            latest_update = (await db.execute(update_stmt)).scalars().first()

            route = flight.route
            origin_airport = route.origin_airport
            dest_airport = route.destination_airport

            status_info = {
                "flight_number": flight.flight_number,
                "airline": flight.airline.name,
                "status": flight.status,
                "origin": {
                    "code": origin_airport.iata_code,
                    "name": origin_airport.name,
                    "city": origin_airport.city
                },
                "destination": {
                    "code": dest_airport.iata_code,
                    "name": dest_airport.name,
                    "city": dest_airport.city
                },
                "scheduled_departure": flight.scheduled_departure.isoformat(),
                "scheduled_arrival": flight.scheduled_arrival.isoformat(),
                "gate": flight.gate,
                "terminal": flight.terminal
            }

            if latest_update:
                status_info.update({
                    "actual_departure": latest_update.new_departure_time.isoformat() if latest_update.new_departure_time else None,
                    "actual_arrival": latest_update.new_arrival_time.isoformat() if latest_update.new_arrival_time else None,
                    "delay_minutes": latest_update.delay_minutes,
                    "update_reason": latest_update.reason
                })

            return {
                "status": "success",
                "flight_status": status_info
            }

        except FlightNotFoundError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Status check failed: {str(e)}"
            }
    
    @staticmethod
    async def get_flight_status(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Alternative flight status endpoint"""
        return await FlightStatusService.check_flight_status(db, params)

class FlightAvailabilityService:
    @staticmethod
    async def check_flight_availability(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check flight availability"""
        try:
            origin = params.get('origin', params.get('frm'))
            destination = params.get('destination', params.get('to'))
            date_str = params.get('date')
            class_of_service = params.get('classname', 'economy')
            
            # Use search flight logic
            search_params = {
                'origin': origin,
                'destination': destination,
                'departure_date': date_str
            }
            
            result = await FlightSearchService.search_flight(db, search_params)
            
            if result["status"] == "success":
                # Filter by class availability
                available_flights = []
                for flight in result["flights"]:
                    class_available = True  # Simplified - in real system would check actual seat availability
                    if class_available:
                        flight_info = {
                            "flight_number": flight["flight_number"],
                            "airline": flight["airline"],
                            "departure_time": flight["departure_time"],
                            "arrival_time": flight["arrival_time"],
                            "available_seats": flight["available_seats"],
                            "class_of_service": class_of_service,
                            "price": flight["price_economy"] if class_of_service == "economy" else flight["price_business"]
                        }
                        available_flights.append(flight_info)
                
                return {
                    "status": "success",
                    "availability": {
                        "flights_available": len(available_flights),
                        "class_of_service": class_of_service,
                        "flights": available_flights
                    }
                }
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Availability check failed: {str(e)}"
            }
    
    @staticmethod
    async def query_flight_availability(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query flight availability with time preferences"""
        try:
            origin = params.get('origin')
            destination = params.get('destination')
            date_str = params.get('date')
            time_of_day = params.get('time_of_day', 'any')
            
            search_params = {
                'origin': origin,
                'destination': destination,
                'departure_date': date_str,
                'preferred_time': time_of_day
            }
            
            return await FlightSearchService.search_flights(db, search_params)
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Flight availability query failed: {str(e)}"
            }
    
    @staticmethod
    async def check_flight_availability_and_fare(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check both availability and fare information"""
        try:
            booking_ref = params.get('booking_reference')
            new_date = params.get('new_date')

            # Get current booking
            booking_stmt = select(Booking).where(Booking.booking_reference == booking_ref)
            booking = (await db.execute(booking_stmt)).scalars().first()

            if not booking:
                raise BookingNotFoundError(f"Booking {booking_ref} not found")

            # Get first segment
            segment_stmt = select(BookingSegment).where(BookingSegment.booking_id == booking.id)
            segment = (await db.execute(segment_stmt)).scalars().first()

            if not segment:
                return {"status": "error", "message": "No flight segments found"}

            current_flight = segment.flight
            route = current_flight.route

            # Build search params
            search_params = {
                'origin': route.origin_airport.iata_code,
                'destination': route.destination_airport.iata_code,
                'departure_date': new_date
            }

            # Run availability search
            availability_result = await FlightSearchService.search_flight(db, search_params)

            if availability_result["status"] == "success":
                current_price = float(booking.total_amount)
                for flight in availability_result["flights"]:
                    new_price = flight["price_economy"]
                    price_difference = new_price - current_price

                    flight.update({
                        "current_booking_price": current_price,
                        "price_difference": price_difference,
                        "change_fee": 75.0,
                        "total_cost_change": price_difference + 75.0
                    })

            return availability_result

        except Exception as e:
            return {
                "status": "error",
                "message": f"Availability and fare check failed: {str(e)}"
            }

class FlightBookingService:
    @staticmethod
    async def book_flight(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Book a flight"""
        try:
            # Generate unique booking reference
            booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            while True:
                stmt = select(Booking).where(Booking.booking_reference == booking_ref)
                existing = (await db.execute(stmt)).scalars().first()
                if not existing:
                    break
                booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

            # Find or create passenger
            passenger_email = params.get('contact', 'passenger@example.com')
            passenger_stmt = select(Passenger).where(Passenger.email == passenger_email)
            passenger = (await db.execute(passenger_stmt)).scalars().first()

            # If no matching passenger, pick one at random
            if not passenger:
                passenger = await db.scalar(
                    select(Passenger).order_by(func.random()).limit(1)
                )
                if not passenger:
                    passenger = Passenger(
                        first_name="John",
                        last_name="Doe",
                        email=passenger_email,
                        phone="+1-555-0123"
                    )
                    db.add(passenger)
                    await db.flush()

            # Create booking
            booking = Booking(
                booking_reference=booking_ref,
                passenger_id=passenger.id,
                total_amount=Decimal(str(params.get('price', 950))),
                currency='USD',
                status='confirmed',
                trip_type=params.get('trip_type', 'round-trip')
            )
            db.add(booking)
            await db.flush()

            # Get airports
            origin = params.get('origin', 'Chicago')
            destination = params.get('destination', 'Madrid')

            origin_stmt = select(Airport).where(
                or_(Airport.iata_code == origin, Airport.city.ilike(f"%{origin}%"))
            )
            dest_stmt = select(Airport).where(
                or_(Airport.iata_code == destination, Airport.city.ilike(f"%{destination}%"))
            )

            origin_airport = (await db.execute(origin_stmt)).scalars().first()
            dest_airport = (await db.execute(dest_stmt)).scalars().first()

            if origin_airport and dest_airport:
                route_stmt = select(Route).where(
                    Route.origin_airport_id == origin_airport.id,
                    Route.destination_airport_id == dest_airport.id
                )
                route = (await db.execute(route_stmt)).scalars().first()

                if route:
                    departure_date = params.get('departure_date', '2025-08-10')
                    search_date = datetime.strptime(departure_date, '%Y-%m-%d').date()

                    flight_stmt = select(Flight).where(
                        Flight.route_id == route.id,
                        func.date(Flight.scheduled_departure) == search_date
                    )
                    flight = (await db.execute(flight_stmt)).scalars().first()

                    if flight:
                        segment = BookingSegment(
                            booking_id=booking.id,
                            flight_id=flight.id,
                            passenger_id=passenger.id,
                            class_of_service=params.get('classname', 'economy'),
                            ticket_number=''.join(random.choices(string.digits, k=10)),
                            baggage_allowance_kg=23
                        )
                        db.add(segment)

            await db.commit()

            return {
                "status": "success",
                "booking_reference": booking_ref,
                "passenger_name": f"{passenger.first_name} {passenger.last_name}",
                "total_amount": float(booking.total_amount),
                "confirmation_message": f"Flight booked successfully. Booking reference: {booking_ref}",
                "booking_details": {
                    "origin": params.get('origin'),
                    "destination": params.get('destination'),
                    "departure_date": params.get('departure_date'),
                    "class": params.get('classname', 'economy'),
                    "passengers": params.get('passengers', 1)
                }
            }

        except Exception as e:
            await db.rollback()
            return {
                "status": "error",
                "message": f"Booking failed: {str(e)}"
            }

class FlightChangeService:
    @staticmethod
    async def change_flight(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Change flight booking"""
        try:
            booking_ref = params.get('booking_reference', params.get('confirmation_number'))
            new_date = params.get('new_departure_date', params.get('new_date', params.get('new_flight_date')))
            new_destination = params.get('new_destination')

            # Get current booking
            booking_stmt = select(Booking).where(Booking.booking_reference == booking_ref)
            booking = (await db.execute(booking_stmt)).scalars().first()

            if not booking:
                raise BookingNotFoundError(f"Booking {booking_ref} not found")

            # Get current flight segment with joined flight + route + airports
            segment_stmt = (
                select(BookingSegment)
                .options(
                    joinedload(BookingSegment.flight)
                    .joinedload(Flight.route)
                    .joinedload(Route.origin_airport),
                    joinedload(BookingSegment.flight)
                    .joinedload(Flight.route)
                    .joinedload(Route.destination_airport)
                )
                .where(BookingSegment.booking_id == booking.id)
            )
            segment = (await db.execute(segment_stmt)).scalars().first()

            if not segment or not segment.flight:
                return {"status": "error", "message": "No flight segments found"}

            current_flight = segment.flight
            route = current_flight.route

            # Calculate change fee
            change_fee = Decimal('75') if route.distance_km <= 2000 else Decimal('200')
            if (current_flight.scheduled_departure - datetime.now()).days < 1:
                change_fee *= Decimal('2')

            changes_made = []
            new_flights = []

            # Handle date change
            if new_date:
                try:
                    search_date = datetime.strptime(new_date, '%Y-%m-%d').date()
                    flights_stmt = (
                        select(Flight)
                        .where(
                            Flight.route_id == current_flight.route_id,
                            func.date(Flight.scheduled_departure) == search_date,
                            Flight.status == 'scheduled'
                        )
                    )
                    new_flights = (await db.execute(flights_stmt)).scalars().all()
                    if new_flights:
                        changes_made.append(f"Date changed to {new_date}")
                except Exception:
                    return {"status": "error", "message": "Invalid date format"}

            # Handle destination change
            if new_destination:
                dest_stmt = select(Airport).where(
                    or_(
                        Airport.iata_code == new_destination,
                        Airport.city.ilike(f"%{new_destination}%")
                    )
                )
                dest_airport = (await db.execute(dest_stmt)).scalars().first()

                if dest_airport:
                    new_route_stmt = select(Route).where(
                        Route.origin_airport_id == route.origin_airport_id,
                        Route.destination_airport_id == dest_airport.id
                    )
                    new_route = (await db.execute(new_route_stmt)).scalars().first()
                    if new_route:
                        changes_made.append(f"Destination changed to {dest_airport.city}")
                        change_fee += Decimal('100')

            return {
                "status": "success",
                "booking_reference": booking_ref,
                "current_flight": {
                    "flight_number": current_flight.flight_number,
                    "departure": current_flight.scheduled_departure.isoformat(),
                    "route": f"{route.origin_airport.iata_code} → {route.destination_airport.iata_code}"
                },
                "requested_changes": changes_made,
                "change_fee": float(change_fee),
                "new_flight_options": [
                    {
                        "flight_number": f.flight_number,
                        "departure": f.scheduled_departure.isoformat(),
                        "available_seats": 25,
                        "price_difference": random.randint(-100, 200)
                    } for f in new_flights[:3]
                ] if new_flights else [],
                "policy": {
                    "changes_allowed": True,
                    "same_day_change_fee": float(change_fee * 2),
                    "advance_change_fee": float(change_fee),
                    "restrictions": "Changes must be made at least 2 hours before departure"
                }
            }

        except BookingNotFoundError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Flight change failed: {str(e)}"}
    
    @staticmethod
    async def confirm_flight_change(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Confirm flight change"""
        try:
            booking_ref = params.get('booking_reference')
            new_departure_date = params.get('new_departure_date')

            # Get current booking
            booking_stmt = select(Booking).where(Booking.booking_reference == booking_ref)
            booking = (await db.execute(booking_stmt)).scalars().first()

            if not booking:
                raise BookingNotFoundError(f"Booking {booking_ref} not found")

            # Get flight segment
            segment_stmt = select(BookingSegment).where(BookingSegment.booking_id == booking.id)
            segment = (await db.execute(segment_stmt)).scalars().first()

            if segment:
                # Update booking total with change fee
                change_fee = Decimal('75')
                booking.total_amount += change_fee

                await db.commit()

                return {
                    "status": "success",
                    "booking_reference": booking_ref,
                    "confirmation_message": "Flight change confirmed successfully",
                    "new_departure_date": new_departure_date,
                    "change_fee_charged": float(change_fee),
                    "new_total_amount": float(booking.total_amount),
                    "confirmation_number": f"CHG{random.randint(100000, 999999)}"
                }

            return {"status": "error", "message": "Unable to confirm change"}

        except Exception as e:
            await db.rollback()
            return {
                "status": "error",
                "message": f"Change confirmation failed: {str(e)}"
            }    
    
    @staticmethod
    async def update_flight_date(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update flight date"""
        try:
            booking_ref = params.get('booking_reference')
            new_return_date = params.get('new_return_date')
            
            # Use change_flight logic for date updates
            change_params = {
                'booking_reference': booking_ref,
                'new_departure_date': new_return_date
            }
            
            return await FlightChangeService.change_flight(db, change_params)
            
        except Exception as e:
            return {"status": "error", "message": f"Date update failed: {str(e)}"}