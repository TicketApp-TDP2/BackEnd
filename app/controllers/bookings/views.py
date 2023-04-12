from fastapi.exceptions import HTTPException
from app.repositories.bookings import PersistentBookingRepository
from fastapi import status, APIRouter
from app.config.logger import setup_logger
from app.schemas.bookings import BookingCreateSchema, BookingSchema
from app.commands.bookings import CreateBookingCommand
from app.utils.error import TicketAppError


logger = setup_logger(name=__name__)
router = APIRouter()


@router.post(
    '/bookings', status_code=status.HTTP_201_CREATED, response_model=BookingSchema
)
async def create_booking(booking_body: BookingCreateSchema):
    try:
        repository = PersistentBookingRepository()
        booking = CreateBookingCommand(repository, booking_body).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
    return booking
