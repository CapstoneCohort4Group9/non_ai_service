from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
import random
import string
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from .database_models import *
from .database_connection import DatabaseError, BookingNotFoundError, FlightNotFoundError, PassengerNotFoundError

class CustomerSupportService:
    @staticmethod
    async def escalate_to_human_agent(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate to human customer service agent"""
        try:
            reason = params.get('reason', 'General inquiry')
            booking_ref = params.get('booking_reference')
            phone_number = params.get('phone_number', params.get('callback_number'))
            preferred_time = params.get('preferred_time', 'anytime')
            name = params.get('name', 'Customer')
            preferred_channel = params.get('preferred_channel', 'phone')
            
            # Generate case number
            case_number = f"CS{random.randint(100000, 999999)}"
            
            # Create customer service log
            cs_log = CustomerServiceLog(
                booking_reference=booking_ref,
                interaction_type='escalation',
                agent_id='SYSTEM',
                summary=f"Escalation request: {reason}",
                status='open'
            )
            db.add(cs_log)
            db.commit()
            
            # Determine priority and estimated wait time
            high_priority_keywords = ['urgent', 'emergency', 'cancelled', 'stranded', 'medical', 'missed flight']
            priority = 'high' if any(word in reason.lower() for word in high_priority_keywords) else 'normal'
            
            if priority == 'high':
                estimated_wait = "5-10 minutes"
                callback_time = "Within 15 minutes"
            else:
                estimated_wait = "15-20 minutes"
                callback_time = "Within 1 hour"
            
            # Determine department based on reason
            department = "General Support"
            if any(word in reason.lower() for word in ['refund', 'compensation', 'money']):
                department = "Refunds & Compensation"
            elif any(word in reason.lower() for word in ['booking', 'reservation', 'change']):
                department = "Reservations"
            elif any(word in reason.lower() for word in ['baggage', 'luggage']):
                department = "Baggage Services"
            elif any(word in reason.lower() for word in ['medical', 'emergency', 'assistance']):
                department = "Emergency Services"
            
            return {
                "status": "success",
                "case_number": case_number,
                "message": "Your request has been escalated to a human agent",
                "escalation_details": {
                    "priority": priority,
                    "department": department,
                    "estimated_wait_time": estimated_wait,
                    "case_created": datetime.now().isoformat()
                },
                "contact_options": {
                    "phone": "1-800-HOPJET-1 (1-800-467-5381)",
                    "chat": "Available on hopjetair.com",
                    "email": "support@hopjetair.com",
                    "emergency": "1-800-EMERGENCY (24/7)"
                },
                "callback_info": {
                    "callback_scheduled": bool(phone_number),
                    "callback_number": phone_number if phone_number else None,
                    "callback_time": preferred_time if phone_number else None,
                    "estimated_callback": callback_time if phone_number else None
                },
                "next_steps": [
                    "An agent will contact you shortly" if phone_number else "Please call the number above or use chat",
                    "Have your booking reference ready",
                    "Prepare any relevant documentation",
                    "Check your email for case number confirmation"
                ],
                "business_hours": {
                    "general_support": "6 AM - 11 PM EST",
                    "emergency_support": "24/7",
                    "chat_support": "24/7",
                    "phone_support": "24/7 for emergencies, 6 AM - 11 PM EST for general inquiries"
                },
                "self_service_options": [
                    "Check flight status online",
                    "Manage bookings through mobile app",
                    "Access FAQ for common questions",
                    "Use online check-in"
                ]
            }
            
        except Exception as e:
            db.rollback()
            return {
                "status": "error",
                "message": f"Escalation failed: {str(e)}"
            }
    
    @staticmethod
    async def schedule_callback(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a callback from customer service"""
        try:
            phone_number = params.get('phone_number')
            booking_ref = params.get('booking_reference')
            purpose = params.get('purpose', 'General inquiry')
            preferred_time = params.get('preferred_time', 'anytime')
            
            if not phone_number:
                return {"status": "error", "message": "Phone number required for callback"}
            
            # Generate callback reference
            callback_ref = f"CB{random.randint(100000, 999999)}"
            
            # Determine callback slot
            now = datetime.now()
            if preferred_time.lower() == 'anytime':
                callback_time = now + timedelta(hours=1)
            elif 'morning' in preferred_time.lower():
                callback_time = now.replace(hour=9, minute=0) + timedelta(days=1 if now.hour >= 12 else 0)
            elif 'afternoon' in preferred_time.lower():
                callback_time = now.replace(hour=14, minute=0) + timedelta(days=1 if now.hour >= 17 else 0)
            elif 'evening' in preferred_time.lower():
                callback_time = now.replace(hour=19, minute=0) + timedelta(days=1 if now.hour >= 21 else 0)
            else:
                callback_time = now + timedelta(hours=2)
            
            return {
                "status": "success",
                "callback_reference": callback_ref,
                "callback_scheduled": True,
                "callback_details": {
                    "phone_number": phone_number,
                    "scheduled_time": callback_time.isoformat(),
                    "purpose": purpose,
                    "estimated_duration": "10-15 minutes"
                },
                "booking_reference": booking_ref,
                "confirmation_message": f"Callback scheduled successfully. Reference: {callback_ref}",
                "instructions": [
                    "Please be available at the scheduled time",
                    "Have your booking reference ready",
                    "If you miss the call, we'll try once more",
                    "You can reschedule up to 2 hours before the appointment"
                ],
                "contact_info": {
                    "reschedule": "Call 1-800-HOPJET to reschedule",
                    "cancel": "Use callback reference to cancel online"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Callback scheduling failed: {str(e)}"
            }

class PolicyService:
    @staticmethod
    async def query_policy_rag_db(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query airline policies using RAG database"""
        try:
            query_text = params.get('query', '')
            
            # Parse query for keywords
            keywords = query_text.lower().split()
            policy_category = None
            route_type = None
            class_of_service = None
            
            # Detect policy type
            if any(word in keywords for word in ['change', 'modify', 'reschedule', 'switch']):
                policy_category = 'change'
            elif any(word in keywords for word in ['cancel', 'cancellation', 'refund']):
                policy_category = 'cancellation'
            elif any(word in keywords for word in ['baggage', 'bag', 'luggage', 'checked', 'carry-on']):
                policy_category = 'baggage'
            elif any(word in keywords for word in ['fee', 'cost', 'charge', 'price']):
                policy_category = 'fees'
            
            # Detect route type
            if any(word in keywords for word in ['domestic', 'national', 'within']):
                route_type = 'domestic'
            elif any(word in keywords for word in ['international', 'overseas', 'abroad']):
                route_type = 'international'
            
            # Detect class
            if any(word in keywords for word in ['economy', 'coach', 'basic']):
                class_of_service = 'economy'
            elif any(word in keywords for word in ['business', 'premium']):
                class_of_service = 'business'
            elif any(word in keywords for word in ['first', 'luxury']):
                class_of_service = 'first'
            
            # Build query
            query_builder = db.query(AirlinePolicy)
            
            if policy_category:
                query_builder = query_builder.filter(AirlinePolicy.policy_category == policy_category)
            if route_type:
                query_builder = query_builder.filter(AirlinePolicy.route_type == route_type)
            if class_of_service:
                query_builder = query_builder.filter(AirlinePolicy.class_of_service == class_of_service)
            
            policies = query_builder.all()
            
            if not policies:
                # Return general policy information based on keywords
                general_policies = []
                
                if 'baggage' in query_text.lower():
                    general_policies.append({
                        "policy_type": "Baggage Allowance",
                        "description": "Economy passengers receive 1 free checked bag (23kg) on international flights. Domestic flights: $35 for first checked bag.",
                        "conditions": "Bags must not exceed size and weight limits. Additional fees apply for excess baggage."
                    })
                
                if any(word in query_text.lower() for word in ['change', 'cancel']):
                    general_policies.append({
                        "policy_type": "Change and Cancellation",
                        "description": "Changes allowed with fees. Domestic: $75 change fee. International: $200 change fee. Cancellations subject to fare rules.",
                        "conditions": "Changes must be made at least 2 hours before departure. Same-day changes incur double fees."
                    })
                
                if not general_policies:
                    general_policies.append({
                        "policy_type": "General Information",
                        "description": "For specific policy information, please contact customer service at 1-800-HOPJET or visit our website.",
                        "conditions": "Policies may vary based on fare type, route, and booking conditions."
                    })
                
                return {
                    "status": "success",
                    "query": query_text,
                    "policies": general_policies,
                    "suggestion": "Try searching for specific terms like 'baggage allowance', 'change fees', or 'cancellation policy'"
                }
            
            policy_results = []
            for policy in policies:
                policy_info = {
                    "policy_type": policy.policy_type,
                    "category": policy.policy_category,
                    "description": policy.description,
                    "fee_amount": float(policy.fee_amount) if policy.fee_amount else None,
                    "fee_percentage": float(policy.fee_percentage) if policy.fee_percentage else None,
                    "conditions": policy.conditions,
                    "route_type": policy.route_type,
                    "class_of_service": policy.class_of_service,
                    "effective_dates": {
                        "from": policy.effective_from.isoformat() if policy.effective_from else None,
                        "to": policy.effective_to.isoformat() if policy.effective_to else None
                    }
                }
                policy_results.append(policy_info)
            
            return {
                "status": "success",
                "query": query_text,
                "matched_categories": {
                    "policy_category": policy_category,
                    "route_type": route_type,
                    "class_of_service": class_of_service
                },
                "policies": policy_results,
                "total_policies_found": len(policy_results)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Policy query failed: {str(e)}"
            }

class RefundService:
    @staticmethod
    async def initiate_refund(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate refund process"""
        try:
            booking_ref = params.get('booking_reference')
            reason = params.get('reason', params.get('cancellation_reason', 'passenger_request'))
            refund_method = params.get('refund_method', 'credit_card')
            amount = params.get('amount')
            
            # Check for flight booking
            booking = db.query(Booking).filter_by(booking_reference=booking_ref).first()
            trip_booking = db.query(TripBooking).filter_by(booking_reference=booking_ref).first()
            
            if not booking and not trip_booking:
                raise BookingNotFoundError(f"Booking {booking_ref} not found")
            
            main_booking = booking or trip_booking
            booking_type = "flight" if booking else "trip"
            
            # Check if refund already exists
            existing_refund = db.query(Refund).filter(
                or_(
                    Refund.booking_id == main_booking.id,
                    Refund.trip_booking_id == main_booking.id
                )
            ).first()
            
            if existing_refund:
                return {
                    "status": "error",
                    "message": f"Refund already initiated. Reference: {existing_refund.refund_reference}"
                }
            
            # Calculate refund amount based on cancellation policy
            refund_amount = amount if amount else main_booking.total_amount
            refund_type = 'full'
            cancellation_fee = Decimal('0')
            
            # Check timing for fees (only for future bookings)
            if booking_type == "flight":
                segments = db.query(BookingSegment).filter_by(booking_id=main_booking.id).all()
                if segments:
                    earliest_departure = min(segment.flight.scheduled_departure for segment in segments)
                    time_to_departure = earliest_departure - datetime.now()
                    
                    if time_to_departure.days < 0:
                        return {
                            "status": "error",
                            "message": "Cannot refund past flights. Please contact customer service for assistance."
                        }
                    elif time_to_departure.days < 1:
                        cancellation_fee = main_booking.total_amount * Decimal('0.5')
                        refund_type = 'partial'
                    elif time_to_departure.days < 7:
                        cancellation_fee = Decimal('200')
                        refund_type = 'partial'
                    elif time_to_departure.days < 30:
                        cancellation_fee = Decimal('100')
                        refund_type = 'partial'
            else:  # trip booking
                time_to_trip = main_booking.travel_start_date - datetime.now().date()
                if time_to_trip.days < 0:
                    return {
                        "status": "error", 
                        "message": "Cannot refund past trips. Please contact customer service for assistance."
                    }
                elif time_to_trip.days < 7:
                    cancellation_fee = main_booking.total_amount * Decimal('0.5')
                    refund_type = 'partial'
                elif time_to_trip.days < 30:
                    cancellation_fee = Decimal('300')
                    refund_type = 'partial'
            
            refund_amount = main_booking.total_amount - cancellation_fee
            
            # Generate refund reference
            refund_ref = f"RF{random.randint(100000, 999999)}"
            
            # Create refund record
            refund = Refund(
                booking_id=main_booking.id if booking else None,
                trip_booking_id=main_booking.id if trip_booking else None,
                refund_reference=refund_ref,
                refund_type=refund_type,
                amount=refund_amount,
                reason=reason,
                status='pending',
                refund_method=refund_method
            )
            db.add(refund)
            
            # Update booking status
            main_booking.status = 'refund_requested'
            db.commit()
            
            processing_time_map = {
                'credit_card': "3-5 business days",
                'bank_transfer': "7-10 business days", 
                'travel_credit': "1-2 business days"
            }
            processing_time = processing_time_map.get(refund_method, "5-7 business days")
            
            return {
                "status": "success",
                "refund_reference": refund_ref,
                "booking_reference": booking_ref,
                "booking_type": booking_type,
                "refund_details": {
                    "original_amount": float(main_booking.total_amount),
                    "cancellation_fee": float(cancellation_fee),
                    "refund_amount": float(refund_amount),
                    "refund_type": refund_type,
                    "refund_method": refund_method
                },
                "processing_info": {
                    "status": "pending_approval",
                    "processing_time": processing_time,
                    "approval_time": "24-48 hours"
                },
                "confirmation_message": f"Refund initiated successfully. Reference: {refund_ref}",
                "next_steps": [
                    "You will receive email confirmation within 24 hours",
                    "Refund will be processed after approval",
                    f"Funds will be returned via {refund_method}",
                    "Contact customer service if you have questions"
                ],
                "policy_applied": {
                    "same_day_cancellation": "50% fee applies",
                    "within_week": "$200-300 fee applies", 
                    "within_month": "$100 fee applies",
                    "advance_cancellation": "No fee"
                }
            }
            
        except BookingNotFoundError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            db.rollback()
            return {
                "status": "error",
                "message": f"Refund initiation failed: {str(e)}"
            }
    
    @staticmethod
    async def check_refund_eligibility(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check if booking is eligible for refund"""
        try:
            booking_ref = params.get('booking_reference')
            
            booking = db.query(Booking).filter_by(booking_reference=booking_ref).first()
            if not booking:
                return {"status": "error", "message": f"Booking {booking_ref} not found"}
            
            # Check current status
            if booking.status in ['cancelled', 'refunded']:
                return {
                    "status": "success",
                    "eligible": False,
                    "reason": f"Booking already {booking.status}"
                }
            
            # Check if flights have already departed
            segments = db.query(BookingSegment).filter_by(booking_id=booking.id).all()
            if segments:
                earliest_departure = min(segment.flight.scheduled_departure for segment in segments)
                if earliest_departure < datetime.now():
                    return {
                        "status": "success",
                        "eligible": False,
                        "reason": "Flight has already departed"
                    }
                
                # Calculate potential refund
                time_to_departure = earliest_departure - datetime.now()
                if time_to_departure.days < 1:
                    fee_percentage = 50
                    fee_amount = booking.total_amount * Decimal('0.5')
                elif time_to_departure.days < 7:
                    fee_percentage = 0
                    fee_amount = Decimal('200')
                elif time_to_departure.days < 30:
                    fee_percentage = 0
                    fee_amount = Decimal('100')
                else:
                    fee_percentage = 0
                    fee_amount = Decimal('0')
                
                refund_amount = booking.total_amount - fee_amount
                
                return {
                    "status": "success",
                    "eligible": True,
                    "refund_details": {
                        "original_amount": float(booking.total_amount),
                        "cancellation_fee": float(fee_amount),
                        "fee_percentage": fee_percentage,
                        "refund_amount": float(refund_amount),
                        "refund_percentage": float((refund_amount / booking.total_amount) * 100)
                    },
                    "time_to_departure": {
                        "days": time_to_departure.days,
                        "hours": time_to_departure.seconds // 3600
                    },
                    "policy_notes": [
                        "Refund amount depends on timing of cancellation",
                        "Same-day cancellations incur 50% fee",
                        "Week-before cancellations incur $200 fee",
                        "Month-before cancellations incur $100 fee"
                    ]
                }
            
            return {
                "status": "success",
                "eligible": True,
                "refund_amount": float(booking.total_amount),
                "no_fees": "No flights found or special circumstances"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Refund eligibility check failed: {str(e)}"
            }

class BaggageService:
    @staticmethod
    async def check_baggage_allowance(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check baggage allowance for booking"""
        try:
            booking_ref = params.get('booking_reference')
            airline = params.get('airline', 'HopJetAir')
            class_of_service = params.get('classname', 'economy')
            route_type = params.get('route_type', 'international')
            departure = params.get('departure', params.get('origin'))
            destination = params.get('destination')
            
            # Determine route type if not provided
            if departure and destination and not route_type:
                # Simple logic: if both are US airports, it's domestic
                us_airports = ['JFK', 'LAX', 'ORD', 'DFW', 'ATL', 'MIA', 'SEA', 'BOS']
                if departure in us_airports and destination in us_airports:
                    route_type = 'domestic'
                else:
                    route_type = 'international'
            
            # Define comprehensive baggage policies
            baggage_policies = {
                'economy': {
                    'domestic': {
                        'carry_on': {
                            'pieces': 1,
                            'weight_kg': 10,
                            'dimensions': '56x45x25 cm',
                            'fee': 0,
                            'description': 'One carry-on bag plus personal item'
                        },
                        'checked': {
                            'pieces': 0,
                            'weight_kg': 23,
                            'dimensions': '158 cm total',
                            'fee': 35,
                            'description': 'First checked bag fee applies'
                        },
                        'personal_item': {
                            'pieces': 1,
                            'weight_kg': 5,
                            'dimensions': '40x30x15 cm',
                            'fee': 0,
                            'description': 'Small bag that fits under seat'
                        }
                    },
                    'international': {
                        'carry_on': {
                            'pieces': 1,
                            'weight_kg': 10,
                            'dimensions': '56x45x25 cm',
                            'fee': 0,
                            'description': 'One carry-on bag plus personal item'
                        },
                        'checked': {
                            'pieces': 1,
                            'weight_kg': 23,
                            'dimensions': '158 cm total',
                            'fee': 0,
                            'description': 'One free checked bag included'
                        },
                        'personal_item': {
                            'pieces': 1,
                            'weight_kg': 5,
                            'dimensions': '40x30x15 cm',
                            'fee': 0,
                            'description': 'Small bag that fits under seat'
                        }
                    }
                },
                'business': {
                    'domestic': {
                        'carry_on': {
                            'pieces': 2,
                            'weight_kg': 10,
                            'dimensions': '56x45x25 cm',
                            'fee': 0,
                            'description': 'Two carry-on bags plus personal item'
                        },
                        'checked': {
                            'pieces': 2,
                            'weight_kg': 32,
                            'dimensions': '158 cm total',
                            'fee': 0,
                            'description': 'Two free checked bags'
                        },
                        'personal_item': {
                            'pieces': 1,
                            'weight_kg': 8,
                            'dimensions': '40x30x20 cm',
                            'fee': 0,
                            'description': 'Premium personal item allowance'
                        }
                    },
                    'international': {
                        'carry_on': {
                            'pieces': 2,
                            'weight_kg': 10,
                            'dimensions': '56x45x25 cm',
                            'fee': 0,
                            'description': 'Two carry-on bags plus personal item'
                        },
                        'checked': {
                            'pieces': 2,
                            'weight_kg': 32,
                            'dimensions': '158 cm total',
                            'fee': 0,
                            'description': 'Two free checked bags'
                        },
                        'personal_item': {
                            'pieces': 1,
                            'weight_kg': 8,
                            'dimensions': '40x30x20 cm',
                            'fee': 0,
                            'description': 'Premium personal item allowance'
                        }
                    }
                }
            }
            
            policy = baggage_policies.get(class_of_service, baggage_policies['economy'])
            route_policy = policy.get(route_type, policy['international'])
            
            # If booking reference provided, get specific passenger details
            booking_specific = {}
            tier_benefits = {}
            
            if booking_ref:
                booking = db.query(Booking).filter_by(booking_reference=booking_ref).first()
                if booking:
                    passenger = booking.passenger
                    tier_multipliers = {
                        'basic': 1,
                        'silver': 1.2,
                        'gold': 1.5,
                        'platinum': 2
                    }
                    
                    tier_multiplier = tier_multipliers.get(passenger.tier_status, 1)
                    
                    # Apply tier benefits
                    if passenger.tier_status != 'basic':
                        enhanced_policy = route_policy.copy()
                        enhanced_policy['checked']['pieces'] = min(3, int(route_policy['checked']['pieces'] * tier_multiplier))
                        enhanced_policy['checked']['weight_kg'] = min(45, int(route_policy['checked']['weight_kg'] * tier_multiplier))
                        route_policy = enhanced_policy
                        
                        tier_benefits = {
                            "tier_status": passenger.tier_status,
                            "benefits_applied": True,
                            "additional_bags": enhanced_policy['checked']['pieces'] - baggage_policies[class_of_service][route_type]['checked']['pieces'],
                            "weight_bonus": enhanced_policy['checked']['weight_kg'] - baggage_policies[class_of_service][route_type]['checked']['weight_kg']
                        }
                    
                    booking_specific = {
                        "passenger_name": f"{passenger.first_name} {passenger.last_name}",
                        "passenger_tier": passenger.tier_status,
                        "frequent_flyer": passenger.frequent_flyer_number
                    }
            
            return {
                "status": "success",
                "airline": airline,
                "flight_details": {
                    "class_of_service": class_of_service,
                    "route_type": route_type,
                    "departure": departure,
                    "destination": destination
                },
                "baggage_allowance": route_policy,
                "tier_benefits": tier_benefits,
                "booking_specific": booking_specific,
                "excess_baggage_fees": {
                    "overweight_fee_per_kg": 25,
                    "oversized_fee": 100,
                    "additional_bag_fee": 75,
                    "weight_limit_exceeded": "Bags over 32kg not accepted"
                },
                "restricted_items": [
                    "Liquids over 100ml in carry-on",
                    "Sharp objects and tools",
                    "Flammable materials",
                    "Lithium batteries over 100Wh",
                    "Sports equipment (special handling required)"
                ],
                "packing_tips": [
                    "Weigh bags before arriving at airport",
                    "Pack liquids in clear, resealable bags",
                    "Keep valuables and medications in carry-on",
                    "Label bags with contact information",
                    "Check airline website for latest restrictions"
                ],
                "special_items": {
                    "sports_equipment": "Additional fees may apply",
                    "musical_instruments": "Can be carried on or checked with special handling",
                    "medical_equipment": "Free allowance with proper documentation",
                    "infant_items": "Strollers and car seats travel free"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Baggage allowance check failed: {str(e)}"
            }

class PricingService:
    @staticmethod
    async def search_flight_prices(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search and compare flight prices"""
        try:
            origin = params.get('origin', 'Chicago')
            destination = params.get('destination', 'Madrid')
            departure_date = params.get('departure_date')
            return_date = params.get('return_date')
            passengers = params.get('passengers', {'adults': 1})
            cabin_class = params.get('cabin_classname', params.get('travel_classname', 'economy'))
            trip_type = params.get('trip_type', 'roundtrip')
            
            # Generate realistic price data based on route and timing
            base_prices = {
                'economy': random.randint(300, 800),
                'premium_economy': random.randint(600, 1200),
                'business': random.randint(1200, 2500),
                'first': random.randint(2500, 5000)
            }
            
            # Adjust prices based on date proximity and seasonality
            if departure_date:
                try:
                    dep_date = datetime.strptime(departure_date, '%Y-%m-%d')
                    days_ahead = (dep_date - datetime.now()).days
                    
                    # Price increases as date approaches
                    if days_ahead < 14:
                        multiplier = 1.5
                    elif days_ahead < 30:
                        multiplier = 1.2
                    elif days_ahead < 60:
                        multiplier = 1.0
                    else:
                        multiplier = 0.9
                    
                    # Seasonal adjustment
                    month = dep_date.month
                    if month in [6, 7, 8, 12]:  # Peak season
                        multiplier *= 1.3
                    elif month in [1, 2, 11]:  # Low season
                        multiplier *= 0.8
                    
                    base_prices = {k: int(v * multiplier) for k, v in base_prices.items()}
                except:
                    pass
            
            # Generate multiple price options from different "airlines"
            airlines = ['HopJetAir', 'American Airlines', 'Delta Air Lines', 'United Airlines', 'British Airways']
            price_options = []
            
            for i, airline in enumerate(airlines):
                for class_type, base_price in base_prices.items():
                    if cabin_class != 'all' and class_type != cabin_class:
                        continue
                        
                    # Add some price variation between airlines
                    price_variation = random.uniform(0.85, 1.15)
                    final_price = int(base_price * price_variation)
                    
                    # Calculate total for all passengers
                    adult_count = passengers.get('adults', 1) if isinstance(passengers, dict) else 1
                    child_count = passengers.get('children', 0) if isinstance(passengers, dict) else 0
                    infant_count = passengers.get('infants', 0) if isinstance(passengers, dict) else 0
                    
                    total_price = (final_price * adult_count + 
                                 final_price * 0.75 * child_count + 
                                 final_price * 0.1 * infant_count)
                    
                    # Add return flight cost for round trips
                    if trip_type == 'roundtrip' and return_date:
                        total_price *= 2
                    
                    price_option = {
                        "airline": airline,
                        "class": class_type,
                        "price_per_person": final_price,
                        "total_price": int(total_price),
                        "currency": "USD",
                        "availability": random.choice([True, True, True, False]),  # 75% available
                        "refundable": class_type in ['business', 'first'],
                        "changes_allowed": True,
                        "change_fee": 75 if class_type == 'economy' else 0,
                        "baggage_included": class_type != 'economy',
                        "flight_duration": f"{random.randint(8, 15)}h {random.randint(0, 59)}m",
                        "stops": random.choice([0, 1]) if airline != 'HopJetAir' else 0,
                        "booking_class": random.choice(['Y', 'B', 'M', 'H']) if class_type == 'economy' else class_type[0].upper()
                    }
                    
                    # Add special offers
                    if random.random() < 0.3:  # 30% chance of special offer
                        offer_types = ['Early Bird', 'Weekend Special', 'Last Minute', 'Group Discount']
                        price_option["special_offer"] = {
                            "type": random.choice(offer_types),
                            "discount": random.choice([10, 15, 20, 25]),
                            "conditions": "Limited time offer"
                        }
                        price_option["original_price"] = price_option["total_price"]
                        price_option["total_price"] = int(price_option["total_price"] * 0.85)
                    
                    price_options.append(price_option)
            
            # Sort by total price
            price_options.sort(key=lambda x: x['total_price'])
            
            return {
                "status": "success",
                "search_criteria": {
                    "origin": origin,
                    "destination": destination,
                    "departure_date": departure_date,
                    "return_date": return_date,
                    "passengers": passengers,
                    "cabin_class": cabin_class,
                    "trip_type": trip_type
                },
                "price_options": price_options[:15],  # Return top 15 options
                "price_analysis": {
                    "lowest_price": price_options[0]["total_price"] if price_options else 0,
                    "highest_price": price_options[-1]["total_price"] if price_options else 0,
                    "average_price": sum(opt["total_price"] for opt in price_options) // len(price_options) if price_options else 0,
                    "price_range": "Moderate" if departure_date else "Variable"
                },
                "booking_tips": [
                    "Book Tuesday-Thursday for best domestic deals",
                    "International flights: book 6-8 weeks in advance",
                    "Consider nearby airports for additional savings", 
                    "Flexible dates can save up to 30%",
                    "Clear browser cookies between searches"
                ],
                "price_alerts": {
                    "available": True,
                    "notification_methods": ["email", "SMS", "app"],
                    "price_drop_threshold": "10% or $50"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Price search failed: {str(e)}"
            }