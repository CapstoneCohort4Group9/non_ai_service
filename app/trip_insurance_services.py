from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
import random
import string
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from .database_models import *
from .database_connection import DatabaseError, BookingNotFoundError, FlightNotFoundError, PassengerNotFoundError

class TripPackageService:
    @staticmethod
    async def search_trip(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for trip packages"""
        try:
            destination = params.get('destination', 'Madrid')
            budget = params.get('budget', params.get('budget_max', params.get('max_budget', 1500)))
            interests = params.get('interests', params.get('activities', []))
            duration_days = params.get('duration_days', params.get('duration_nights', params.get('trip_length_days', 5)))
            origin = params.get('origin', 'New York')
            departure_date = params.get('departure_date')
            
            # Build query
            query = db.query(TripPackage)
            
            if destination:
                query = query.filter(
                    or_(
                        TripPackage.destination_city.ilike(f"%{destination}%"),
                        TripPackage.destination_country.ilike(f"%{destination}%")
                    )
                )
            
            if budget:
                query = query.filter(TripPackage.price_per_person <= budget)
            
            if duration_days:
                # Allow some flexibility in duration
                query = query.filter(
                    TripPackage.duration_days.between(duration_days - 2, duration_days + 2)
                )
            
            packages = query.all()
            
            # Score packages based on interests
            scored_packages = []
            for package in packages:
                score = 0
                if interests:
                    for interest in interests:
                        if interest.lower() in package.description.lower():
                            score += 1
                        if interest.lower() in package.category.lower():
                            score += 2
                        if interest.lower() in package.name.lower():
                            score += 3
                
                # Calculate total price including estimated flight cost
                flight_cost = random.randint(400, 1200)  # Estimated flight cost
                total_price = float(package.price_per_person)
                if package.includes_flight:
                    estimated_total = total_price
                else:
                    estimated_total = total_price + flight_cost
                
                package_info = {
                    "package_code": package.package_code,
                    "name": package.name,
                    "description": package.description,
                    "destination": {
                        "city": package.destination_city,
                        "country": package.destination_country
                    },
                    "duration_days": package.duration_days,
                    "price_per_person": total_price,
                    "estimated_total_price": estimated_total,
                    "category": package.category,
                    "includes": {
                        "flight": package.includes_flight,
                        "hotel": package.includes_hotel,
                        "activities": package.includes_activities
                    },
                    "match_score": score,
                    "departure_options": [origin] if origin else ["New York", "Los Angeles", "Chicago"],
                    "available_dates": [
                        (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                        (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
                        (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
                    ]
                }
                scored_packages.append(package_info)
            
            # Sort by score and price
            scored_packages.sort(key=lambda x: (-x['match_score'], x['estimated_total_price']))
            
            return {
                "status": "success",
                "search_criteria": {
                    "destination": destination,
                    "budget": budget,
                    "interests": interests,
                    "duration_days": duration_days,
                    "origin": origin
                },
                "packages": scored_packages[:10],  # Top 10 results
                "total_found": len(scored_packages),
                "filters_applied": {
                    "destination_filter": bool(destination),
                    "budget_filter": bool(budget),
                    "duration_filter": bool(duration_days)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Trip search failed: {str(e)}"
            }
    
    @staticmethod
    async def book_trip(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Book a trip package"""
        try:
            package_name = params.get('package', params.get('excursion', 'Madrid Historical Tour'))
            departure_date = params.get('departure_date')
            return_date = params.get('return_date')
            passengers = params.get('passengers', [{'type': 'adult', 'count': 2}])
            travelers = params.get('travelers', params.get('num_passengers', 2))
            
            # Handle different passenger formats
            if isinstance(passengers, list) and passengers:
                if isinstance(passengers[0], dict):
                    total_passengers = sum(p.get('count', 1) for p in passengers)
                else:
                    total_passengers = len(passengers)
            else:
                total_passengers = travelers if isinstance(travelers, int) else 2
            
            # Find package
            package = db.query(TripPackage).filter(
                or_(
                    TripPackage.name.ilike(f"%{package_name}%"),
                    TripPackage.package_code == package_name
                )
            ).first()
            
            if not package:
                # Create a default package for demo
                package = TripPackage(
                    package_code='MAD001',
                    name='Madrid Cultural Explorer',
                    description='Discover the rich history and culture of Madrid with museum tours, flamenco shows, and traditional tapas experiences.',
                    destination_city='Madrid',
                    destination_country='Spain',
                    duration_days=5,
                    price_per_person=Decimal('1299.00'),
                    category='cultural',
                    includes_flight=True,
                    includes_hotel=True,
                    includes_activities=True
                )
                db.add(package)
                db.flush()
            
            # Generate booking reference
            booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            while db.query(TripBooking).filter_by(booking_reference=booking_ref).first():
                booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            
            # Create or find passenger
            passenger = db.query(Passenger).first()  # Simplified for demo
            if not passenger:
                passenger = Passenger(
                    first_name="John",
                    last_name="Doe",
                    email="traveler@example.com",
                    phone="+1-555-0123"
                )
                db.add(passenger)
                db.flush()
            
            # Parse dates
            if departure_date:
                travel_start = datetime.strptime(departure_date, '%Y-%m-%d').date()
            else:
                travel_start = (datetime.now() + timedelta(days=30)).date()
            
            if return_date:
                travel_end = datetime.strptime(return_date, '%Y-%m-%d').date()
            else:
                travel_end = travel_start + timedelta(days=package.duration_days)
            
            # Calculate total amount
            total_amount = package.price_per_person * total_passengers
            
            # Create trip booking
            trip_booking = TripBooking(
                booking_reference=booking_ref,
                passenger_id=passenger.id,
                trip_package_id=package.id,
                travel_start_date=travel_start,
                travel_end_date=travel_end,
                num_passengers=total_passengers,
                total_amount=total_amount,
                status='confirmed'
            )
            db.add(trip_booking)
            db.commit()
            
            return {
                "status": "success",
                "booking_reference": booking_ref,
                "package_name": package.name,
                "destination": f"{package.destination_city}, {package.destination_country}",
                "travel_dates": {
                    "start": travel_start.isoformat(),
                    "end": travel_end.isoformat(),
                    "duration": package.duration_days
                },
                "passengers": total_passengers,
                "total_amount": float(total_amount),
                "currency": "USD",
                "includes": {
                    "flight": package.includes_flight,
                    "hotel": package.includes_hotel,
                    "activities": package.includes_activities
                },
                "booking_details": {
                    "booking_date": datetime.now().isoformat(),
                    "status": "confirmed",
                    "package_code": package.package_code
                },
                "confirmation_message": f"Trip booked successfully! Reference: {booking_ref}",
                "next_steps": [
                    "Check email for detailed itinerary",
                    "Complete passenger information if required",
                    "Review travel documents needed",
                    "Consider travel insurance"
                ]
            }
            
        except Exception as e:
            db.rollback()
            return {
                "status": "error",
                "message": f"Trip booking failed: {str(e)}"
            }
    
    @staticmethod
    async def check_trip_details(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check detailed trip information"""
        try:
            booking_ref = params.get('booking_reference')
            last_name = params.get('last_name')
            
            trip_booking = db.query(TripBooking).filter_by(booking_reference=booking_ref).first()
            if not trip_booking:
                return {"status": "error", "message": f"Trip booking {booking_ref} not found"}
            
            # Verify passenger name if provided
            if last_name and last_name.lower() not in trip_booking.passenger.last_name.lower():
                return {"status": "error", "message": "Passenger name does not match booking"}
            
            package = trip_booking.trip_package
            passenger = trip_booking.passenger
            
            # Get excursions for this trip
            excursions = db.query(ExcursionBooking).filter_by(trip_booking_id=trip_booking.id).all()
            
            trip_details = {
                "booking_reference": booking_ref,
                "passenger_details": {
                    "name": f"{passenger.first_name} {passenger.last_name}",
                    "email": passenger.email,
                    "phone": passenger.phone,
                    "tier_status": passenger.tier_status
                },
                "trip_package": {
                    "name": package.name,
                    "code": package.package_code,
                    "description": package.description,
                    "category": package.category
                },
                "destination": {
                    "city": package.destination_city,
                    "country": package.destination_country
                },
                "travel_dates": {
                    "start": trip_booking.travel_start_date.isoformat(),
                    "end": trip_booking.travel_end_date.isoformat(),
                    "duration_days": package.duration_days
                },
                "booking_details": {
                    "booking_date": trip_booking.booking_date.isoformat(),
                    "passengers": trip_booking.num_passengers,
                    "total_amount": float(trip_booking.total_amount),
                    "status": trip_booking.status
                },
                "includes": {
                    "flight": package.includes_flight,
                    "hotel": package.includes_hotel,
                    "activities": package.includes_activities
                },
                "excursions": [
                    {
                        "name": exc.excursion.name,
                        "booking_reference": exc.booking_reference,
                        "date": exc.excursion_date.isoformat(),
                        "duration": f"{exc.excursion.duration_hours} hours",
                        "participants": exc.num_participants,
                        "amount": float(exc.total_amount),
                        "status": exc.status,
                        "meeting_point": "Hotel lobby",
                        "category": exc.excursion.category
                    } for exc in excursions
                ],
                "special_requests": trip_booking.special_requests
            }
            
            return {
                "status": "success",
                "trip_details": trip_details
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Trip details check failed: {str(e)}"}
    
    @staticmethod
    async def check_trip_offers(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check available trip offers and deals"""
        try:
            destination = params.get('destination', params.get('city'))
            category = params.get('category', params.get('type'))
            budget = params.get('budget', params.get('budget_per_person', params.get('max_budget')))
            travelers = params.get('travelers', params.get('traveler_count', 1))
            
            # Get base packages
            search_params = {
                'destination': destination,
                'budget': budget,
                'interests': params.get('interests', params.get('activities', [])),
                'duration_days': params.get('duration', params.get('duration_days'))
            }
            
            base_result = await TripPackageService.search_trip(db, search_params)
            
            if base_result["status"] != "success":
                return base_result
            
            # Add special offers and deals
            offers = []
            for package in base_result["packages"][:5]:  # Top 5 packages
                # Generate promotional offers
                base_price = package["price_per_person"]
                
                # Early bird discount
                early_bird_price = base_price * 0.85
                offers.append({
                    "package_code": package["package_code"],
                    "package_name": package["name"],
                    "offer_type": "Early Bird Special",
                    "original_price": base_price,
                    "discounted_price": early_bird_price,
                    "savings": base_price - early_bird_price,
                    "discount_percentage": 15,
                    "conditions": "Book 45 days in advance",
                    "valid_until": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                    "destinations": [package["destination"]]
                })
                
                # Group discount
                if travelers >= 4:
                    group_price = base_price * 0.9
                    offers.append({
                        "package_code": package["package_code"],
                        "package_name": package["name"],
                        "offer_type": "Group Discount",
                        "original_price": base_price,
                        "discounted_price": group_price,
                        "savings": base_price - group_price,
                        "discount_percentage": 10,
                        "conditions": f"Groups of {travelers} or more",
                        "valid_until": (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
                        "destinations": [package["destination"]]
                    })
                
                # Last minute deal
                last_minute_price = base_price * 0.75
                offers.append({
                    "package_code": package["package_code"],
                    "package_name": package["name"],
                    "offer_type": "Last Minute Deal",
                    "original_price": base_price,
                    "discounted_price": last_minute_price,
                    "savings": base_price - last_minute_price,
                    "discount_percentage": 25,
                    "conditions": "Departure within 14 days",
                    "valid_until": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                    "destinations": [package["destination"]]
                })
            
            return {
                "status": "success",
                "search_criteria": {
                    "destination": destination,
                    "category": category,
                    "budget": budget,
                    "travelers": travelers
                },
                "current_offers": offers,
                "featured_destinations": [
                    {"city": "Madrid", "country": "Spain", "deals_available": 3},
                    {"city": "Paris", "country": "France", "deals_available": 2},
                    {"city": "Rome", "country": "Italy", "deals_available": 4},
                    {"city": "Barcelona", "country": "Spain", "deals_available": 2}
                ],
                "seasonal_promotions": [
                    {
                        "name": "Summer Europe Special",
                        "discount": "Up to 20% off",
                        "valid_dates": "June 1 - August 31",
                        "destinations": ["Europe"]
                    },
                    {
                        "name": "Fall Cultural Tours",
                        "discount": "15% off + free museum passes",
                        "valid_dates": "September 1 - November 30",
                        "destinations": ["Spain", "France", "Italy"]
                    }
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Trip offers check failed: {str(e)}"
            }

class InsuranceService:
    @staticmethod
    async def search_flight_insurance(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for flight insurance options"""
        try:
            destination = params.get('destination', 'Miami')
            start_date = params.get('start_date')
            end_date = params.get('end_date')
            travelers = params.get('travelers', 1)
            coverage_needs = params.get('coverage_needs', params.get('coverage', []))
            trip_cost = params.get('trip_cost', 500)
            
            # Define insurance plans
            insurance_plans = [
                {
                    "plan_name": "Basic Flight Protection",
                    "plan_code": "BASIC_FLIGHT",
                    "coverage_type": "flight",
                    "premium": 29.99 * travelers,
                    "coverage_amount": 1000,
                    "benefits": [
                        "Flight cancellation up to $1,000",
                        "Flight delay compensation up to $500",
                        "Missed connection coverage",
                        "24/7 customer service"
                    ],
                    "exclusions": [
                        "Pre-existing medical conditions",
                        "Weather delays under 3 hours",
                        "Carrier-caused delays"
                    ],
                    "deductible": 0
                },
                {
                    "plan_name": "Comprehensive Travel Shield",
                    "plan_code": "COMPREHENSIVE",
                    "coverage_type": "comprehensive",
                    "premium": 89.99 * travelers,
                    "coverage_amount": 5000,
                    "benefits": [
                        "Trip cancellation up to $5,000",
                        "Medical emergency coverage up to $25,000",
                        "Baggage loss/delay protection up to $1,500",
                        "Emergency evacuation up to $100,000",
                        "24/7 emergency assistance",
                        "Rental car coverage"
                    ],
                    "exclusions": [
                        "High-risk activities",
                        "Pre-existing conditions (waived if purchased within 14 days)"
                    ],
                    "deductible": 100
                },
                {
                    "plan_name": "Premium Global Coverage",
                    "plan_code": "PREMIUM_GLOBAL",
                    "coverage_type": "premium",
                    "premium": 149.99 * travelers,
                    "coverage_amount": 10000,
                    "benefits": [
                        "Trip cancellation up to $10,000",
                        "Emergency medical up to $100,000",
                        "Emergency evacuation up to $500,000",
                        "Cancel for any reason (75% coverage)",
                        "Adventure sports coverage",
                        "Business equipment coverage",
                        "Identity theft assistance"
                    ],
                    "exclusions": [
                        "Acts of war",
                        "Nuclear incidents",
                        "Pandemics (limited coverage)"
                    ],
                    "deductible": 0
                }
            ]
            
            # Score plans based on coverage needs
            for plan in insurance_plans:
                score = 0
                for need in coverage_needs:
                    if any(need.lower() in benefit.lower() for benefit in plan['benefits']):
                        score += 1
                plan['match_score'] = score
                
                # Add trip-specific calculations
                plan['coverage_percentage'] = min(100, (plan['coverage_amount'] / trip_cost) * 100) if trip_cost > 0 else 100
                plan['premium_percentage'] = (plan['premium'] / trip_cost) * 100 if trip_cost > 0 else 0
            
            # Sort by match score
            insurance_plans.sort(key=lambda x: -x['match_score'])
            
            return {
                "status": "success",
                "search_criteria": {
                    "destination": destination,
                    "travel_dates": f"{start_date} to {end_date}",
                    "travelers": travelers,
                    "coverage_needs": coverage_needs,
                    "trip_cost": trip_cost
                },
                "insurance_plans": insurance_plans,
                "recommendation": "Consider the Comprehensive Travel Shield for international travel with medical coverage.",
                "important_notes": [
                    "Purchase within 14 days of initial trip payment for pre-existing condition waiver",
                    "Review all terms and conditions before purchase",
                    "Keep all receipts for potential claims",
                    "Contact insurance provider immediately in case of emergency"
                ],
                "coverage_tips": [
                    "Medical coverage is especially important for international travel",
                    "Trip cancellation coverage should match your trip cost",
                    "Consider 'Cancel for Any Reason' if you need flexibility",
                    "Adventure sports require specialized coverage"
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Insurance search failed: {str(e)}"
            }
    
    @staticmethod
    async def purchase_flight_insurance(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Purchase flight insurance"""
        try:
            plan = params.get('plan', 'comprehensive')
            destination = params.get('destination')
            start_date = params.get('start_date')
            end_date = params.get('end_date')
            travelers = params.get('travelers', 1)
            booking_ref = params.get('booking_reference', params.get('confirmation_number'))
            trip_cost = params.get('ticket_price', 500)
            
            # Find existing booking if provided
            booking = None
            if booking_ref:
                booking = db.query(Booking).filter_by(booking_reference=booking_ref).first()
            
            # Determine plan details
            plan_details = {
                'basic': {'premium': 29.99, 'coverage': 1000, 'type': 'flight'},
                'standard': {'premium': 89.99, 'coverage': 5000, 'type': 'comprehensive'},
                'comprehensive': {'premium': 89.99, 'coverage': 5000, 'type': 'comprehensive'},
                'full': {'premium': 149.99, 'coverage': 10000, 'type': 'premium'},
                'premium': {'premium': 149.99, 'coverage': 10000, 'type': 'premium'}
            }
            
            selected_plan = plan_details.get(plan, plan_details['comprehensive'])
            total_premium = selected_plan['premium'] * travelers
            
            # Generate policy number
            policy_number = f"HJ{random.randint(100000, 999999)}"
            
            # Create insurance policy
            insurance = InsurancePolicy(
                policy_number=policy_number,
                booking_id=booking.id if booking else None,
                passenger_id=booking.passenger_id if booking else 1,  # Default passenger
                policy_type=selected_plan['type'],
                coverage_amount=Decimal(str(selected_plan['coverage'])),
                premium=Decimal(str(total_premium)),
                start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
                end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
                status='active',
                provider='HopJetAir Insurance Partners',
                terms_conditions='Standard travel insurance terms apply. See policy documents for complete details.'
            )
            db.add(insurance)
            db.commit()
            
            return {
                "status": "success",
                "policy_number": policy_number,
                "plan_type": selected_plan['type'],
                "coverage_amount": selected_plan['coverage'],
                "premium_paid": total_premium,
                "travelers_covered": travelers,
                "coverage_period": {
                    "start": start_date,
                    "end": end_date,
                    "duration_days": (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days
                },
                "purchase_details": {
                    "purchase_date": datetime.now().isoformat(),
                    "currency": "USD",
                    "payment_method": "Credit Card"
                },
                "confirmation_message": f"Insurance purchased successfully. Policy number: {policy_number}",
                "next_steps": [
                    "Policy documents will be emailed within 24 hours",
                    "Save policy number for your records",
                    "Review coverage details and exclusions",
                    "Keep claim contact information handy while traveling"
                ],
                "important_contacts": {
                    "claims": "1-800-CLAIM-HJ",
                    "emergency_assistance": "1-800-EMERGENCY",
                    "policy_service": "1-800-POLICY-HJ"
                },
                "claim_process": {
                    "step1": "Contact claims department immediately",
                    "step2": "Provide policy number and incident details", 
                    "step3": "Submit required documentation",
                    "step4": "Receive claim decision within 10 business days"
                }
            }
            
        except Exception as e:
            db.rollback()
            return {
                "status": "error",
                "message": f"Insurance purchase failed: {str(e)}"
            }
    
    @staticmethod
    async def search_trip_insurance(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search trip insurance options"""
        try:
            # Use flight insurance logic but adjust for trip-specific needs
            trip_params = {
                'destination': params.get('destination'),
                'start_date': params.get('start_date'),
                'end_date': params.get('end_date'),
                'travelers': params.get('travelers', 1),
                'coverage_needs': params.get('coverage_needs', params.get('coverage', [])),
                'trip_cost': params.get('budget', 1000)
            }
            
            result = await InsuranceService.search_flight_insurance(db, trip_params)
            
            if result["status"] == "success":
                # Add trip-specific recommendations
                result["trip_specific_recommendations"] = [
                    "Trip cancellation coverage is essential for non-refundable bookings",
                    "Medical coverage is crucial for international destinations", 
                    "Consider baggage coverage for valuable items",
                    "Emergency evacuation coverage for remote destinations"
                ]
                
                # Adjust recommendations based on activities
                activities = params.get('activities', [])
                if any(activity in ['hiking', 'skiing', 'diving'] for activity in activities):
                    result["activity_recommendations"] = [
                        "Adventure sports require specialized coverage",
                        "Consider premium plans for high-risk activities",
                        "Verify coverage for specific activities planned"
                    ]
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Trip insurance search failed: {str(e)}"
            }
    
    @staticmethod
    async def purchase_trip_insurance(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Purchase trip insurance"""
        try:
            # Use flight insurance purchase logic
            insurance_params = {
                'plan': params.get('plan', 'comprehensive'),
                'destination': params.get('destination'),
                'start_date': params.get('start_date'),
                'end_date': params.get('end_date'),
                'travelers': params.get('travelers', 1),
                'trip_cost': params.get('budget', 1000)
            }
            
            return await InsuranceService.purchase_flight_insurance(db, insurance_params)
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Trip insurance purchase failed: {str(e)}"
            }
    
    @staticmethod
    async def check_flight_insurance_coverage(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check flight insurance coverage details"""
        try:
            booking_ref = params.get('booking_reference')
            policy_number = params.get('policy_number')
            
            # Find insurance policy
            policy = None
            if policy_number:
                policy = db.query(InsurancePolicy).filter_by(policy_number=policy_number).first()
            elif booking_ref:
                booking = db.query(Booking).filter_by(booking_reference=booking_ref).first()
                if booking:
                    policy = db.query(InsurancePolicy).filter_by(booking_id=booking.id).first()
            
            if not policy:
                return {
                    "status": "error",
                    "message": "Insurance policy not found"
                }
            
            coverage_details = {
                "policy_number": policy.policy_number,
                "policy_status": policy.status,
                "policy_type": policy.policy_type,
                "coverage_period": {
                    "start": policy.start_date.isoformat(),
                    "end": policy.end_date.isoformat(),
                    "active": policy.start_date <= datetime.now().date() <= policy.end_date
                },
                "coverage_amount": float(policy.coverage_amount),
                "premium_paid": float(policy.premium),
                "provider": policy.provider,
                "benefits": []
            }
            
            # Add benefits based on policy type
            if policy.policy_type == 'flight':
                coverage_details["benefits"] = [
                    "Flight cancellation coverage",
                    "Flight delay compensation",
                    "Missed connection protection"
                ]
            elif policy.policy_type == 'comprehensive':
                coverage_details["benefits"] = [
                    "Trip cancellation coverage",
                    "Medical emergency coverage",
                    "Baggage protection",
                    "Emergency assistance"
                ]
            elif policy.policy_type == 'premium':
                coverage_details["benefits"] = [
                    "Comprehensive trip coverage",
                    "Cancel for any reason",
                    "Adventure sports coverage",
                    "Business equipment protection"
                ]
            
            return {
                "status": "success",
                "coverage_details": coverage_details,
                "claim_information": {
                    "how_to_claim": "Call 1-800-CLAIM-HJ",
                    "required_documents": ["Policy number", "Incident details", "Receipts", "Medical reports if applicable"],
                    "claim_processing_time": "5-10 business days",
                    "emergency_contact": "1-800-EMERGENCY for 24/7 assistance"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Insurance coverage check failed: {str(e)}"
            }