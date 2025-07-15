from fastapi import APIRouter, HTTPException,status
from src.db.connection import get_db_connection
from fastapi.responses import JSONResponse
from src.db.exceptions import DatabaseQueryError
from src.db.models import (
    get_boarding_pass_data, check_in_booking, choose_seat_data, change_seat_data
)

router = APIRouter()

@router.get("/api/v1/boarding-pass/{booking_id}")
async def get_boarding_pass(booking_id: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                result = await get_boarding_pass_data(cursor, booking_id)
                await conn.commit()
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boarding pass not found")
                return {
                    "status": "success",
                    "boarding_pass": {
                        "gate": result[5],
                        "seat": result[6],
                        "boarding_time": result[7],
                        "pdf_url": result[8]
                    }
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.get("/api/v1/print-boarding-pass/{booking_id}")
async def print_boarding_pass(booking_id: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                result = await get_boarding_pass_data(cursor, booking_id)
                await conn.commit()
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boarding pass not found")
                return {
                    "status": "success",
                    "boarding_pass": {
                        "gate": result[5],
                        "seat": result[6],
                        "boarding_time": result[7],
                        "pdf_url": result[8]
                    }
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.post("/api/v1/check-in/{booking_id}")
async def check_in(booking_id: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                result = await check_in_booking(cursor, booking_id)
                if not result["updated"]:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
                await conn.commit()
                return {
                    "status": "success",
                    "message": "Check-in successful",
                    "boarding_pass": {
                        "gate": result["gate"],
                        "seat": result["seat"],
                        "boarding_time": result["boarding_time"]
                    }
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.post("/api/v1/choose-seat/{booking_id}")
async def choose_seat(booking_id: str, seat_number: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                result = await choose_seat_data(cursor, booking_id, seat_number)
                await conn.commit()
                return {
                    "status": "success",
                    "seat": {
                        "booking_id": booking_id,
                        "flight_number": result["flight_number"],
                        "seat_number": seat_number,
                        "additional_fee": result["additional_fee"]
                    }
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )


@router.post("/api/v1/change-seat/{booking_id}")
async def change_seat(booking_id: str, seat_number: str):
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                result = await change_seat_data(cursor, booking_id, seat_number)
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found")
                await conn.commit()
                return {
                    "status": "success",
                    "seat": {
                        "flight_number": result[0],
                        "seat_number": result[1],
                        "additional_fee": result[2]
                    },
                    "policy": "$20 fee for changes"
                }
    except DatabaseQueryError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)}
        )