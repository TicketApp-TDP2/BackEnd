from fastapi.exceptions import HTTPException
from app.repositories.organizers import PersistentOrganizerRepository
from fastapi import status, APIRouter
from app.config.logger import setup_logger
from app.schemas.organizers import OrganizerCreateSchema, OrganizerSchema
from app.commands.organizers import CreateOrganizerCommand, GetOrganizerCommand
from app.utils.error import TicketAppError
from typing import List


logger = setup_logger(name=__name__)
router = APIRouter()


@router.post(
    '/organizers', status_code=status.HTTP_201_CREATED, response_model=OrganizerSchema
)
async def create_organizer(organizer_body: OrganizerCreateSchema):
    try:
        repository = PersistentOrganizerRepository()
        organizer = CreateOrganizerCommand(repository, organizer_body).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
    return organizer


@router.get(
    '/organizers/{id}', status_code=status.HTTP_200_OK, response_model=OrganizerSchema
)
async def get_organizer(id: str):
    try:
        repository = PersistentOrganizerRepository()
        organizer = GetOrganizerCommand(repository, id).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )

    return organizer
