from fastapi import APIRouter, HTTPException, Query, status
from src.db.connection import get_db_connection
from fastapi.responses import JSONResponse
from src.db.exceptions import DatabaseQueryError
from src.db.models import (
    book_flight_data, get_flight_offers_data, get_flight_prices_data,
    get_flight_reservation_data, get_flight_status_data, search_flights_data,
    cancel_flight_data, change_flight_data, purchase_flight_insurance_data,
    get_refund_data, get_arrival_time_data, get_departure_time_data
)

router = APIRouter()

@router.post("/api/v1/book-flight/")
async def book_flight(flight_number: str = Query(...), passenger_id: str = Query(...)):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                booking_id = await book_flight_data(cursor, flight_number, passenger_id)
                if not booking_id:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Flight not available")
                await conn.commit()
                return {"status": "success", "booking_id": booking_id}
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.get("/api/v1/flight-offers/")
async def check_flight_offers():
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                offers = await get_flight_offers_data(cursor)
                await conn.commit()
                return {"status": "success", "offers": offers}
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.get("/api/v1/flight-prices/{flight_number}")
async def check_flight_prices(flight_number: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                result = await get_flight_prices_data(cursor, flight_number)
                await conn.commit()
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flight not found")
                return {
                    "status": "success",
                    "prices": {
                        "price": result[0],
                        "availability": result[1]
                    }
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.get("/api/v1/flight-reservation/{booking_id}")
async def check_flight_reservation(booking_id: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                result = await get_flight_reservation_data(cursor, booking_id)
                await conn.commit()
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
                return {
                    "status": "success",
                    "reservation": {
                        "passenger_id": result[0],
                        "flight_number": result[1],
                        "booking_date": result[2],
                        "status": result[3],
                        "total_price": result[4],
                        "departure": result[5],
                        "destination": result[6]
                    }
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.get("/api/v1/flight-status/{flight_number}")
async def check_flight_status(flight_number: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                result = await get_flight_status_data(cursor, flight_number)
                await conn.commit()
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flight not found")
                return {
                    "status": "success",
                    "flight_status": {
                        "departure": result[0],
                        "destination": result[1],
                        "status": result[2],
                        "departure_time": result[3],
                        "arrival_time": result[4],
                        "gate": result[5]
                    }
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.get("/api/v1/search-flight/{departure}/{destination}/{date}")
async def search_flight(departure: str, destination: str, date: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                flights = await search_flights_data(cursor, departure, destination, date)
                await conn.commit()
                return {"status": "success", "flights": flights}
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.post("/api/v1/cancel-flight/{booking_id}")
async def cancel_flight(booking_id: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                updated = await cancel_flight_data(cursor, booking_id)
                if not updated:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
                await conn.commit()
                return {
                    "status": "success",
                    "booking_status": "Cancelled",
                    "policy": "Free within 24 hours, $50 fee after"
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.post("/api/v1/change-flight/{booking_id}")
async def change_flight(booking_id: str, new_flight_number: str = Query(...)):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                result = await change_flight_data(cursor, booking_id, new_flight_number)
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
                await conn.commit()
                return {
                    "status": "success",
                    "booking": {
                        "passenger_id": result[0],
                        "flight_number": result[1],
                        "booking_date": result[2],
                        "status": result[3],
                        "total_price": result[4]
                    },
                    "policy": "Free within 24 hours, $75 fee after"
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.post("/api/v1/purchase-flight-insurance/{booking_id}")
async def purchase_flight_insurance(booking_id: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                insurance_id = await purchase_flight_insurance_data(cursor, booking_id)
                await conn.commit()
                return {
                    "status": "success",
                    "insurance_id": insurance_id,
                    "terms": "Covers cancellation up to $1,000"
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.post("/api/v1/get-refund/{booking_id}")
async def get_refund(booking_id: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                updated = await get_refund_data(cursor, booking_id)
                if not updated:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
                await conn.commit()
                return {
                    "status": "success",
                    "booking_status": "Refunded",
                    "policy": "Processed in 5-7 days, 50% penalty for non-refundable"
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.get("/api/v1/arrival-time/{flight_number}")
async def check_arrival_time(flight_number: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                result = await get_arrival_time_data(cursor, flight_number)
                await conn.commit()
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flight not found")
                return {"status": "success", "arrival_time": result}
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.get("/api/v1/departure-time/{flight_number}")
async def check_departure_time(flight_number: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                result = await get_departure_time_data(cursor, flight_number)
                await conn.commit()
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flight not found")
                return {"status": "success", "departure_time": result}
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )