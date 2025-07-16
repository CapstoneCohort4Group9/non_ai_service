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

class BookingServices:
    """
    Complete Booking Services for HopJetAir
    Handles all 10 booking-related endpoints
    """
    
    @staticmethod
    async def get_booking_details(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed booking information"""
        try:
            booking_ref = params.get('booking_reference')
            passenger_name = params.get('passenger_name')

            if not booking_ref:
                return {"status": "error", "message": "Booking reference is required"}

            # Load booking with passenger and segments
            booking_stmt = (
                select(Booking)
                .options(joinedload(Booking.passenger))
                .where(Booking.booking_reference == booking_ref)
            )
            booking = (await db.execute(booking_stmt)).scalars().first()

            if not booking:
                raise BookingNotFoundError(f"Booking {booking_ref} not found")

            # Verify passenger name if provided
            if passenger_name:
                passenger = booking.passenger
                full_name = f"{passenger.first_name} {passenger.last_name}".lower()
                if passenger_name.lower() not in full_name:
                    return {"status": "error", "message": "Passenger name does not match booking"}

            # Load booking segments with full relationship chain
            segment_stmt = (
                select(BookingSegment)
                .options(
                    joinedload(BookingSegment.flight)
                    .joinedload(Flight.airline),
                    joinedload(BookingSegment.flight)
                    .joinedload(Flight.route)
                    .joinedload(Route.origin_airport),
                    joinedload(BookingSegment.flight)
                    .joinedload(Flight.route)
                    .joinedload(Route.destination_airport),
                    joinedload(BookingSegment.flight)
                    .joinedload(Flight.aircraft)
                    .joinedload(Aircraft.aircraft_type)
                )
                .where(BookingSegment.booking_id == booking.id)
            )
            segments = (await db.execute(segment_stmt)).scalars().all()

            segment_details = []
            for segment in segments:
                flight = segment.flight
                route = flight.route

                segment_info = {
                    "segment_id": segment.id,
                    "flight_number": flight.flight_number,
                    "airline": flight.airline.name,
                    "origin": {
                        "code": route.origin_airport.iata_code,
                        "name": route.origin_airport.name,
                        "city": route.origin_airport.city,
                        "country": route.origin_airport.country
                    },
                    "destination": {
                        "code": route.destination_airport.iata_code,
                        "name": route.destination_airport.name,
                        "city": route.destination_airport.city,
                        "country": route.destination_airport.country
                    },
                    "departure_time": flight.scheduled_departure.isoformat(),
                    "arrival_time": flight.scheduled_arrival.isoformat(),
                    "flight_duration": f"{route.flight_duration_minutes // 60}h {route.flight_duration_minutes % 60}m",
                    "class_of_service": segment.class_of_service,
                    "seat_number": segment.seat_number,
                    "ticket_number": segment.ticket_number,
                    "fare_basis": segment.fare_basis,
                    "meal_preference": segment.meal_preference,
                    "baggage_allowance": f"{segment.baggage_allowance_kg}kg",
                    "check_in_status": segment.check_in_status,
                    "boarding_pass_issued": segment.boarding_pass_issued,
                    "special_requests": segment.special_requests,
                    "gate": flight.gate,
                    "terminal": flight.terminal,
                    "aircraft": f"{flight.aircraft.aircraft_type.manufacturer} {flight.aircraft.aircraft_type.model}"
                }
                segment_details.append(segment_info)

            passenger = booking.passenger

            return {
                "status": "success",
                "booking_details": {
                    "booking_reference": booking.booking_reference,
                    "booking_date": booking.booking_date.isoformat(),
                    "booking_status": booking.status,
                    "trip_type": booking.trip_type,
                    "booking_source": booking.booking_source,
                    "total_amount": float(booking.total_amount),
                    "currency": booking.currency,
                    "passenger_details": {
                        "name": f"{passenger.first_name} {passenger.last_name}",
                        "email": passenger.email,
                        "phone": passenger.phone,
                        "date_of_birth": passenger.date_of_birth.isoformat() if passenger.date_of_birth else None,
                        "nationality": passenger.nationality,
                        "passport_number": passenger.passport_number,
                        "frequent_flyer_number": passenger.frequent_flyer_number,
                        "tier_status": passenger.tier_status
                    },
                    "flight_segments": segment_details,
                    "segment_count": len(segment_details)
                }
            }

        except BookingNotFoundError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Failed to retrieve booking details: {str(e)}"}
    
    @staticmethod
    async def check_flight_reservation(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check flight reservation details"""
        try:
            booking_ref = params.get('booking_reference', params.get('confirmation_number'))
            last_name = params.get('last_name')
            email = params.get('email')
            full_name = params.get('full_name')

            booking = None

            if booking_ref:
                booking_stmt = (
                    select(Booking)
                    .options(joinedload(Booking.passenger))
                    .where(Booking.booking_reference == booking_ref)
                )
                booking = (await db.execute(booking_stmt)).scalars().first()

            elif email:
                passenger_stmt = select(Passenger).where(Passenger.email == email)
                passenger = (await db.execute(passenger_stmt)).scalars().first()
                if passenger:
                    booking_stmt = (
                        select(Booking)
                        .options(joinedload(Booking.passenger))
                        .where(Booking.passenger_id == passenger.id)
                    )
                    booking = (await db.execute(booking_stmt)).scalars().first()

            elif full_name:
                parts = full_name.split()
                if len(parts) >= 2:
                    first, last = parts[0], parts[-1]
                    passenger_stmt = select(Passenger).where(
                        and_(
                            Passenger.first_name.ilike(f"%{first}%"),
                            Passenger.last_name.ilike(f"%{last}%")
                        )
                    )
                    passenger = (await db.execute(passenger_stmt)).scalars().first()
                    if passenger:
                        booking_stmt = (
                            select(Booking)
                            .options(joinedload(Booking.passenger))
                            .where(Booking.passenger_id == passenger.id)
                        )
                        booking = (await db.execute(booking_stmt)).scalars().first()

            if not booking:
                return {
                    "status": "error",
                    "message": "Reservation not found. Please check your booking reference or contact customer service."
                }

            if last_name and last_name.lower() not in booking.passenger.last_name.lower():
                return {
                    "status": "error",
                    "message": "Last name does not match reservation"
                }

            # Load segments with full relationship tree
            segment_stmt = (
                select(BookingSegment)
                .options(
                    joinedload(BookingSegment.flight)
                    .joinedload(Flight.route)
                    .joinedload(Route.origin_airport),
                    joinedload(BookingSegment.flight)
                    .joinedload(Flight.route)
                    .joinedload(Route.destination_airport),
                    joinedload(BookingSegment.flight).joinedload(Flight.airline)
                )
                .where(BookingSegment.booking_id == booking.id)
            )
            segments = (await db.execute(segment_stmt)).scalars().all()

            reservation_details = {
                "reservation_found": True,
                "booking_reference": booking.booking_reference,
                "passenger_details": {
                    "name": f"{booking.passenger.first_name} {booking.passenger.last_name}",
                    "email": booking.passenger.email,
                    "phone": booking.passenger.phone,
                    "tier_status": booking.passenger.tier_status,
                    "frequent_flyer": booking.passenger.frequent_flyer_number
                },
                "booking_summary": {
                    "booking_date": booking.booking_date.isoformat(),
                    "booking_status": booking.status,
                    "total_amount": float(booking.total_amount),
                    "currency": booking.currency,
                    "trip_type": booking.trip_type,
                    "total_segments": len(segments)
                },
                "flights": []
            }

            for segment in segments:
                flight = segment.flight
                route = flight.route

                flight_info = {
                    "flight_number": flight.flight_number,
                    "airline": flight.airline.name,
                    "route": f"{route.origin_airport.iata_code} → {route.destination_airport.iata_code}",
                    "departure": {
                        "airport": route.origin_airport.name,
                        "city": route.origin_airport.city,
                        "time": flight.scheduled_departure.isoformat(),
                        "terminal": flight.terminal,
                        "gate": flight.gate
                    },
                    "arrival": {
                        "airport": route.destination_airport.name,
                        "city": route.destination_airport.city,
                        "time": flight.scheduled_arrival.isoformat()
                    },
                    "passenger_details": {
                        "seat": segment.seat_number,
                        "class": segment.class_of_service,
                        "meal": segment.meal_preference,
                        "baggage": f"{segment.baggage_allowance_kg}kg"
                    },
                    "status": {
                        "flight_status": flight.status,
                        "check_in_status": segment.check_in_status,
                        "boarding_pass_issued": segment.boarding_pass_issued
                    }
                }
                reservation_details["flights"].append(flight_info)

            return {
                "status": "success",
                "reservation": reservation_details
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Reservation check failed: {str(e)}"
            }
    
    @staticmethod
    async def query_booking_details(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        ENDPOINT 3: Query booking details with flexible search
        /query_booking_details
        """
        try:
            booking_ref = params.get('booking_reference')
            last_name = params.get('last_name')
            
            if not booking_ref:
                return {
                    "status": "error",
                    "message": "Booking reference is required"
                }
            
            # Use existing booking details logic
            search_params = {
                'booking_reference': booking_ref,
                'passenger_name': last_name
            }
            
            result = await BookingServices.get_booking_details(db, search_params)
            
            # Add query-specific information
            if result["status"] == "success":
                result["query_info"] = {
                    "search_method": "booking_reference",
                    "additional_verification": "last_name" if last_name else None,
                    "query_timestamp": datetime.now().isoformat()
                }
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Booking query failed: {str(e)}"
            }
    
    @staticmethod
    async def retrieve_booking_by_email(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve booking using email address"""
        try:
            email = params.get("email")

            if not email:
                return {"status": "error", "message": "Email address is required"}

            # Find passenger
            passenger_stmt = select(Passenger).where(Passenger.email == email)
            passenger = (await db.execute(passenger_stmt)).scalars().first()

            if not passenger:
                return {"status": "error", "message": "No bookings found for this email address"}

            # Get bookings with segments and flights preloaded
            booking_stmt = (
                select(Booking)
                .options(joinedload(Booking.passenger))
                .where(Booking.passenger_id == passenger.id)
                .order_by(Booking.booking_date.desc())
            )
            bookings = (await db.execute(booking_stmt)).scalars().all()

            if not bookings:
                return {"status": "error", "message": "No bookings found for this passenger"}

            booking_list = []
            for booking in bookings:
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
                    .order_by(BookingSegment.id.asc())
                )
                segments = (await db.execute(segment_stmt)).scalars().all()

                booking_info = {
                    "booking_reference": booking.booking_reference,
                    "booking_date": booking.booking_date.isoformat(),
                    "status": booking.status,
                    "total_amount": float(booking.total_amount),
                    "currency": booking.currency,
                    "trip_type": booking.trip_type,
                    "flight_count": len(segments),
                    "booking_source": booking.booking_source
                }

                if segments:
                    first_segment = segments[0]
                    flight = first_segment.flight
                    route = flight.route

                    booking_info["primary_route"] = {
                        "origin": route.origin_airport.iata_code,
                        "destination": route.destination_airport.iata_code,
                        "origin_city": route.origin_airport.city,
                        "destination_city": route.destination_airport.city,
                        "departure_date": flight.scheduled_departure.strftime('%Y-%m-%d'),
                        "departure_time": flight.scheduled_departure.strftime('%H:%M')
                    }

                    if len(segments) > 1:
                        return_flight = segments[-1].flight
                        booking_info["return_date"] = return_flight.scheduled_departure.strftime('%Y-%m-%d')

                booking_list.append(booking_info)

            return {
                "status": "success",
                "email": email,
                "passenger_details": {
                    "name": f"{passenger.first_name} {passenger.last_name}",
                    "tier_status": passenger.tier_status,
                    "frequent_flyer_number": passenger.frequent_flyer_number
                },
                "bookings_found": len(booking_list),
                "bookings": booking_list
            }

        except Exception as e:
            return {"status": "error", "message": f"Email booking retrieval failed: {str(e)}"}
    
    @staticmethod
    async def cancel_booking(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a flight booking"""
        try:
            confirmation_number = params.get("confirmation_number")

            if not confirmation_number:
                return {"status": "error", "message": "Confirmation number is required"}

            # Fetch booking with segments and flights eager-loaded
            booking_stmt = (
                select(Booking)
                .where(Booking.booking_reference == confirmation_number)
            )
            booking = (await db.execute(booking_stmt)).scalars().first()

            if not booking:
                raise BookingNotFoundError(f"Booking {confirmation_number} not found")

            if booking.status == "cancelled":
                return {
                    "status": "error",
                    "message": "Booking is already cancelled",
                    "booking_reference": confirmation_number,
                    "current_status": "cancelled"
                }

            segment_stmt = (
                select(BookingSegment)
                .options(
                    joinedload(BookingSegment.flight)
                )
                .where(BookingSegment.booking_id == booking.id)
            )
            segments = (await db.execute(segment_stmt)).scalars().all()

            cancellation_fee = Decimal("0")
            refund_amount = booking.total_amount
            cancellation_reason = "standard_cancellation"

            if segments:
                earliest_departure = min(s.flight.scheduled_departure for s in segments)
                time_to_departure = earliest_departure - datetime.now()

                if time_to_departure.total_seconds() < 0:
                    return {
                        "status": "error",
                        "message": "Cannot cancel booking for flights that have already departed"
                    }
                elif time_to_departure.total_seconds() < 7200:
                    return {
                        "status": "error",
                        "message": "Cannot cancel booking less than 2 hours before departure. Please contact airport."
                    }
                elif time_to_departure.days < 1:
                    cancellation_fee = booking.total_amount * Decimal("0.5")
                    cancellation_reason = "same_day_cancellation"
                elif time_to_departure.days < 7:
                    cancellation_fee = Decimal("200")
                    cancellation_reason = "short_notice_cancellation"
                elif time_to_departure.days < 30:
                    cancellation_fee = Decimal("100")
                    cancellation_reason = "advance_cancellation"

                refund_amount = booking.total_amount - cancellation_fee

            original_status = booking.status
            booking.status = "cancelled"

            refund_ref = f"RF{random.randint(100000, 999999)}"
            refund = Refund(
                booking_id=booking.id,
                refund_reference=refund_ref,
                refund_type="partial" if cancellation_fee > 0 else "full",
                amount=refund_amount,
                reason=cancellation_reason,
                status="approved",
                refund_method="credit_card"
            )
            db.add(refund)
            await db.commit()

            return {
                "status": "success",
                "cancellation_details": {
                    "booking_reference": confirmation_number,
                    "cancelled_at": datetime.now().isoformat(),
                    "original_status": original_status,
                    "cancellation_reason": cancellation_reason
                },
                "financial_details": {
                    "original_amount": float(booking.total_amount),
                    "cancellation_fee": float(cancellation_fee),
                    "refund_amount": float(refund_amount),
                    "currency": booking.currency,
                    "refund_reference": refund_ref
                },
                "refund_information": {
                    "refund_method": "Original payment method",
                    "processing_time": "5-7 business days",
                    "refund_status": "approved"
                },
                "policy_information": {
                    "cancellation_policy": {
                        "same_day": "50% cancellation fee",
                        "within_week": "$200 cancellation fee",
                        "within_month": "$100 cancellation fee",
                        "30_days_advance": "No cancellation fee"
                    }
                },
                "message": "Booking cancelled successfully. Refund will be processed to your original payment method."
            }

        except BookingNotFoundError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            await db.rollback()
            return {"status": "error", "message": f"Cancellation failed: {str(e)}"}
    
    @staticmethod
    async def send_itinerary_email(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send complete itinerary via email"""
        try:
            booking_ref = params.get("booking_reference")
            email = params.get("email")

            if not booking_ref:
                return {"status": "error", "message": "Booking reference is required"}

            booking_stmt = (
                select(Booking)
                .options(joinedload(Booking.passenger))
                .where(Booking.booking_reference == booking_ref)
            )
            booking = (await db.execute(booking_stmt)).scalars().first()

            if not booking:
                raise BookingNotFoundError(f"Booking {booking_ref} not found")

            passenger = booking.passenger
            recipient_email = email or passenger.email

            if not recipient_email:
                return {"status": "error", "message": "Email address is required"}

            segment_stmt = (
                select(BookingSegment)
                .options(
                    joinedload(BookingSegment.flight)
                    .joinedload(Flight.airline),
                    joinedload(BookingSegment.flight)
                    .joinedload(Flight.aircraft)
                    .joinedload(Aircraft.aircraft_type),
                    joinedload(BookingSegment.flight)
                    .joinedload(Flight.route)
                    .joinedload(Route.origin_airport),
                    joinedload(BookingSegment.flight)
                    .joinedload(Flight.route)
                    .joinedload(Route.destination_airport)
                )
                .where(BookingSegment.booking_id == booking.id)
                .order_by(BookingSegment.id.asc())
            )
            segments = (await db.execute(segment_stmt)).scalars().all()

            itinerary_details = {
                "booking_reference": booking_ref,
                "passenger_name": f"{passenger.first_name} {passenger.last_name}",
                "booking_date": booking.booking_date.isoformat(),
                "total_amount": float(booking.total_amount),
                "currency": booking.currency,
                "booking_status": booking.status,
                "trip_type": booking.trip_type,
                "flights": []
            }

            for i, segment in enumerate(segments, 1):
                flight = segment.flight
                route = flight.route

                flight_details = {
                    "segment_number": i,
                    "flight_number": flight.flight_number,
                    "airline": flight.airline.name,
                    "aircraft": f"{flight.aircraft.aircraft_type.manufacturer} {flight.aircraft.aircraft_type.model}",
                    "departure": {
                        "airport": f"{route.origin_airport.name} ({route.origin_airport.iata_code})",
                        "city": route.origin_airport.city,
                        "country": route.origin_airport.country,
                        "date": flight.scheduled_departure.strftime('%Y-%m-%d'),
                        "time": flight.scheduled_departure.strftime('%H:%M'),
                        "terminal": flight.terminal,
                        "gate": flight.gate
                    },
                    "arrival": {
                        "airport": f"{route.destination_airport.name} ({route.destination_airport.iata_code})",
                        "city": route.destination_airport.city,
                        "country": route.destination_airport.country,
                        "date": flight.scheduled_arrival.strftime('%Y-%m-%d'),
                        "time": flight.scheduled_arrival.strftime('%H:%M')
                    },
                    "passenger_info": {
                        "seat": segment.seat_number,
                        "class": segment.class_of_service,
                        "meal": segment.meal_preference,
                        "baggage": f"{segment.baggage_allowance_kg}kg included",
                        "ticket_number": segment.ticket_number
                    },
                    "flight_duration": f"{route.flight_duration_minutes // 60}h {route.flight_duration_minutes % 60}m",
                    "check_in_status": segment.check_in_status,
                    "boarding_pass_available": segment.boarding_pass_issued
                }
                itinerary_details["flights"].append(flight_details)

            return {
                "status": "success",
                "email_details": {
                    "booking_reference": booking_ref,
                    "email_sent": True,
                    "recipient_email": recipient_email,
                    "sent_timestamp": datetime.now().isoformat(),
                    "email_subject": f"HopJetAir Itinerary - {booking_ref}"
                },
                "itinerary_summary": itinerary_details,
                "email_content": {
                    "includes": [
                        "Complete flight itinerary",
                        "Booking confirmation details",
                        "Check-in information",
                        "Baggage allowance details",
                        "Contact information",
                        "Important travel tips"
                    ],
                    "attachments": [
                        "Boarding passes (if checked in)",
                        "Booking confirmation PDF"
                    ]
                },
                "travel_tips": [
                    "Check-in online 24 hours before departure",
                    "Arrive 2 hours early for domestic, 3 hours for international",
                    "Have valid ID ready for security",
                    "Review baggage restrictions"
                ],
                "message": "Complete itinerary sent successfully to your email"
            }

        except BookingNotFoundError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Itinerary email failed: {str(e)}"}        
    
    
    @staticmethod
    async def check_arrival_time(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check flight arrival time and details"""
        try:
            flight_number = params.get("flight_number")
            date_str = params.get("date")
            booking_ref = params.get("booking_reference")
            passenger_name = params.get("passenger_name")
            airline_name = params.get("airline")

            flight = None

            # ✈️ Search by flight number + date
            if flight_number and date_str:
                try:
                    search_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    stmt = (
                        select(Flight)
                        .options(
                            joinedload(Flight.route)
                                .joinedload(Route.origin_airport),
                            joinedload(Flight.route)
                                .joinedload(Route.destination_airport),
                            joinedload(Flight.airline),
                            joinedload(Flight.aircraft)
                                .joinedload(Aircraft.aircraft_type)
                        )
                        .where(
                            Flight.flight_number == flight_number,
                            func.date(Flight.scheduled_departure) == search_date
                        )
                    )
                    if airline_name:
                        stmt = stmt.join(Airline).where(Airline.name.ilike(f"%{airline_name}%"))

                    flight = (await db.execute(stmt)).scalars().first()
                except ValueError:
                    return {"status": "error", "message": "Invalid date format. Use YYYY-MM-DD"}

            # 📦 Search by booking reference
            elif booking_ref:
                booking_stmt = select(Booking).options(joinedload(Booking.passenger)).where(
                    Booking.booking_reference == booking_ref
                )
                booking = (await db.execute(booking_stmt)).scalars().first()
                if not booking:
                    raise BookingNotFoundError(f"Booking {booking_ref} not found")

                if passenger_name:
                    full_name = f"{booking.passenger.first_name} {booking.passenger.last_name}".lower()
                    if passenger_name.lower() not in full_name:
                        return {"status": "error", "message": "Passenger name does not match booking"}

                segment_stmt = (
                    select(BookingSegment)
                    .options(
                        joinedload(BookingSegment.flight)
                            .joinedload(Flight.route)
                            .joinedload(Route.origin_airport),
                        joinedload(BookingSegment.flight)
                            .joinedload(Flight.route)
                            .joinedload(Route.destination_airport),
                        joinedload(BookingSegment.flight)
                            .joinedload(Flight.airline),
                        joinedload(BookingSegment.flight)
                            .joinedload(Flight.aircraft)
                            .joinedload(Aircraft.aircraft_type)
                    )
                    .where(BookingSegment.booking_id == booking.id)
                    .order_by(BookingSegment.id.asc())
                )
                segment = (await db.execute(segment_stmt)).scalars().first()
                flight = segment.flight if segment else None

            else:
                return {
                    "status": "error",
                    "message": "Flight number with date or booking reference required"
                }

            if not flight:
                return {"status": "error", "message": "Flight not found"}

            # 🔍 Fetch latest flight status update
            update_stmt = (
                select(FlightStatusUpdate)
                .where(FlightStatusUpdate.flight_id == flight.id)
                .order_by(FlightStatusUpdate.update_time.desc())
            )
            latest_update = (await db.execute(update_stmt)).scalars().first()

            route = flight.route
            origin_airport = route.origin_airport
            destination_airport = route.destination_airport

            departure_info = {
                "flight_details": {
                    "flight_number": flight.flight_number,
                    "airline": flight.airline.name,
                    "aircraft": f"{flight.aircraft.aircraft_type.manufacturer} {flight.aircraft.aircraft_type.model}",
                    "status": flight.status
                },
                "route_information": {
                    "origin": {
                        "code": origin_airport.iata_code,
                        "name": origin_airport.name,
                        "city": origin_airport.city,
                        "country": origin_airport.country,
                        "timezone": origin_airport.timezone
                    },
                    "destination": {
                        "code": destination_airport.iata_code,
                        "name": destination_airport.name,
                        "city": destination_airport.city,
                        "country": destination_airport.country
                    },
                    "distance": f"{route.distance_km} km",
                    "flight_duration": f"{route.flight_duration_minutes // 60}h {route.flight_duration_minutes % 60}m"
                },
                "departure_times": {
                    "scheduled_departure": flight.scheduled_departure.isoformat(),
                    "scheduled_departure_local": flight.scheduled_departure.strftime('%Y-%m-%d %H:%M'),
                    "estimated_departure": flight.scheduled_departure.isoformat(),
                    "delay_minutes": 0
                },
                "terminal_information": {
                    "departure_airport": origin_airport.name,
                    "terminal": flight.terminal,
                    "gate": flight.gate
                },
                "check_in_information": {
                    "check_in_opens": (flight.scheduled_departure - timedelta(hours=24)).isoformat(),
                    "check_in_closes": (flight.scheduled_departure - timedelta(hours=2)).isoformat(),
                    "boarding_time": (flight.scheduled_departure - timedelta(minutes=30)).strftime('%H:%M'),
                    "gate_closes": (flight.scheduled_departure - timedelta(minutes=15)).strftime('%H:%M')
                },
                "travel_preparation": {
                    "arrival_recommendations": {
                        "domestic": "Arrive 2 hours before departure",
                        "international": "Arrive 3 hours before departure"
                    },
                    "required_documents": [
                        "Valid government-issued photo ID",
                        "Boarding pass (mobile or printed)",
                        "Passport for international travel"
                    ],
                    "security_guidelines": [
                        "Liquids in containers 100ml or less",
                        "Remove laptops and large electronics",
                        "Wear easily removable shoes",
                        "Have ID and boarding pass ready"
                    ],
                    "baggage_drop": {
                        "opens": (flight.scheduled_departure - timedelta(hours=3)).strftime('%H:%M'),
                        "closes": (flight.scheduled_departure - timedelta(minutes=45)).strftime('%H:%M')
                    }
                }
            }

            if latest_update:
                departure_info["departure_times"].update({
                    "estimated_departure": latest_update.new_departure_time.isoformat()
                        if latest_update.new_departure_time else flight.scheduled_departure.isoformat(),
                    "delay_minutes": latest_update.delay_minutes or 0,
                    "delay_reason": latest_update.reason,
                    "last_updated": latest_update.update_time.isoformat()
                })
                if latest_update.gate_change:
                    departure_info["terminal_information"]["gate_change"] = {
                        "old_gate": flight.gate,
                        "new_gate": latest_update.gate_change
                    }

            return {
                "status": "success",
                "departure_details": departure_info
            }

        except BookingNotFoundError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Departure time check failed: {str(e)}"}        
    
    @staticmethod
    async def update_flight_date(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update flight date for existing booking"""
        try:
            booking_ref = params.get("booking_reference")
            new_departure_date = params.get("new_departure_date")
            new_return_date = params.get("new_return_date")

            if not booking_ref:
                return {"status": "error", "message": "Booking reference is required"}

            booking_stmt = (
                select(Booking)
                .options(joinedload(Booking.passenger))
                .where(Booking.booking_reference == booking_ref)
            )
            booking = (await db.execute(booking_stmt)).scalars().first()

            if not booking:
                raise BookingNotFoundError(f"Booking {booking_ref} not found")

            if booking.status == "cancelled":
                return {"status": "error", "message": "Cannot update cancelled booking"}

            segment_stmt = (
                select(BookingSegment)
                .options(
                    joinedload(BookingSegment.flight)
                    .joinedload(Flight.route)
                )
                .where(BookingSegment.booking_id == booking.id)
            )
            segments = (await db.execute(segment_stmt)).scalars().all()

            if not segments:
                return {"status": "error", "message": "No flight segments found"}

            date_changes = []
            change_fee = Decimal("0")
            base_change_fee = Decimal("75")

            # ✏️ Departure date change
            if new_departure_date:
                try:
                    new_dep_date = datetime.strptime(new_departure_date, "%Y-%m-%d").date()
                    outbound_segment = segments[0]
                    route = outbound_segment.flight.route

                    flight_stmt = select(Flight).where(
                        Flight.route_id == route.id,
                        func.date(Flight.scheduled_departure) == new_dep_date,
                        Flight.status == "scheduled"
                    )
                    new_flights = (await db.execute(flight_stmt)).scalars().all()

                    if new_flights:
                        change_fee += base_change_fee
                        date_changes.append({
                            "segment": "outbound",
                            "old_date": outbound_segment.flight.scheduled_departure.strftime("%Y-%m-%d"),
                            "new_date": new_departure_date,
                            "flight_options": [
                                {
                                    "flight_number": f.flight_number,
                                    "departure_time": f.scheduled_departure.strftime("%H:%M"),
                                    "arrival_time": f.scheduled_arrival.strftime("%H:%M")
                                } for f in new_flights[:3]
                            ]
                        })
                    else:
                        return {
                            "status": "error",
                            "message": f"No flights available on {new_departure_date}"
                        }
                except ValueError:
                    return {"status": "error", "message": "Invalid departure date format. Use YYYY-MM-DD"}

            # 🔁 Return date change
            if new_return_date and len(segments) > 1:
                try:
                    new_ret_date = datetime.strptime(new_return_date, "%Y-%m-%d").date()
                    return_segment = segments[-1]
                    return_route = return_segment.flight.route

                    return_stmt = select(Flight).where(
                        Flight.route_id == return_route.id,
                        func.date(Flight.scheduled_departure) == new_ret_date,
                        Flight.status == "scheduled"
                    )
                    new_return_flights = (await db.execute(return_stmt)).scalars().all()

                    if new_return_flights:
                        change_fee += base_change_fee
                        date_changes.append({
                            "segment": "return",
                            "old_date": return_segment.flight.scheduled_departure.strftime("%Y-%m-%d"),
                            "new_date": new_return_date,
                            "flight_options": [
                                {
                                    "flight_number": f.flight_number,
                                    "departure_time": f.scheduled_departure.strftime("%H:%M"),
                                    "arrival_time": f.scheduled_arrival.strftime("%H:%M")
                                } for f in new_return_flights[:3]
                            ]
                        })
                    else:
                        return {
                            "status": "error",
                            "message": f"No return flights available on {new_return_date}"
                        }
                except ValueError:
                    return {"status": "error", "message": "Invalid return date format. Use YYYY-MM-DD"}

            if not date_changes:
                return {"status": "error", "message": "No valid date changes specified"}

            # ⏱️ Same-day fee adjustment
            for segment in segments:
                time_to_departure = segment.flight.scheduled_departure - datetime.now()
                if time_to_departure.days < 1:
                    change_fee *= Decimal("2")
                    break

            return {
                "status": "success",
                "date_change_details": {
                    "booking_reference": booking_ref,
                    "passenger_name": f"{booking.passenger.first_name} {booking.passenger.last_name}",
                    "changes_requested": date_changes,
                    "change_fee": float(change_fee),
                    "new_total_amount": float(booking.total_amount + change_fee),
                    "currency": booking.currency
                },
                "change_policy": {
                    "advance_changes": f"${base_change_fee} per segment",
                    "same_day_changes": f"${base_change_fee * 2} per segment",
                    "restrictions": "Changes must be made at least 2 hours before departure"
                },
                "next_steps": [
                    "Review available flight options",
                    "Confirm new flight selection",
                    "Pay change fee to complete modification",
                    "Receive updated itinerary"
                ],
                "confirmation_required": True,
                "message": "Date change options found. Please confirm your selection to proceed."
            }

        except BookingNotFoundError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Date update failed: {str(e)}"}
    
    @staticmethod
    async def send_email(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        ENDPOINT 10: Send various types of emails (boarding pass, confirmation, etc.)
        /send_email
        """
        try:
            passenger_name = params.get('passenger_name')
            flight_number = params.get('flight_number')
            flight_date_str = params.get('flight_date') # Renamed to avoid conflict with datetime.date object
            document = params.get('document', 'boarding_pass')
            email = params.get('email')
            booking_ref = params.get('booking_reference')
            
            # Validate required parameters
            if not any([passenger_name, booking_ref]): # Flight number and date are for lookup, not strictly required if booking_ref is present
                return {
                    "status": "error",
                    "message": "Either passenger name with flight number/date OR booking reference is required"
                }
            
            passenger = None
            booking = None
            flight = None
            segment = None

            if booking_ref:
                # 🔍 Get booking with passenger and segments eagerly loaded
                booking_stmt = select(Booking).where(Booking.booking_reference == booking_ref).options(
                    joinedload(Booking.passenger),
                    joinedload(Booking.segments).joinedload(BookingSegment.flight).joinedload(Flight.airline) # Load flight and airline
                )
                booking = (await db.execute(booking_stmt)).scalars().first()
                
                if booking:
                    passenger = booking.passenger
                    if booking.segments:
                        # If flight_number is provided, try to find a matching segment
                        if flight_number:
                            for seg in booking.segments:
                                if seg.flight and seg.flight.flight_number == flight_number:
                                    segment = seg
                                    flight = seg.flight
                                    break
                            if not segment:
                                return {
                                    "status": "error",
                                    "message": f"Flight {flight_number} not found in booking {booking_ref}"
                                }
                        else:
                            # If no flight_number specified, take the first segment's flight
                            segment = booking.segments[0]
                            flight = segment.flight
                    
                    # Verify passenger name if provided with booking_ref
                    if passenger_name and passenger:
                        full_name = f"{passenger.first_name} {passenger.last_name}".lower()
                        if passenger_name.lower() not in full_name:
                            return {
                                "status": "error",
                                "message": "Passenger name does not match booking"
                            }

            elif passenger_name and flight_number and flight_date_str:
                try:
                    search_date = datetime.strptime(flight_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return {
                        "status": "error",
                        "message": "Invalid date format. Please use YYYY-MM-DD"
                    }

                name_parts = passenger_name.split()
                first_name = name_parts[0]
                last_name = name_parts[-1] if len(name_parts) > 1 else ''

                # 🔍 Search for passenger and associated booking/segment/flight
                # We need to join through BookingSegment to Flight to match on flight details
                passenger_stmt = select(Passenger).where(
                    and_(
                        Passenger.first_name.ilike(f"%{first_name}%"),
                        Passenger.last_name.ilike(f"%{last_name}%")
                    )
                ).options(
                    joinedload(Passenger.bookings).joinedload(Booking.segments).joinedload(BookingSegment.flight) # Load bookings -> segments -> flights
                )
                passengers_result = await db.execute(passenger_stmt)
                all_passengers = passengers_result.scalars().all()

                for p in all_passengers:
                    for b in p.bookings:
                        for s in b.segments:
                            if s.flight and s.flight.flight_number == flight_number and \
                            s.flight.scheduled_departure.date() == search_date:
                                passenger = p
                                booking = b
                                segment = s
                                flight = s.flight
                                break
                        if passenger: break
                    if passenger: break

            if not passenger or not booking or not segment or not flight:
                return {
                    "status": "error",
                    "message": "Passenger, booking, or flight information not found with the provided details."
                }
            
            recipient_email = email or passenger.email
            if not recipient_email:
                return {
                    "status": "error",
                    "message": "Email address is required to send the document."
                }
            
            # Ensure flight's route, origin_airport, destination_airport, and airline are loaded
            # The above joinedloads for booking.segments should already bring in flight and airline.
            # Now explicitly load route and airports if not already.
            flight_details_stmt = select(Flight).where(Flight.id == flight.id).options(
                joinedload(Flight.route).joinedload(Route.origin_airport),
                joinedload(Flight.route).joinedload(Route.destination_airport),
                joinedload(Flight.airline),
                joinedload(Flight.aircraft).joinedload(Aircraft.aircraft_type)
            )
            flight_full = (await db.execute(flight_details_stmt)).scalars().first()

            if not flight_full:
                return {"status": "error", "message": "Detailed flight information could not be retrieved."}
            
            flight = flight_full # Update flight object with full details

            # Get latest status update for the specific flight
            latest_update_stmt = select(FlightStatusUpdate).where(
                FlightStatusUpdate.flight_id == flight.id
            ).order_by(FlightStatusUpdate.update_time.desc())
            latest_update = (await db.execute(latest_update_stmt)).scalars().first()
            
            route = flight.route
            origin_airport = route.origin_airport
            destination_airport = route.destination_airport
            
            email_content = {
                "recipient": recipient_email,
                "passenger_name": f"{passenger.first_name} {passenger.last_name}",
                "booking_reference": booking.booking_reference,
                "sent_at": datetime.now().isoformat()
            }
            
            # Populate flight_details for all document types
            flight_details = {
                "flight_number": flight.flight_number,
                "airline": flight.airline.name,
                "date": flight.scheduled_departure.strftime('%Y-%m-%d'),
                "departure": {
                    "time": flight.scheduled_departure.strftime('%H:%M'),
                    "airport": f"{origin_airport.name} ({origin_airport.iata_code})",
                    "terminal": flight.terminal,
                    "gate": flight.gate
                },
                "arrival": {
                    "time": flight.scheduled_arrival.strftime('%H:%M'),
                    "airport": f"{destination_airport.name} ({destination_airport.iata_code})"
                },
                "seat": segment.seat_number,
                "class": segment.class_of_service
            }
            email_content["flight_details"] = flight_details

            if document == 'boarding_pass':
                email_content.update({
                    "subject": f"HopJetAir Boarding Pass - {flight.flight_number}",
                    "document_type": "Boarding Pass",
                    "content_includes": [
                        "Mobile boarding pass",
                        "QR code for scanning",
                        "Gate and seat information",
                        "Boarding time details"
                    ],
                    "instructions": [
                        "Show mobile boarding pass at security",
                        "Present at boarding gate",
                        "Keep pass until destination"
                    ]
                })
                
            elif document == 'itinerary':
                email_content.update({
                    "subject": f"HopJetAir Itinerary - {booking.booking_reference}",
                    "document_type": "Complete Itinerary",
                    "content_includes": [
                        "All flight details",
                        "Check-in information",
                        "Baggage allowance",
                        "Contact information"
                    ]
                })
                
            elif document == 'confirmation':
                email_content.update({
                    "subject": f"HopJetAir Booking Confirmation - {booking.booking_reference}",
                    "document_type": "Booking Confirmation", 
                    "content_includes": [
                        "Booking summary",
                        "Payment confirmation",
                        "Passenger details",
                        "Terms and conditions"
                    ]
                })
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported document type: {document}. Supported types are 'boarding_pass', 'itinerary', 'confirmation'."
                }

            # Add latest flight status updates if available
            if latest_update:
                email_content["flight_details"]["status_update"] = {
                    "current_status": latest_update.status,
                    "estimated_departure": latest_update.new_departure_time.isoformat() if latest_update.new_departure_time else None,
                    "estimated_arrival": latest_update.new_arrival_time.isoformat() if latest_update.new_arrival_time else None,
                    "delay_minutes": latest_update.delay_minutes,
                    "reason": latest_update.reason,
                    "gate_change": latest_update.gate_change,
                    "last_updated": latest_update.update_time.isoformat()
                }
            
            return {
                "status": "success",
                "email_details": email_content,
                "delivery_info": {
                    "email_sent": True,
                    "delivery_method": "Email",
                    "estimated_delivery": "Within 5 minutes",
                    "backup_options": [
                        "Download from mobile app",
                        "Print at airport kiosk",
                        "Request at check-in counter"
                    ]
                },
                "support_info": {
                    "customer_service": "1-800-HOPJET",
                    "email_support": "support@hopjetair.com",
                    "live_chat": "Available on hopjetair.com"
                },
                "message": f"{document.replace('_', ' ').title()} sent successfully to {recipient_email}"
            }
            
        except BookingNotFoundError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            # In a real application, you'd want to log the full exception traceback for debugging.
            return {
                "status": "error",
                "message": f"Email sending failed: {str(e)}"
            }
    
    @staticmethod
    async def check_departure_time(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        ENDPOINT 8: Check flight departure time and details
        /check_departure_time
        """
        try:
            flight_number = params.get('flight_number')
            date_str = params.get('date')
            booking_ref = params.get('booking_reference')
            passenger_name = params.get('passenger_name')
            last_name = params.get('last_name') # This is redundant if passenger_name can be full name
            airline_name_param = params.get('airline') # Renamed to avoid conflict with Airline model
            departure_airport_code = params.get('departure_airport') # Renamed to clarify it's a code
            
            flight = None
            
            # Determine search strategy
            if booking_ref:
                # 🔍 Search by booking reference, eagerly loading related data
                booking_stmt = select(Booking).where(Booking.booking_reference == booking_ref).options(
                    joinedload(Booking.passenger),
                    joinedload(Booking.booking_segments).joinedload(BookingSegment.flight)
                                                .joinedload(Flight.airline),
                    joinedload(Booking.booking_segments).joinedload(BookingSegment.flight)
                                                .joinedload(Flight.aircraft).joinedload(Aircraft.aircraft_type),
                    joinedload(Booking.booking_segments).joinedload(BookingSegment.flight)
                                                .joinedload(Flight.route).joinedload(Route.origin_airport),
                    joinedload(Booking.booking_segments).joinedload(BookingSegment.flight)
                                                .joinedload(Flight.route).joinedload(Route.destination_airport)
                )
                booking = (await db.execute(booking_stmt)).scalars().first()
                
                if not booking:
                    raise BookingNotFoundError(f"Booking {booking_ref} not found")
                
                # Verify passenger name if provided with booking_ref
                if passenger_name or last_name:
                    passenger = booking.passenger
                    if not passenger:
                        return {"status": "error", "message": "Passenger information not found for this booking."}

                    # Construct full name for comparison (case-insensitive and flexible)
                    full_name_from_db = f"{passenger.first_name} {passenger.last_name}".lower()
                    provided_name_check = False
                    if passenger_name:
                        if passenger_name.lower() in full_name_from_db:
                            provided_name_check = True
                    if last_name and not provided_name_check: # Check last_name if passenger_name didn't match
                        if last_name.lower() in full_name_from_db:
                            provided_name_check = True

                    if not provided_name_check:
                        return {
                            "status": "error",
                            "message": "Passenger name provided does not match booking details."
                        }
                
                # Assuming a booking typically has one relevant flight segment for departure status
                # If multiple segments, could add logic to select based on flight_number if present
                if booking.booking_segments:
                    flight = booking.booking_segments[0].flight
                
            elif flight_number and date_str:
                try:
                    search_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    return {
                        "status": "error",
                        "message": "Invalid date format. Please use YYYY-MM-DD"
                    }
                
                # 🔍 Search by flight number and date, eagerly loading related data
                flight_stmt = select(Flight).where(
                    and_(
                        Flight.flight_number == flight_number,
                        func.date(Flight.scheduled_departure) == search_date
                    )
                ).options(
                    joinedload(Flight.airline),
                    joinedload(Flight.aircraft).joinedload(Aircraft.aircraft_type),
                    joinedload(Flight.route).joinedload(Route.origin_airport),
                    joinedload(Flight.route).joinedload(Route.destination_airport)
                )

                if airline_name_param:
                    # Add a join and filter for airline name if provided
                    flight_stmt = flight_stmt.join(Airline).where(Airline.name.ilike(f"%{airline_name_param}%"))
                
                if departure_airport_code:
                    # Add a join and filter for origin airport if provided
                    flight_stmt = flight_stmt.join(Route).join(Airport, Route.origin_airport_id == Airport.id).where(Airport.iata_code.ilike(departure_airport_code))

                flight = (await db.execute(flight_stmt)).scalars().first()
                
            else:
                return {
                    "status": "error",
                    "message": "Flight number with date OR booking reference is required to check departure time."
                }
            
            if not flight:
                return {
                    "status": "error",
                    "message": "Flight not found with the provided details. Please check the flight number, date, and booking reference."
                }
            
            # Get latest status update for the flight
            latest_update_stmt = select(FlightStatusUpdate).where(
                FlightStatusUpdate.flight_id == flight.id
            ).order_by(FlightStatusUpdate.update_time.desc())
            latest_update = (await db.execute(latest_update_stmt)).scalars().first()
            
            route = flight.route
            origin_airport = route.origin_airport
            destination_airport = route.destination_airport
            
            # Determine if this is domestic or international
            is_international = origin_airport.country != destination_airport.country
            
            departure_info = {
                "flight_details": {
                    "flight_number": flight.flight_number,
                    "airline": flight.airline.name,
                    "aircraft": f"{flight.aircraft.aircraft_type.manufacturer} {flight.aircraft.aircraft_type.model}",
                    "current_status": flight.status, # Using flight.status directly
                    "flight_type": "international" if is_international else "domestic"
                },
                "route_information": {
                    "origin": {
                        "code": origin_airport.iata_code,
                        "name": origin_airport.name,
                        "city": origin_airport.city,
                        "country": origin_airport.country,
                        "timezone": origin_airport.timezone
                    },
                    "destination": {
                        "code": destination_airport.iata_code,
                        "name": destination_airport.name,
                        "city": destination_airport.city,
                        "country": destination_airport.country,
                        "timezone": destination_airport.timezone
                    },
                    "distance": f"{route.distance_km} km",
                    "flight_duration": f"{route.flight_duration_minutes // 60}h {route.flight_duration_minutes % 60}m"
                },
                "departure_times": {
                    "scheduled_departure": flight.scheduled_departure.isoformat(),
                    "scheduled_departure_local": flight.scheduled_departure.strftime('%Y-%m-%d %H:%M'),
                    "departure_date": flight.scheduled_departure.strftime('%A, %B %d, %Y'),
                    "departure_time": flight.scheduled_departure.strftime('%I:%M %p')
                },
                "terminal_information": {
                    "departure_airport": origin_airport.name,
                    "terminal": flight.terminal or "TBA",
                    "gate": flight.gate or "TBA",
                    "check_in_counters": "Level 2, Terminal Main" # Placeholder, consider making dynamic
                },
                "check_in_information": {
                    "online_checkin": {
                        "opens": (flight.scheduled_departure - timedelta(hours=24)).isoformat(),
                        "closes": (flight.scheduled_departure - timedelta(hours=2)).isoformat(),
                        "url": "https://hopjetair.com/check-in"
                    },
                    "airport_checkin": {
                        "opens": (flight.scheduled_departure - timedelta(hours=3)).strftime('%H:%M'),
                        "closes": (flight.scheduled_departure - timedelta(minutes=45)).strftime('%H:%M')
                    },
                    "boarding_information": {
                        "boarding_begins": (flight.scheduled_departure - timedelta(minutes=45)).strftime('%H:%M'),
                        "boarding_ends": (flight.scheduled_departure - timedelta(minutes=15)).strftime('%H:%M'),
                        "final_call": (flight.scheduled_departure - timedelta(minutes=10)).strftime('%H:%M')
                    }
                }
            }
            
            # Add delay information if available
            if latest_update:
                departure_info["departure_times"].update({
                    "estimated_departure": latest_update.new_departure_time.isoformat() if latest_update.new_departure_time else flight.scheduled_departure.isoformat(),
                    "delay_minutes": latest_update.delay_minutes or 0,
                    "delay_reason": latest_update.reason,
                    "last_updated": latest_update.update_time.isoformat(),
                    # FIXED: Removed 'latest_update.status_message' as it's not an attribute
                    "status_message": "Flight delayed" if latest_update.delay_minutes else "On time"
                })

                if latest_update.gate_change:
                    departure_info["terminal_information"]["gate_change"] = {
                        "old_gate": flight.gate,
                        "new_gate": latest_update.gate_change,
                        "change_time": latest_update.update_time.isoformat()
                    }
            else:
                departure_info["departure_times"].update({
                    "estimated_departure": flight.scheduled_departure.isoformat(),
                    "delay_minutes": 0,
                    "status_message": "On time"
                })
            
            # Add comprehensive travel preparation info
            departure_info["travel_preparation"] = {
                "airport_arrival": {
                    "domestic_flights": "Arrive 2 hours before departure",
                    "international_flights": "Arrive 3 hours before departure",
                    "recommended_for_this_flight": "3 hours before departure" if is_international else "2 hours before departure"
                },
                "required_documents": {
                    "all_passengers": [
                        "Valid government-issued photo ID",
                        "Boarding pass (mobile or printed)"
                    ],
                    "international_travel": [
                        "Valid passport",
                        "Visa (if required for destination)",
                        "Health documentation (if required)"
                    ] if is_international else [],
                    "covid_requirements": "Check current requirements at hopjetair.com/travel-requirements"
                },
                "security_checkpoint": {
                    "preparation_tips": [
                        "Liquids in containers 100ml or less in clear bag",
                        "Remove laptops and large electronics from bags",
                        "Wear easily removable shoes",
                        "Have ID and boarding pass ready",
                        "Remove jackets and belts"
                    ],
                    "prohibited_items": [
                        "Sharp objects over 6cm",
                        "Liquids over 100ml (except baby formula/medicine)",
                        "Flammable items",
                        "Tools and sporting equipment"
                    ]
                },
                "baggage_services": {
                    "baggage_drop": {
                        "opens": (flight.scheduled_departure - timedelta(hours=3)).strftime('%H:%M'),
                        "closes": (flight.scheduled_departure - timedelta(minutes=45)).strftime('%H:%M'),
                        "location": "Level 2, Terminal Main" # Placeholder
                    },
                    "oversized_baggage": "Special counter at Level 1",
                    "baggage_weight_limit": "23kg for economy, 32kg for business/first"
                }
            }
            
            # Add airport services and amenities
            departure_info["airport_services"] = {
                "dining": [
                    "Food court - Terminal Main",
                    "Restaurant - Gate area",
                    "Coffee shops throughout terminal"
                ],
                "shopping": [
                    "Duty-free shop",
                    "Travel essentials store",
                    "Gift shop"
                ],
                "facilities": [
                    "Free WiFi throughout terminal",
                    "Charging stations at all gates",
                    "Business lounge (Level 3)",
                    "Family restrooms",
                    "ATM machines",
                    "Currency exchange"
                ],
                "transportation": {
                    "to_airport": [
                        "Taxi service",
                        "Ride-sharing pickup - Level 1",
                        "Public transportation",
                        "Hotel shuttles",
                        "Rental car return"
                    ],
                    "parking": [
                        "Short-term parking - $8/hour",
                        "Long-term parking - $12/day",
                        "Valet parking - $25/day"
                    ]
                }
            }
            
            # Add weather and travel alerts if applicable
            departure_info["travel_alerts"] = {
                "weather_advisory": "Check current weather conditions for potential delays",
                "traffic_advisory": "Allow extra time for airport access during peak hours",
                "special_notices": [
                    "Terminal construction may affect access routes",
                    "Enhanced security procedures in effect"
                ]
            }
            
            return {
                "status": "success",
                "departure_details": departure_info,
                "helpful_tips": [
                    "Download the HopJetAir mobile app for real-time updates",
                    "Check in online to save time at the airport",
                    "Monitor flight status for any last-minute changes",
                    "Join HopJetAir Rewards for priority boarding"
                ]
            }
            
        except BookingNotFoundError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            # In a real application, you'd want to log the full exception traceback for debugging.
            return {
                "status": "error",
                "message": f"Departure time check failed: {str(e)}"
            }

    