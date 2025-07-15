from fastapi import APIRouter, HTTPException, Query, status
from src.db.connection import get_db_connection
from fastapi.responses import JSONResponse
from src.db.exceptions import DatabaseQueryError
from src.db.models import (
    get_trip_prices_data, book_trip_data, get_trip_details_data, get_trip_offers_data,
    get_trip_plan_data, search_trips_data, cancel_trip_data, change_trip_data,
    purchase_trip_insurance_data
)

router = APIRouter()

@router.get("/api/v1/trip-prices/{trip_id}")
async def check_trip_prices(trip_id: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                result = await get_trip_prices_data(cursor, trip_id)
                await conn.commit()
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
                return {
                    "status": "success",
                    "trip_prices": {
                        "total_price": result[0]
                    }
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.post("/api/v1/book-trip/")
async def book_trip(passenger_id: str = Query(...)):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                trip_id = await book_trip_data(cursor, passenger_id)
                await conn.commit()
                return {"status": "success", "trip_id": trip_id}
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.get("/api/v1/trip-details/{trip_id}")
async def check_trip_details(trip_id: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                result = await get_trip_details_data(cursor, trip_id)
                await conn.commit()
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
                return {
                    "status": "success",
                    "trip_details": {
                        "total_price": result["total_price"],
                        "status": result["status"],
                        "components": result["components"]
                    }
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.get("/api/v1/trip-offers/")
async def check_trip_offers():
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                offers = await get_trip_offers_data(cursor)
                await conn.commit()
                return {"status": "success", "offers": offers}
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.get("/api/v1/trip-plan/{trip_id}")
async def check_trip_plan(trip_id: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                plan = await get_trip_plan_data(cursor, trip_id)
                await conn.commit()
                if not plan:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip plan not found")
                return {"status": "success", "trip_plan": plan}
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.get("/api/v1/search-trip/{departure}/{destination}/{date}")
async def search_trip(departure: str, destination: str, date: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                trips = await search_trips_data(cursor, departure, destination, date)
                await conn.commit()
                return {"status": "success", "trips": trips}
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.post("/api/v1/cancel-trip/{trip_id}")
async def cancel_trip(trip_id: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                updated = await cancel_trip_data(cursor, trip_id)
                if not updated:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
                await conn.commit()
                return {
                    "status": "success",
                    "trip_status": "Cancelled",
                    "policy": "Free within 48 hours, $100 fee after"
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.post("/api/v1/change-trip/{trip_id}")
async def change_trip(trip_id: str, new_flight_number: str = Query(...)):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                result = await change_trip_data(cursor, trip_id, new_flight_number)
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip component not found")
                await conn.commit()
                return {
                    "status": "success",
                    "trip_component": {
                        "component_type": result[0],
                        "flight_number": result[1],
                        "price": result[2]
                    },
                    "policy": "Free within 48 hours, $100 fee after"
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.post("/api/v1/purchase-trip-insurance/{trip_id}")
async def purchase_trip_insurance(trip_id: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                insurance_id = await purchase_trip_insurance_data(cursor, trip_id)
                await conn.commit()
                return {
                    "status": "success",
                    "insurance_id": insurance_id,
                    "terms": "Covers cancellation up to $2,000"
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )