from fastapi.exceptions import HTTPException
from app.repositories.event import PersistentEventRepository
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
        stat = GetStatsCommand(event_repository, params).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
    return stat
