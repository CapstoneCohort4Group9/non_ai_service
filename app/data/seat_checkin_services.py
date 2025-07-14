from datetime import datetime, date, timedelta
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
            near_exit = params.get('near_exit', False)
            
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
            
            # Apply filters
            if seat_preference and seat_preference != 'any':
                seat_map_query = seat_map_query.filter(SeatMap.seat_type == seat_preference)
            
            if near_exit:
                seat_map_query = seat_map_query.filter(SeatMap.is_exit_row == True)
            
            seat_map = seat_map_query.all()
            
            # Get occupied seats
            occupied_seats = db.query(FlightSeat).filter_by(
                flight_id=flight.id
            ).filter(FlightSeat.status == 'occupied').all()
            
            occupied_seat_numbers = {seat.seat_number for seat in occupied_seats}
            
            # Organize available seats by class and type
            available_seats = {
                'economy': {'window': [], 'aisle': [], 'middle': []},
                'business': {'window': [], 'aisle': [], 'middle': []},
                'first': {'window': [], 'aisle': [], 'middle': []}
            }
            
            for seat in seat_map:
                if seat.seat_number not in occupied_seat_numbers and not seat.is_blocked:
                    seat_fee = 0
                    if seat.extra_legroom:
                        seat_fee = 25
                    elif seat.class_of_service != 'economy':
                        seat_fee = 50
                    elif seat.is_exit_row:
                        seat_fee = 15
                    
                    seat_info = {
                        'seat_number': seat.seat_number,
                        'seat_type': seat.seat_type,
                        'extra_legroom': seat.extra_legroom,
                        'exit_row': seat.is_exit_row,
                        'fee': seat_fee,
                        'class': seat.class_of_service
                    }
                    
                    if seat.class_of_service in available_seats:
                        if seat.seat_type in available_seats[seat.class_of_service]:
                            available_seats[seat.class_of_service][seat.seat_type].append(seat_info)
            
            # Calculate totals
            total_available = sum(
                len(seats) for class_seats in available_seats.values() 
                for seats in class_seats.values()
            )
            
            return {
                "status": "success",
                "flight_number": flight.flight_number,
                "aircraft_type": f"{aircraft_type.manufacturer} {aircraft_type.model}",
                "passenger_class": segment.class_of_service,
                "current_seat": segment.seat_number,
                "available_seats": available_seats,
                "total_available": total_available,
                "seat_preferences": {
                    "window_available": len(available_seats['economy']['window']) > 0,
                    "aisle_available": len(available_seats['economy']['aisle']) > 0,
                    "exit_row_available": any(seat['exit_row'] for class_seats in available_seats.values() for seats in class_seats.values() for seat in seats),
                    "extra_legroom_available": any(seat['extra_legroom'] for class_seats in available_seats.values() for seats in class_seats.values() for seat in seats)
                },
                "seat_map_url": f"https://hopjetair.com/seat-map/{flight.id}"
            }
            
        except BookingNotFoundError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Seat availability check failed: {str(e)}"
            }
    
    @staticmethod
    async def change_seat(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Change passenger seat assignment"""
        try:
            booking_ref = params.get('booking_reference')
            new_seat = params.get('new_seat', params.get('seat_number'))
            
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
            
            # Check seat map for validation and fees
            seat_map_entry = db.query(SeatMap).filter_by(
                aircraft_type_id=flight.aircraft.aircraft_type.id,
                seat_number=new_seat
            ).first()
        