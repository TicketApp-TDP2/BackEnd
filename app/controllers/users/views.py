from fastapi.exceptions import HTTPException
from app.repositories.users import PersistentUserRepository
from fastapi import status, APIRouter
from app.config.logger import setup_logger
from app.schemas.users import UserCreateSchema, UserSchema
from app.commands.users import CreateUserCommand, GetUserCommand
from app.utils.error import TicketAppError
from typing import List
from app.schemas.bookings import BookingSchema
from app.commands.bookings import GetBookingsByReserverCommand
from app.repositories.bookings import PersistentBookingRepository
from app.repositories.event import PersistentEventRepository


logger = setup_logger(name=__name__)
router = APIRouter()


@router.post(
    '/users',
    status_code=status.HTTP_201_CREATED,
    response_model=UserSchema,
    tags=["Users"],
)
async def create_user(user_body: UserCreateSchema):
    try:
        repository = PersistentUserRepository()
        user = CreateUserCommand(repository, user_body).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
    return user


@router.get(
    '/users/{id}',
    status_code=status.HTTP_200_OK,
    response_model=UserSchema,
    tags=["Users"],
)
async def get_user(id: str):
    try:
        repository = PersistentUserRepository()
        user = GetUserCommand(repository, id).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )

    return user


@router.get(
    '/users/{id}/bookings_reserved',
    status_code=status.HTTP_200_OK,
    response_model=List[BookingSchema],
)
async def get_user_bookings_reserved(id: str):
    try:
        repository = PersistentBookingRepository()
        event_repository = PersistentEventRepository()
        bookings = GetBookingsByReserverCommand(
            repository, event_repository, id
        ).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )

    return bookings
