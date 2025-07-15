from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
import random
import string
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from database_models import *
from database_connection import DatabaseError, BookingNotFoundError, FlightNotFoundError, PassengerNotFoundError

class SeatManagementService:
    @staticmethod
    async def check_seat_availability(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check available seats on a flight"""
        try:
            booking_ref = params.get('booking_reference')
            flight_number = params.get('flight_number')
            seat_preference = params.get('seat_preference', 'any')
            
            # Get booking and flight info
            booking = db.query(Booking).filter_by(booking_reference=booking_ref).first()
            if not booking:
                raise BookingNotFoundError(f"Booking {booking_ref} not found")
            
            # Get the flight
            segment = db.query(BookingSegment).filter_by(booking_id=booking.id).first()
            if not segment:
                return {"status": "error", "message": "No flight segments found"}
            
            flight = segment.flight
            aircraft_type = flight.aircraft.aircraft_type
            
            # Get seat map
            seat_map_query = db.query(SeatMap).filter_by(aircraft_type_id=aircraft_type.id)
            
            # Filter by passenger's class
            passenger_class = segment.class_of_service
            seat_map_query = seat_map_query.filter_by(class_of_service=passenger_class)
            
            # Apply seat preference filter
            if seat_preference and seat_preference != 'any':
                if seat_preference == 'window':
                    seat_map_query = seat_map_query.filter_by(seat_type='window')
                elif seat_preference == 'aisle':
                    seat_map_query = seat_map_query.filter_by(seat_type='aisle')
                elif seat_preference == 'exit':
                    seat_map_query = seat_map_query.filter_by(is_exit_row=True)
            
            available_seats = seat_map_query.all()
            
            # Get occupied seats
            occupied_seats = db.query(FlightSeat).filter_by(
                flight_id=flight.id,
                status='occupied'
            ).all()
            
            occupied_seat_numbers = {seat.seat_number for seat in occupied_seats}
            
            # Filter out occupied and blocked seats
            free_seats = []
            for seat in available_seats:
                if seat.seat_number not in occupied_seat_numbers and not seat.is_blocked:
                    seat_fee = 0
                    if seat.extra_legroom:
                        seat_fee = 25
                    elif seat.is_exit_row:
                        seat_fee = 15
                    
                    seat_info = {
                        'seat_number': seat.seat_number,
                        'seat_type': seat.seat_type,
                        'extra_legroom': seat.extra_legroom,
                        'exit_row': seat.is_exit_row,
                        'fee': seat_fee,
                        'available': True
                    }
                    free_seats.append(seat_info)
            
            # Organize by rows for better display
            seat_rows = {}
            for seat in free_seats:
                row = seat['seat_number'][:-1]  # Remove letter
                if row not in seat_rows:
                    seat_rows[row] = []
                seat_rows[row].append(seat)
            
            return {
                "status": "success",
                "flight_number": flight.flight_number,
                "aircraft_type": f"{aircraft_type.manufacturer} {aircraft_type.model}",
                "passenger_class": passenger_class,
                "seat_preference": seat_preference,
                "available_seats": free_seats,
                "seats_by_row": seat_rows,
                "total_available": len(free_seats),
                "seat_map_info": {
                    "total_seats": aircraft_type.total_seats,
                    "occupied_seats": len(occupied_seat_numbers),
                    "available_seats": len(free_seats)
                }
            }
            
        except BookingNotFoundError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Seat availability check failed: {str(e)}"}
    
    @staticmethod
    async def change_seat(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Change passenger seat assignment"""
        try:
            booking_ref = params.get('booking_reference')
            new_seat = params.get('new_seat')
            
            booking = db.query(Booking).filter_by(booking_reference=booking_ref).first()
            if not booking:
                raise BookingNotFoundError(f"Booking {booking_ref} not found")
            
            segment = db.query(BookingSegment).filter_by(booking_id=booking.id).first()
            if not segment:
                return {"status": "error", "message": "No flight segments found"}
            
            flight = segment.flight
            
            # Check if new seat is available
            existing_seat = db.query(FlightSeat).filter_by(
                flight_id=flight.id,
                seat_number=new_seat
            ).first()
            
            if existing_seat and existing_seat.status == 'occupied':
                return {
                    "status": "error",
                    "message": f"Seat {new_seat} is already occupied"
                }
            
            # Check seat map for fees and validity
            seat_map_entry = db.query(SeatMap).filter_by(
                aircraft_type_id=flight.aircraft.aircraft_type.id,
                seat_number=new_seat
            ).first()
            
            if not seat_map_entry:
                return {
                    "status": "error",
                    "message": f"Seat {new_seat} does not exist on this aircraft"
                }
            
            # Check class compatibility
            if seat_map_entry.class_of_service != segment.class_of_service:
                return {
                    "status": "error",
                    "message": f"Seat {new_seat} is not available for {segment.class_of_service} class"
                }
            
            # Calculate seat fee
            seat_fee = 0
            if seat_map_entry.extra_legroom:
                seat_fee = 25
            elif seat_map_entry.is_exit_row:
                seat_fee = 15
            
            # Update seat assignment
            old_seat = segment.seat_number
            segment.seat_number = new_seat
            
            # Update flight seat records
            if existing_seat:
                existing_seat.passenger_id = segment.passenger_id
                existing_seat.booking_segment_id = segment.id
                existing_seat.status = 'occupied'
                existing_seat.seat_fee = Decimal(str(seat_fee))
            else:
                new_flight_seat = FlightSeat(
                    flight_id=flight.id,
                    seat_number=new_seat,
                    passenger_id=segment.passenger_id,
                    booking_segment_id=segment.id,
                    seat_fee=Decimal(str(seat_fee)),
                    status='occupied'
                )
                db.add(new_flight_seat)
            
            # Free up old seat
            if old_seat:
                old_flight_seat = db.query(FlightSeat).filter_by(
                    flight_id=flight.id,
                    seat_number=old_seat
                ).first()
                if old_flight_seat:
                    old_flight_seat.passenger_id = None
                    old_flight_seat.booking_segment_id = None
                    old_flight_seat.status = 'available'
                    old_flight_seat.seat_fee = 0
            
            db.commit()
            
            return {
                "status": "success",
                "message": f"Seat changed successfully from {old_seat or 'unassigned'} to {new_seat}",
                "booking_reference": booking_ref,
                "flight_number": flight.flight_number,
                "old_seat": old_seat,
                "new_seat": new_seat,
                "seat_details": {
                    "seat_type": seat_map_entry.seat_type,
                    "extra_legroom": seat_map_entry.extra_legroom,
                    "exit_row": seat_map_entry.is_exit_row,
                    "fee": seat_fee
                },
                "total_fees": seat_fee
            }
            
        except BookingNotFoundError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": f"Seat change failed: {str(e)}"}
    
    @staticmethod
    async def choose_seat(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Choose seat during booking or check-in"""
        try:
            booking_ref = params.get('booking_reference')
            seat_number = params.get('seat_number')
            
            booking = db.query(Booking).filter_by(booking_reference=booking_ref).first()
            if not booking:
                raise BookingNotFoundError(f"Booking {booking_ref} not found")
            
            segment = db.query(BookingSegment).filter_by(booking_id=booking.id).first()
            if not segment:
                return {"status": "error", "message": "No flight segments found"}
            
            # Use change_seat logic for seat selection
            result = await SeatManagementService.change_seat(db, {
                'booking_reference': booking_ref,
                'new_seat': seat_number
            })
            
            if result['status'] == 'success':
                result['message'] = f"Seat {seat_number} successfully selected"
                result['confirmation'] = f"Your seat {seat_number} is confirmed for flight {result['flight_number']}"
            
            return result
            
        except Exception as e:
            return {"status": "error", "message": f"Seat selection failed: {str(e)}"}

class CheckInService:
    @staticmethod
    async def check_in_passenger(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check in passenger for flight"""
        try:
            booking_ref = params.get('booking_reference')
            last_name = params.get('last_name')
            flight_number = params.get('flight_number')
            
            booking = db.query(Booking).filter_by(booking_reference=booking_ref).first()
            if not booking:
                raise BookingNotFoundError(f"Booking {booking_ref} not found")
            
            # Verify last name if provided
            if last_name and last_name.lower() not in booking.passenger.last_name.lower():
                return {
                    "status": "error",
                    "message": "Last name does not match booking"
                }
            
            # Get booking segments
            segments_query = db.query(BookingSegment).filter_by(booking_id=booking.id)
            if flight_number:
                segments_query = segments_query.join(Flight).filter(Flight.flight_number == flight_number)
            
            segments = segments_query.all()
            
            if not segments:
                return {"status": "error", "message": "No flight segments found"}
            
            checked_in_segments = []
            for segment in segments:
                flight = segment.flight
                
                # Check if already checked in
                if segment.check_in_status == 'checked_in':
                    checked_in_segments.append({
                        "flight_number": flight.flight_number,
                        "status": "already_checked_in",
                        "seat": segment.seat_number,
                        "check_in_time": "Previously completed"
                    })
                    continue
                
                # Check timing (24 hours before departure)
                time_to_departure = flight.scheduled_departure - datetime.now()
                if time_to_departure.total_seconds() > 24 * 3600:
                    checked_in_segments.append({
                        "flight_number": flight.flight_number,
                        "status": "too_early",
                        "message": "Check-in opens 24 hours before departure",
                        "opens_at": (flight.scheduled_departure - timedelta(hours=24)).isoformat()
                    })
                    continue
                
                # Check if too late (2 hours before departure for international, 1 hour for domestic)
                route = flight.route
                cutoff_hours = 2 if route.distance_km > 2000 else 1
                if time_to_departure.total_seconds() < cutoff_hours * 3600:
                    checked_in_segments.append({
                        "flight_number": flight.flight_number,
                        "status": "too_late",
                        "message": f"Check-in closed {cutoff_hours} hours before departure",
                        "closed_at": (flight.scheduled_departure - timedelta(hours=cutoff_hours)).isoformat()
                    })
                    continue
                
                # Perform check-in
                segment.check_in_status = 'checked_in'
                
                # Assign seat if not already assigned
                if not segment.seat_number:
                    # Find available seat
                    available_seats = db.query(SeatMap).filter_by(
                        aircraft_type_id=flight.aircraft.aircraft_type.id,
                        class_of_service=segment.class_of_service
                    ).limit(10).all()
                    
                    if available_seats:
                        # Prefer aisle seats for automatic assignment
                        aisle_seats = [s for s in available_seats if s.seat_type == 'aisle']
                        selected_seat = aisle_seats[0] if aisle_seats else available_seats[0]
                        segment.seat_number = selected_seat.seat_number
                        
                        # Create flight seat record
                        flight_seat = FlightSeat(
                            flight_id=flight.id,
                            seat_number=selected_seat.seat_number,
                            passenger_id=segment.passenger_id,
                            booking_segment_id=segment.id,
                            status='occupied'
                        )
                        db.add(flight_seat)
                
                route = flight.route
                checked_in_segments.append({
                    "flight_number": flight.flight_number,
                    "status": "checked_in",
                    "seat": segment.seat_number,
                    "gate": flight.gate,
                    "terminal": flight.terminal,
                    "departure_time": flight.scheduled_departure.isoformat(),
                    "route": f"{route.origin_airport.iata_code} → {route.destination_airport.iata_code}",
                    "boarding_time": (flight.scheduled_departure - timedelta(minutes=30)).isoformat(),
                    "check_in_time": datetime.now().isoformat()
                })
            
            db.commit()
            
            passenger = booking.passenger
            return {
                "status": "success",
                "booking_reference": booking_ref,
                "passenger_name": f"{passenger.first_name} {passenger.last_name}",
                "check_in_completed": len([s for s in checked_in_segments if s["status"] == "checked_in"]),
                "segments": checked_in_segments,
                "boarding_pass_available": any(s["status"] == "checked_in" for s in checked_in_segments),
                "next_steps": [
                    "Arrive at gate 45 minutes before domestic flights",
                    "Arrive at gate 60 minutes before international flights",
                    "Have photo ID ready",
                    "Download boarding pass or print at kiosk"
                ]
            }
            
        except BookingNotFoundError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": f"Check-in failed: {str(e)}"}
    
    @staticmethod
    async def check_in(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Basic check-in function"""
        try:
            flight_number = params.get('flight_number')
            last_name = params.get('last_name')
            departure_airport = params.get('departure_airport')
            
            # Find passenger by last name and flight
            passenger = db.query(Passenger).filter(
                Passenger.last_name.ilike(f"%{last_name}%")
            ).first()
            
            if not passenger:
                return {"status": "error", "message": f"Passenger {last_name} not found"}
            
            # Find booking segment for this flight
            segment = db.query(BookingSegment).join(Flight).join(Booking).filter(
                and_(
                    Flight.flight_number == flight_number,
                    Booking.passenger_id == passenger.id
                )
            ).first()
            
            if not segment:
                return {"status": "error", "message": f"No booking found for {last_name} on flight {flight_number}"}
            
            # Use check_in_passenger logic
            result = await CheckInService.check_in_passenger(db, {
                'booking_reference': segment.booking.booking_reference,
                'last_name': last_name,
                'flight_number': flight_number
            })
            
            return result
            
        except Exception as e:
            return {"status": "error", "message": f"Check-in failed: {str(e)}"}
    
    @staticmethod
    async def check_flight_checkin_status(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check flight check-in status"""
        try:
            booking_ref = params.get('booking_reference')
            flight_number = params.get('flight_number')
            confirmation_number = params.get('confirmation_number')
            
            # Use booking reference or confirmation number
            search_ref = booking_ref or confirmation_number
            
            booking = db.query(Booking).filter_by(booking_reference=search_ref).first()
            if not booking:
                raise BookingNotFoundError(f"Booking {search_ref} not found")
            
            # Get specific flight segment
            segments_query = db.query(BookingSegment).filter_by(booking_id=booking.id)
            if flight_number:
                segments_query = segments_query.join(Flight).filter(Flight.flight_number == flight_number)
            
            segments = segments_query.all()
            
            if not segments:
                return {"status": "error", "message": "No flight segments found"}
            
            segment_statuses = []
            for segment in segments:
                flight = segment.flight
                route = flight.route
                
                # Determine check-in window
                departure_time = flight.scheduled_departure
                checkin_opens = departure_time - timedelta(hours=24)
                cutoff_hours = 2 if route.distance_km > 2000 else 1
                checkin_closes = departure_time - timedelta(hours=cutoff_hours)
                
                now = datetime.now()
                checkin_available = checkin_opens <= now <= checkin_closes
                
                segment_info = {
                    "flight_number": flight.flight_number,
                    "route": f"{route.origin_airport.iata_code} → {route.destination_airport.iata_code}",
                    "departure_time": departure_time.isoformat(),
                    "check_in_status": segment.check_in_status,
                    "seat_assigned": segment.seat_number,
                    "boarding_pass_issued": segment.boarding_pass_issued,
                    "gate": flight.gate,
                    "terminal": flight.terminal,
                    "check_in_window": {
                        "opens": checkin_opens.isoformat(),
                        "closes": checkin_closes.isoformat(),
                        "currently_available": checkin_available
                    }
                }
                
                if segment.check_in_status == 'checked_in':
                    segment_info["boarding_time"] = (departure_time - timedelta(minutes=30)).isoformat()
                    segment_info["status_message"] = "Check-in completed"
                elif not checkin_available and now < checkin_opens:
                    segment_info["status_message"] = "Check-in not yet available"
                elif not checkin_available and now > checkin_closes:
                    segment_info["status_message"] = "Check-in closed - contact gate agent"
                else:
                    segment_info["status_message"] = "Ready for check-in"
                
                segment_statuses.append(segment_info)
            
            passenger = booking.passenger
            return {
                "status": "success",
                "booking_reference": search_ref,
                "passenger_name": f"{passenger.first_name} {passenger.last_name}",
                "overall_status": "checked_in" if all(s["check_in_status"] == "checked_in" for s in segments) else "pending",
                "segments": segment_statuses,
                "can_check_in_online": any(s["check_in_window"]["currently_available"] for s in segment_statuses)
            }
            
        except BookingNotFoundError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Check-in status check failed: {str(e)}"}

class BoardingPassService:
    @staticmethod
    async def get_boarding_pass(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get boarding pass for checked-in passenger"""
        try:
            booking_ref = params.get('booking_reference')
            flight_number = params.get('flight_number')
            passenger_name = params.get('passenger_name')
            
            booking = db.query(Booking).filter_by(booking_reference=booking_ref).first()
            if not booking:
                raise BookingNotFoundError(f"Booking {booking_ref} not found")
            
            # Find the specific segment
            segment_query = db.query(BookingSegment).filter_by(booking_id=booking.id)
            if flight_number:
                segment_query = segment_query.join(Flight).filter(Flight.flight_number == flight_number)
            
            segment = segment_query.first()
            
            if not segment:
                return {"status": "error", "message": f"Flight {flight_number} not found in booking"}
            
            if segment.check_in_status != 'checked_in':
                return {
                    "status": "error",
                    "message": "Passenger not checked in. Please check in first.",
                    "check_in_available": True
                }
            
            # Mark boarding pass as issued
            segment.boarding_pass_issued = True
            db.commit()
            
            flight = segment.flight
            route = flight.route
            passenger = booking.passenger
            
            # Generate boarding pass data
            boarding_pass = {
                "passenger_name": f"{passenger.first_name} {passenger.last_name}",
                "booking_reference": booking_ref,
                "flight_details": {
                    "flight_number": flight.flight_number,
                    "date": flight.scheduled_departure.strftime('%Y-%m-%d'),
                    "departure_time": flight.scheduled_departure.strftime('%H:%M'),
                    "boarding_time": (flight.scheduled_departure - timedelta(minutes=30)).strftime('%H:%M')
                },
                "route": {
                    "origin": {
                        "code": route.origin_airport.iata_code,
                        "name": route.origin_airport.name,
                        "city": route.origin_airport.city
                    },
                    "destination": {
                        "code": route.destination_airport.iata_code,
                        "name": route.destination_airport.name,
                        "city": route.destination_airport.city
                    }
                },
                "seat_assignment": {
                    "seat": segment.seat_number,
                    "class": segment.class_of_service.title()
                },
                "gate_info": {
                    "gate": flight.gate,
                    "terminal": flight.terminal
                },
                "sequence_number": random.randint(1, 200),
                "barcode": f"M1{booking_ref}{flight.flight_number}{segment.seat_number}{random.randint(1000, 9999)}",
                "frequent_flyer": passenger.frequent_flyer_number,
                "baggage_allowance": f"{segment.baggage_allowance_kg}kg"
            }
            
            return {
                "status": "success",
                "boarding_pass": boarding_pass,
                "format": "mobile_pass",
                "download_url": f"https://hopjetair.com/boarding-pass/{booking_ref}",
                "qr_code": f"https://hopjetair.com/qr/{booking_ref}",
                "instructions": [
                    "Show this boarding pass at security checkpoint",
                    "Present at boarding gate",
                    "Keep phone battery charged",
                    "Screenshot recommended as backup"
                ],
                "important_notes": [
                    f"Boarding begins at {boarding_pass['flight_details']['boarding_time']}",
                    f"Gate {flight.gate} in Terminal {flight.terminal}",
                    "Arrive at gate 30 minutes before departure"
                ]
            }
            
        except BookingNotFoundError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Boarding pass generation failed: {str(e)}"}
    
    @staticmethod
    async def get_boarding_pass_pdf(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get boarding pass in PDF format"""
        try:
            booking_ref = params.get('booking_reference')
            flight_number = params.get('flight_number')
            email = params.get('email')
            
            # Get standard boarding pass data
            boarding_pass_result = await BoardingPassService.get_boarding_pass(db, {
                'booking_reference': booking_ref,
                'flight_number': flight_number
            })
            
            if boarding_pass_result['status'] != 'success':
                return boarding_pass_result
            
            # Enhance with PDF-specific information
            boarding_pass_data = boarding_pass_result['boarding_pass']
            
            return {
                "status": "success",
                "boarding_pass": boarding_pass_data,
                "format": "PDF",
                "download_link": f"https://hopjetair.com/boarding-pass-pdf/{booking_ref}",
                "print_instructions": [
                    "Print on standard 8.5x11 inch paper",
                    "Use portrait orientation",
                    "Ensure barcode prints clearly",
                    "Do not fold or tear barcode area"
                ],
                "pdf_ready": True,
                "file_size": "245 KB",
                "email_option": {
                    "available": True,
                    "recipient": email or "passenger@example.com",
                    "subject": f"Boarding Pass - Flight {boarding_pass_data['flight_details']['flight_number']}"
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": f"PDF boarding pass generation failed: {str(e)}"}
    
    @staticmethod
    async def send_boarding_pass_email(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send boarding pass via email"""
        try:
            booking_ref = params.get('booking_reference')
            passenger_name = params.get('passenger_name')
            flight_number = params.get('flight_number')
            flight_date = params.get('flight_date')
            
            # Verify booking exists and get passenger email
            booking = db.query(Booking).filter_by(booking_reference=booking_ref).first()
            if not booking:
                return {"status": "error", "message": f"Booking {booking_ref} not found"}
            
            passenger = booking.passenger
            email_address = passenger.email or "passenger@example.com"
            
            # Get boarding pass data
            boarding_pass_result = await BoardingPassService.get_boarding_pass(db, {
                'booking_reference': booking_ref,
                'flight_number': flight_number
            })
            
            if boarding_pass_result['status'] != 'success':
                return {
                    "status": "error",
                    "message": "Cannot send boarding pass - passenger not checked in"
                }
            
            return {
                "status": "success",
                "booking_reference": booking_ref,
                "passenger_name": passenger_name or f"{passenger.first_name} {passenger.last_name}",
                "flight_number": flight_number,
                "email_details": {
                    "sent": True,
                    "recipient": email_address,
                    "sent_timestamp": datetime.now().isoformat(),
                    "subject": f"HopJetAir Boarding Pass - Flight {flight_number}",
                    "delivery_time": "Usually delivered within 5 minutes"
                },
                "message": "Boarding pass sent successfully to your email",
                "backup_options": [
                    "Download from HopJetAir mobile app",
                    "Print at airport kiosk with booking reference",
                    "Get paper boarding pass at check-in counter"
                ],
                "email_contents": [
                    "Mobile boarding pass (scannable)",
                    "PDF version for printing",
                    "Flight details and gate information",
                    "Important travel reminders"
                ]
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Email sending failed: {str(e)}"}
    
    @staticmethod
    async def verify_booking_and_get_boarding_pass(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Verify booking details and provide boarding pass"""
        try:
            flight_number = params.get('flight_number')
            last_name = params.get('last_name')
            first_initial = params.get('first_initial')
            
            # Find passenger by name
            passenger = db.query(Passenger).filter(
                and_(
                    Passenger.last_name.ilike(f"%{last_name}%"),
                    Passenger.first_name.ilike(f"{first_initial}%")
                )
            ).first()
            
            if not passenger:
                return {
                    "status": "error",
                    "message": f"Passenger {first_initial}. {last_name} not found"
                }
            
            # Find booking for this flight
            segment = db.query(BookingSegment).join(Flight).join(Booking).filter(
                and_(
                    Flight.flight_number == flight_number,
                    Booking.passenger_id == passenger.id
                )
            ).first()
            
            if not segment:
                return {
                    "status": "error",
                    "message": f"No booking found for {first_initial}. {last_name} on flight {flight_number}"
                }
            
            booking = segment.booking
            flight = segment.flight
            
            # Verify passenger is checked in
            if segment.check_in_status != 'checked_in':
                return {
                    "status": "error",
                    "message": "Passenger not checked in for this flight",
                    "booking_reference": booking.booking_reference,
                    "check_in_required": True
                }
            
            # Get boarding pass
            boarding_pass_result = await BoardingPassService.get_boarding_pass(db, {
                'booking_reference': booking.booking_reference,
                'flight_number': flight_number
            })
            
            if boarding_pass_result['status'] == 'success':
                boarding_pass_result['verification'] = {
                    "passenger_verified": True,
                    "booking_verified": True,
                    "check_in_verified": True,
                    "verification_method": "name_and_flight"
                }
            
            return boarding_pass_result
            
        except Exception as e:
            return {"status": "error", "message": f"Verification and boarding pass retrieval failed: {str(e)}"}
    
    # @staticmethod
    # async def resend_boarding_pass(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
    #     """Resend boarding pass to passenger email"""
    #     try:
    #         email = params.get('email')
            
    #         # Find passenger by email
    #         passenger = db.query(Passenger).filter_by(email=email).first()
    #         if not passenger:
    #             return {"status": "error", "message": f"No passenger found with email {email}"}
            
    #         # Find recent bookings
    #         recent_bookings = db.query(Booking).filter(
    #             and_(
    #                 Booking.passenger_id == passenger.id,
    #                 Booking.booking_date >= datetime.now() - timedelta(days=30)
    #             )
    #         ).all()
            
    #         if not recent_bookings:
    #             return {"status": "error", "message": "No recent bookings found for this email"}
            
    #         # Find checked-in segments
    #         checked_in_segments = []
    #         for booking in recent_bookings:
    #             segments = db.query(BookingSegment).filter(
    #                 and_(
    #                     BookingSegment.booking_id == booking.id,
    #                     BookingSegment.check_in_status == 'checked_in'
    #                 )
    #             ).all()
    #             checked_in_segments.extend(segments)
            
    #         if not checked_in_segments:
    #             return {
    #                 "status": "error",
    #                 "message": "No checked-in flights found for this email"
    #             }
            
    #         # Send boarding passes for all checked-in flights
    #         sent_passes = []
    #         for segment in checked_in_segments:
    #             flight = segment.flight
    #             booking = segment.booking
                
    #             # Only send for future flights
    #             if flight.scheduled_departure > datetime.now():
    #                 sent_passes.append({
    #                     "flight_number": flight.flight_number,
    #                     "booking_reference": booking.booking_reference,
    #                     "departure": flight.scheduled_departure.isoformat(),
    #                     "seat": segment.seat_number
    #                 })
            
    #         return {
    #             "status": "success",
    #             "email": email,
    #             "passenger_name": f"{passenger.first_name} {passenger.last_name}",
    #             "boarding_passes_sent": len(sent_passes),
    #             "flights": sent_passes,
    #             "sent_timestamp": datetime.now().isoformat(),
    #             "message": f"Boarding passes resent to {email}",
    #             "delivery_time": "Usually delivered within 5 minutes"
    #         }
            
    #     except Exception as e:
    #         return {"status": "error", "message": f"Boarding pass resend failed: {str(e)}"}

class CheckInInfoService:
    @staticmethod
    async def get_check_in_info(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get check-in information for airport or airline"""
        try:
            airport = params.get('airport')
            airline = params.get('airline', 'HopJetAir')
            travel_date = params.get('travel_date')
            
            # General check-in information
            checkin_info = {
                "airline": airline,
                "airport": airport,
                "online_checkin": {
                    "available": True,
                    "opens": "24 hours before departure",
                    "closes_domestic": "1 hour before departure",
                    "closes_international": "2 hours before departure",
                    "website": "https://hopjetair.com/checkin",
                    "mobile_app": "HopJetAir Mobile App"
                },
                "airport_checkin": {
                    "kiosk_locations": [
                        "Terminal 1 - Near Gate A1-A20",
                        "Terminal 2 - Main concourse",
                        "Terminal 3 - Departures level"
                    ],
                    "counter_hours": {
                        "domestic": "Opens 3 hours before first departure",
                        "international": "Opens 4 hours before first departure",
                        "closes": "45 minutes before departure"
                    }
                },
                "required_documents": {
                    "domestic": ["Government-issued photo ID"],
                    "international": ["Valid passport", "Visa if required", "Return/onward ticket"]
                },
                "baggage_info": {
                    "drop_off_deadline_domestic": "45 minutes before departure",
                    "drop_off_deadline_international": "60 minutes before departure",
                    "oversized_baggage": "Check with airline counter"
                }
            }
            
            # Airport-specific information
            if airport:
                airport_obj = db.query(Airport).filter(
                    or_(
                        Airport.iata_code == airport,
                        Airport.name.ilike(f"%{airport}%")
                    )
                ).first()
                
                if airport_obj:
                    checkin_info["airport_details"] = {
                        "name": airport_obj.name,
                        "code": airport_obj.iata_code,
                        "city": airport_obj.city,
                        "country": airport_obj.country,
                        "timezone": airport_obj.timezone
                    }
                    
                    # Simulate terminal-specific info
                    if airport_obj.iata_code in ['JFK', 'LAX', 'LHR']:
                        checkin_info["terminal_info"] = {
                            "hopjetair_terminal": "Terminal 1",
                            "checkin_counters": "Counters 101-120",
                            "security_wait_times": "15-30 minutes typical"
                        }
            
            return {
                "status": "success",
                "check_in_information": checkin_info,
                "tips": [
                    "Check in online to save time at airport",
                    "Arrive early during peak travel times",
                    "Have documents ready for quick processing",
                    "Check current security wait times online"
                ]
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Check-in info retrieval failed: {str(e)}"}
    
    @staticmethod
    async def query_airport_checkin_info(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query specific airport check-in information"""
        try:
            airport_code = params.get('airport_code')
            info_requested = params.get('info_requested', ['check-in counters', 'baggage drop-off timings'])
            
            airport = db.query(Airport).filter_by(iata_code=airport_code).first()
            if not airport:
                return {"status": "error", "message": f"Airport {airport_code} not found"}
            
            airport_info = {
                "airport": {
                    "code": airport.iata_code,
                    "name": airport.name,
                    "city": airport.city,
                    "country": airport.country
                }
            }
            
            # Provide requested information
            for info_type in info_requested:
                if 'check-in' in info_type.lower() or 'counter' in info_type.lower():
                    airport_info["check_in_counters"] = {
                        "hopjetair_counters": "101-120",
                        "location": "Terminal 1, Departures Level",
                        "hours": "4:00 AM - 11:00 PM daily",
                        "peak_hours": "6:00 AM - 9:00 AM, 3:00 PM - 7:00 PM",
                        "services": [
                            "Check-in and seat selection",
                            "Baggage drop-off",
                            "Special assistance requests",
                            "Group bookings"
                        ]
                    }
                
                if 'baggage' in info_type.lower():
                    airport_info["baggage_services"] = {
                        "drop_off_locations": [
                            "Check-in counters 101-120",
                            "Self-service kiosks Terminal 1"
                        ],
                        "cutoff_times": {
                            "domestic": "45 minutes before departure",
                            "international": "60 minutes before departure"
                        },
                        "oversized_baggage": {
                            "location": "Special services counter 150",
                            "hours": "5:00 AM - 10:00 PM"
                        },
                        "baggage_claim": {
                            "carousels": "1-8",
                            "location": "Arrivals level"
                        }
                    }
                
                if 'timing' in info_type.lower() or 'hours' in info_type.lower():
                    airport_info["operating_hours"] = {
                        "check_in_opens": "4 hours before first departure",
                        "check_in_closes": "45 minutes before departure (domestic), 60 minutes (international)",
                        "security_checkpoint": "4:30 AM - 11:30 PM",
                        "customer_service": "24/7 for emergencies"
                    }
                
                if 'security' in info_type.lower():
                    airport_info["security_information"] = {
                        "checkpoint_locations": ["Terminal 1 Level 2", "Terminal 2 Level 2"],
                        "current_wait_time": f"{random.randint(5, 25)} minutes",
                        "peak_times": "6:00 AM - 9:00 AM, 4:00 PM - 7:00 PM",
                        "tsa_precheck": "Available at Checkpoint A",
                        "prohibited_items": "Visit TSA.gov for complete list"
                    }
            
            # Add general airport facilities
            airport_info["facilities"] = {
                "wifi": "Free WiFi available throughout terminal",
                "dining": "15+ restaurants and cafes",
                "shopping": "Duty-free and retail stores",
                "parking": "Short-term and long-term options available",
                "transportation": ["Taxi", "Ride-share", "Public transit", "Rental cars"]
            }
            
            return {
                "status": "success",
                "airport_information": airport_info,
                "last_updated": datetime.now().isoformat(),
                "contact_info": {
                    "airport_services": "+1-800-AIRPORT",
                    "hopjetair_counter": "+1-800-HOPJET-1"
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Airport info query failed: {str(e)}"}
    
    # @staticmethod
    # async def get_airline_checkin_baggage_info(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
    #     """Get airline-specific check-in and baggage information"""
    #     try:
    #         airline = params.get('airline', 'HopJetAir')
            
    #         # Get airline from database
    #         airline_obj = db.query(Airline).filter(
    #             or_(
    #                 Airline.name.ilike(f"%{airline}%"),
    #                 Airline.iata_code == airline
    #             )
    #         ).first()
            
    #         if not airline_obj:
    #             airline_obj = db.query(Airline).filter_by(name='HopJetAir').first()
            
    #         airline_info = {
    #             "airline": {
    #                 "name": airline_obj.name if airline_obj else airline,
    #                 "code": airline_obj.iata_code if airline_obj else "HJ",
    #                 "alliance": airline_obj.alliance if airline_obj else "Star Alliance"
    #             },
    #             "check_in_policies": {
    #                 "online_checkin": {
    #                     "opens": "24 hours before departure",
    #                     "closes_domestic": "1 hour before departure",
    #                     "closes_international": "2 hours before departure",
    #                     "seat_selection": "Included for all passengers",
    #                     "mobile_boarding_pass": "Available"
    #                 },
    #                 "airport_checkin": {
    #                     "recommended_arrival_domestic": "2 hours before departure",
    #                     "recommended_arrival_international": "3 hours before departure",
    #                     "check_in_closes": "45 minutes before departure",
    #                     "bag_drop_deadline": "45 minutes before departure"
    #                 }
    #             },
    #             "baggage_allowance": {
    #                 "carry_on": {
    #                     "economy": {"pieces": 1, "weight": "10kg", "size": "56x45x25 cm"},
    #                     "business": {"pieces": 2, "weight": "10kg each", "size": "56x45x25 cm"},
    #                     "first": {"pieces": 2, "weight": "10kg each", "size": "56x45x25 cm"}
    #                 },
    #                 "checked_baggage": {
    #                     "economy_domestic": {"pieces": 1, "weight": "23kg", "fee": "$35"},
    #                     "economy_international": {"pieces": 1, "weight": "23kg", "fee": "Included"},
    #                     "business": {"pieces": 2, "weight": "32kg each", "fee": "Included"},
    #                     "first": {"pieces": 2, "weight": "32kg each", "fee": "Included"}
    #                 },
    #                 "excess_baggage": {
    #                     "overweight_fee": "$25 per kg",
    #                     "oversized_fee": "$100 per bag",
    #                     "additional_bag": "$75-150 depending on route"
    #                 }
    #             },
    #             "special_services": {
    #                 "special_assistance": "Available - request during booking or 48 hours in advance",
    #                 "unaccompanied_minors": "Ages 5-17, additional fees apply",
    #                 "pet_travel": "In-cabin and cargo options available",
    #                 "sports_equipment": "Special handling available with advance notice"
    #             }
    #         }
            
    #         return {
    #             "status": "success",
    #             "airline_information": airline_info,
    #             "contact_info": {
    #                 "customer_service": "1-800-HOPJET-1",
    #                 "special_assistance": "1-800-HOPJET-2",
    #                 "baggage_services": "1-800-HOPJET-3"
    #             },
    #             "useful_links": {
    #                 "online_checkin": "https://hopjetair.com/checkin",
    #                 "manage_booking": "https://hopjetair.com/manage",
    #                 "baggage_calculator": "https://hopjetair.com/baggage"
    #             }
    #         }
            
    #     except Exception as e:
    #         return {"status": "error", "message": f"Airline info retrieval failed: {str(e)}"}

