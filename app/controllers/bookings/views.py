from fastapi.exceptions import HTTPException
from app.repositories.bookings import PersistentBookingRepository
from app.repositories.event import PersistentEventRepository
from fastapi import status, APIRouter
from app.config.logger import setup_logger
from app.schemas.bookings import BookingCreateSchema, BookingSchema, verifyBookingSchema
from app.schemas.stats import EventBookingsByHourStatSchema
from app.commands.bookings import (
    CreateBookingCommand,
    VerifyBookingCommand,
    GetBookingsByEventCommand,
    GetBookingsByEventVerifiedCommand,
    GetBookingsByHourCommand,
)
from app.utils.error import TicketAppError
from typing import List


logger = setup_logger(name=__name__)
router = APIRouter()


@router.post(
    '/bookings', status_code=status.HTTP_201_CREATED, response_model=BookingSchema
)
async def create_booking(booking_body: BookingCreateSchema):
    try:
        repository = PersistentBookingRepository()
        event_repository = PersistentEventRepository()
        booking = CreateBookingCommand(
            repository, booking_body, event_repository
        ).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
    return booking


@router.put(
    '/bookings/{id}/verify',
    status_code=status.HTTP_200_OK,
    response_model=BookingSchema,
)
async def verify_booking(id: str, verify_body: verifyBookingSchema):
    try:
        repository = PersistentBookingRepository()
        event_repository = PersistentEventRepository()
        booking = VerifyBookingCommand(
            repository, event_repository, id, verify_body.event_id
        ).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
    return booking


@router.get(
    '/bookings/event/{event_id}',
    status_code=status.HTTP_200_OK,
    response_model=List[BookingSchema],
)
async def get_bookings_by_event(event_id: str):
    try:
        repository = PersistentBookingRepository()
        bookings = GetBookingsByEventCommand(repository, event_id).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
    return bookings


@router.get(
    '/bookings/event/{event_id}/verified',
    status_code=status.HTTP_200_OK,
    response_model=List[BookingSchema],
)
async def get_bookings_by_event_verified(event_id: str):
    try:
        repository = PersistentBookingRepository()
        bookings = GetBookingsByEventVerifiedCommand(repository, event_id).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
    return bookings


@router.get(
    '/bookings/event/{event_id}/by_hour',
    status_code=status.HTTP_200_OK,
    response_model=List[EventBookingsByHourStatSchema],
)
async def get_bookings_by_hour(event_id: str):
    try:
        repository = PersistentBookingRepository()
        bookings = GetBookingsByHourCommand(repository, event_id).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
    return bookings
