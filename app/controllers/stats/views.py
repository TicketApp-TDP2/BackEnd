from fastapi.exceptions import HTTPException
from app.repositories.event import PersistentEventRepository
from app.repositories.organizers import PersistentOrganizerRepository
from app.repositories.bookings import PersistentBookingRepository
from app.repositories.complaints import PersistentComplaintRepository
from fastapi import status, APIRouter, Depends
from app.config.logger import setup_logger
from app.schemas.stats import AppStatsSchema, StatParams
from app.utils.error import TicketAppError
from app.commands.stats import GetStatsCommand
from typing import List


logger = setup_logger(name=__name__)
router = APIRouter()


@router.get('/stats', status_code=status.HTTP_200_OK, response_model=AppStatsSchema)
async def get_stats(params: StatParams = Depends()):
    try:
        event_repository = PersistentEventRepository()
        organizer_repository = PersistentOrganizerRepository()
        booking_repository = PersistentBookingRepository()
        complaint_repository = PersistentComplaintRepository()
        stat = GetStatsCommand(
            event_repository,
            organizer_repository,
            booking_repository,
            complaint_repository,
            params,
        ).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
    return stat
