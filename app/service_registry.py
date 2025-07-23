"""
HopJetAir Service Registry
Central registry for all airline business services
"""

# Import all service classes
from datetime import datetime
from .flight_services import FlightSearchService, FlightStatusService, FlightAvailabilityService, FlightBookingService, FlightChangeService
from .booking_services import BookingServices
from .seat_checkin_services import SeatManagementService, CheckInService, BoardingPassService, CheckInInfoService
from .trip_insurance_services import TripPackageService, InsuranceService
from .support_pricing_services import CustomerSupportService, PolicyService, RefundService, BaggageService, PricingService

class HopJetAirServiceRegistry:
    """
    Central registry for all HopJetAir services
    Provides unified access to all business logic services
    """
    
    def __init__(self):
        # Flight Services
        self.flight_search = FlightSearchService()
        self.flight_status = FlightStatusService()
        self.flight_availability = FlightAvailabilityService()
        self.flight_booking = FlightBookingService()
        self.flight_change = FlightChangeService()
        
        # Booking Services
        self.booking = BookingServices()
        # self.booking_cancellation = BookingCancellationService()
        # self.booking_modification = BookingModificationService()
        # self.time_checks = TimeCheckServices()
        
        # Seat and Check-in Services
        self.seat_management = SeatManagementService()
        self.check_in = CheckInService()
        self.boarding_pass = BoardingPassService()
        self.check_in_info = CheckInInfoService()
        
        # Trip and Insurance Services
        self.trip_packages = TripPackageService()
        self.insurance = InsuranceService()
        
        # Support and Pricing Services
        self.customer_support = CustomerSupportService()
        self.policy = PolicyService()
        self.refund = RefundService()
        self.baggage = BaggageService()
        self.pricing = PricingService()
    
    def get_service(self, service_name: str):
        """Get service by name"""
        return getattr(self, service_name, None)
    
    def list_services(self):
        """List all available services"""
        return [attr for attr in dir(self) if not attr.startswith('_') and attr not in ['get_service', 'list_services']]

# Service mapping for endpoint handlers
SERVICE_ENDPOINTS = {
    # Flight Services 11
    'search_flight': ('flight_search', 'search_flight'),
    'search_flights': ('flight_search', 'search_flights'),
    'book_flight': ('flight_booking', 'book_flight'),
    'check_flight_status': ('flight_status', 'check_flight_status'),
    'get_flight_status': ('flight_status', 'get_flight_status'),
    'check_flight_availability': ('flight_availability', 'check_flight_availability'),
    'query_flight_availability': ('flight_availability', 'query_flight_availability'),
    'check_flight_availability_and_fare': ('flight_availability', 'check_flight_availability_and_fare'),
    'change_flight': ('flight_change', 'change_flight'),
    'confirm_flight_change': ('flight_change', 'confirm_flight_change'),
    'update_flight_date': ('flight_change', 'update_flight_date'),
    
    # Booking Services 8
    'get_booking_details': ('booking', 'get_booking_details'),
    'check_flight_reservation': ('booking', 'check_flight_reservation'),
    'query_booking_details': ('booking', 'query_booking_details'),
    'retrieve_booking_by_email': ('booking', 'retrieve_booking_by_email'),
    'cancel_booking': ('booking', 'cancel_booking'),
    'send_itinerary_email': ('booking', 'send_itinerary_email'),
    'check_arrival_time': ('booking', 'check_arrival_time'),
    'check_departure_time': ('booking', 'check_departure_time'),
    
    # Seat and Check-in Services 12
    'check_seat_availability': ('seat_management', 'check_seat_availability'),
    'change_seat': ('seat_management', 'change_seat'),
    'choose_seat': ('seat_management', 'choose_seat'),
    'check_in_passenger': ('check_in', 'check_in_passenger'),
    'check_in': ('check_in', 'check_in'),
    'check_flight_checkin_status': ('check_in', 'check_flight_checkin_status'),
    'get_boarding_pass': ('boarding_pass', 'get_boarding_pass'),
    'get_boarding_pass_pdf': ('boarding_pass', 'get_boarding_pass_pdf'),
    'send_boarding_pass_email': ('boarding_pass', 'send_boarding_pass_email'),
    'verify_booking_and_get_boarding_pass': ('boarding_pass', 'verify_booking_and_get_boarding_pass'),
    'get_check_in_info': ('check_in_info', 'get_check_in_info'),
    'query_airport_checkin_info': ('check_in_info', 'query_airport_checkin_info'),
    
    # Trip and Insurance Services 9
    'search_trip': ('trip_packages', 'search_trip'),
    'book_trip': ('trip_packages', 'book_trip'),
    'check_trip_details': ('trip_packages', 'check_trip_details'),
    'check_trip_offers': ('trip_packages', 'check_trip_offers'),
    'purchase_flight_insurance': ('insurance', 'purchase_flight_insurance'),
    'purchase_trip_insurance': ('insurance', 'purchase_trip_insurance'),
       
    # Support and Pricing Services 7
    'escalate_to_human_agent': ('customer_support', 'escalate_to_human_agent'),
    'schedule_callback': ('customer_support', 'schedule_callback'),
    'query_policy_rag_db': ('policy', 'query_policy_rag_db'),
    'initiate_refund': ('refund', 'initiate_refund'),
    'check_refund_eligibility': ('refund', 'check_refund_eligibility'),
    'search_flight_prices': ('pricing', 'search_flight_prices'),
}

# Additional service mappings for endpoints with similar functionality
ADDITIONAL_MAPPINGS = {
    # Trip Management 5
    'check_trip_plan': ('trip_packages', 'check_trip_details'),
    'check_trip_prices': ('pricing', 'search_flight_prices'),
    'search_trip_prices': ('pricing', 'search_flight_prices'),
    'change_trip': ('trip_packages', 'check_trip_details'),  # Would need implementation
    'cancel_trip': ('refund', 'initiate_refund'),
    
    # Flight Offers and Pricing 2
    'check_flight_offers': ('pricing', 'search_flight_prices'),
    'check_flight_prices': ('pricing', 'search_flight_prices'),
    
    # Cancellation and Policies 2
    'get_trip_cancellation_policy': ('policy', 'query_policy_rag_db'),
    
    # Email Services 1
    'send_email': ('boarding_pass', 'send_boarding_pass_email'),
    
    # Excursions (basic implementation) 4
    'get_excursion_cancellation_policy': ('policy', 'query_policy_rag_db'),
    'check_excursion_availability': ('trip_packages', 'check_trip_offers'),
    'book_excursion': ('trip_packages', 'book_trip'),
    'book_activity': ('trip_packages', 'book_trip'),
    
    # Additional Check-in Services 3
    'resend_boarding_pass': ('boarding_pass', 'send_boarding_pass_email'),
    'get_phone_checkin_info': ('check_in_info', 'get_check_in_info'),
    
    # Refund Services 5
    'get_refund': ('refund', 'check_refund_eligibility'),
    'update_refund_method': ('refund', 'initiate_refund'),
    'query_compensation_eligibility': ('refund', 'check_refund_eligibility'),
    'issue_travel_credit_voucher': ('refund', 'initiate_refund'),
    'issue_travel_voucher': ('refund', 'initiate_refund'),
    
    # Insurance Retrieval 1
    'retrieve_flight_insurance': ('insurance', 'check_flight_insurance_coverage'),
    
    # Trip Segments 1
    'get_trip_segments': ('trip_packages', 'check_trip_details'),
}

# Combine all mappings
ALL_SERVICE_MAPPINGS = {**SERVICE_ENDPOINTS, **ADDITIONAL_MAPPINGS}

# Global service registry instance
service_registry = HopJetAirServiceRegistry()

async def execute_service_endpoint(endpoint_name: str, db, params: dict):
    """
    Execute a service endpoint by name
    
    Args:
        endpoint_name: Name of the endpoint
        db: Database session
        params: Parameters for the service call
    
    Returns:
        Service response dictionary
    """
    if endpoint_name not in ALL_SERVICE_MAPPINGS:
        return {
            "status": "error",
            "message": f"Endpoint '{endpoint_name}' not found in service registry"
        }
    
    service_name, method_name = ALL_SERVICE_MAPPINGS[endpoint_name]
    service = service_registry.get_service(service_name)
    
    if not service:
        return {
            "status": "error", 
            "message": f"Service '{service_name}' not found"
        }
    
    method = getattr(service, method_name, None)
    if not method:
        return {
            "status": "error",
            "message": f"Method '{method_name}' not found in service '{service_name}'"
        }
    
    try:
        return await method(db, params)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Service execution failed: {str(e)}"
        }

def get_service_info():
    """Get information about all available services"""
    return {
        "total_endpoints": len(ALL_SERVICE_MAPPINGS),
        "service_categories": {
            "flight_services": len([k for k, v in ALL_SERVICE_MAPPINGS.items() if v[0].startswith('flight')]),
            "booking_services": len([k for k, v in ALL_SERVICE_MAPPINGS.items() if v[0].startswith('booking')]),
            "seat_checkin_services": len([k for k, v in ALL_SERVICE_MAPPINGS.items() if v[0] in ['seat_management', 'check_in', 'boarding_pass']]),
            "trip_insurance_services": len([k for k, v in ALL_SERVICE_MAPPINGS.items() if v[0] in ['trip_packages', 'insurance']]),
            "support_services": len([k for k, v in ALL_SERVICE_MAPPINGS.items() if v[0] in ['customer_support', 'policy', 'refund', 'baggage', 'pricing']])
        },
        "available_endpoints": list(ALL_SERVICE_MAPPINGS.keys())
    }

# Service health check
async def check_service_health():
    """Check health of all services"""
    health_status = {
        "status": "healthy",
        "services": {},
        "timestamp": datetime.now().isoformat()
    }
    
    for service_name in service_registry.list_services():
        try:
            service = service_registry.get_service(service_name)
            health_status["services"][service_name] = {
                "status": "healthy",
                "available": service is not None
            }
        except Exception as e:
            health_status["services"][service_name] = {
                "status": "unhealthy", 
                "error": str(e)
            }
            health_status["status"] = "degraded"
    
    return health_status

# Export commonly used services for direct import
__all__ = [
    'service_registry',
    'execute_service_endpoint', 
    'get_service_info',
    'check_service_health',
    'ALL_SERVICE_MAPPINGS'
]