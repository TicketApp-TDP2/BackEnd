from fastapi.exceptions import HTTPException
from app.repositories.organizers import PersistentOrganizerRepository
from app.repositories.event import PersistentEventRepository
from fastapi import status, APIRouter
from app.config.logger import setup_logger
from app.schemas.organizers import (
    OrganizerCreateSchema,
    OrganizerSchema,
    OrganizerUpdateSchema,
)
from app.commands.organizers import (
    CreateOrganizerCommand,
    GetOrganizerCommand,
    UpdateOrganizerCommand,
    SuspendOrganizerCommand,
    UnSuspendOrganizerCommand,
)
from app.utils.error import TicketAppError
from typing import List


logger = setup_logger(name=__name__)
router = APIRouter()


@router.post(
    '/organizers',
    status_code=status.HTTP_201_CREATED,
    response_model=OrganizerSchema,
    tags=["Organizers"],
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
    '/organizers/{id}',
    status_code=status.HTTP_200_OK,
    response_model=OrganizerSchema,
    tags=["Organizers"],
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


@router.put(
    '/organizers/{id}',
    status_code=status.HTTP_201_CREATED,
    response_model=OrganizerSchema,
    tags=["Organizers"],
)
async def update_organizer(id: str, update_body: OrganizerUpdateSchema):
    try:
        repository = PersistentOrganizerRepository()
        user = UpdateOrganizerCommand(repository, update_body, id).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
    return user


@router.put(
    '/organizers/{id}/suspend',
    status_code=status.HTTP_200_OK,
    response_model=OrganizerSchema,
    tags=["Organizers"],
)
async def suspend_organizer(id: str):
    try:
        repository = PersistentOrganizerRepository()
        event_repository = PersistentEventRepository()
        organizer = SuspendOrganizerCommand(repository, id, event_repository).execute()
        return organizer
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )


@router.put(
    '/organizers/{id}/unsuspend',
    status_code=status.HTTP_200_OK,
    response_model=OrganizerSchema,
    tags=["Organizers"],
)
async def unsuspend_organizer(id: str):
    try:
        repository = PersistentOrganizerRepository()
        event_repository = PersistentEventRepository()
        organizer = UnSuspendOrganizerCommand(
            repository, id, event_repository
        ).execute()
        return organizer
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
