from fastapi.exceptions import HTTPException
from app.repositories.event import PersistentEventRepository
from app.repositories.organizers import PersistentOrganizerRepository
from app.commands.events.events import SearchEventsCommand
from app.parsers.search_parser import SearchEventsParser
from typing import List
from fastapi import Depends, status, APIRouter
from app.config.logger import setup_logger
from app.schemas.event import (
    EventCreateSchema,
    EventSchema,
    SearchEvent,
    EventUpdateSchema,
)
from app.commands.events import (
    CreateEventCommand,
    GetEventCommand,
    PublishEventCommand,
    CancelEventCommand,
    UpdateEventCommand,
    SuspendEventCommand,
    UnSuspendEventCommand,
    AddCollaboratorEventCommand,
    RemoveCollaboratorEventCommand,
)
from app.utils.error import TicketAppError


logger = setup_logger(name=__name__)
router = APIRouter()


@router.post(
    '/events',
    status_code=status.HTTP_201_CREATED,
    response_model=EventSchema,
    tags=["Events"],
)
async def create_event(event_body: EventCreateSchema):
    try:
        repository = PersistentEventRepository()
        event = CreateEventCommand(repository, event_body).execute()
        return event
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )


@router.get(
    '/events/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EventSchema,
    tags=["Events"],
)
async def get_event(id: str):
    try:
        repository = PersistentEventRepository()
        event = GetEventCommand(repository, id).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )

    return event


@router.get(
    '/events',
    status_code=status.HTTP_200_OK,
    response_model=List[EventSchema],
    tags=["Events"],
)
async def search_events(params: SearchEvent = Depends()):
    try:
        search = SearchEventsParser().parse(params)
        repository = PersistentEventRepository()
        events = SearchEventsCommand(repository, search).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )

    return events


@router.put(
    '/events/{id}/publish',
    status_code=status.HTTP_200_OK,
    response_model=EventSchema,
    tags=["Events"],
)
async def publish_event(id: str):
    try:
        repository = PersistentEventRepository()
        event = PublishEventCommand(repository, id).execute()
        return event
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )


@router.put(
    '/events/{id}/cancel',
    status_code=status.HTTP_200_OK,
    response_model=EventSchema,
    tags=["Events"],
)
async def cancel_event(id: str):
    try:
        repository = PersistentEventRepository()
        event = CancelEventCommand(repository, id).execute()
        return event
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )


@router.put(
    '/events/{id}',
    status_code=status.HTTP_201_CREATED,
    response_model=EventSchema,
    tags=["Events"],
)
async def update_event(id: str, update_body: EventUpdateSchema):
    try:
        repository = PersistentEventRepository()
        user = UpdateEventCommand(repository, update_body, id).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
    return user


@router.put(
    '/events/{id}/suspend',
    status_code=status.HTTP_200_OK,
    response_model=EventSchema,
    tags=["Events"],
)
async def suspend_event(id: str):
    try:
        repository = PersistentEventRepository()
        event = SuspendEventCommand(repository, id).execute()
        return event
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )


@router.put(
    '/events/{id}/unsuspend',
    status_code=status.HTTP_200_OK,
    response_model=EventSchema,
    tags=["Events"],
)
async def unsuspend_event(id: str):
    try:
        repository = PersistentEventRepository()
        event = UnSuspendEventCommand(repository, id).execute()
        return event
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )


@router.put(
    '/events/{id}/add_collaborator/{collaborator_email}',
    status_code=status.HTTP_200_OK,
    response_model=EventSchema,
    tags=["Events"],
)
async def add_collaborator_event(id: str, collaborator_email: str):
    try:
        repository = PersistentEventRepository()
        organizer_repository = PersistentOrganizerRepository()
        event = AddCollaboratorEventCommand(
            repository, organizer_repository, id, collaborator_email
        ).execute()
        return event
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )


@router.put(
    '/events/{id}/remove_collaborator/{collaborator_id}',
    status_code=status.HTTP_200_OK,
    response_model=EventSchema,
    tags=["Events"],
)
async def remove_collaborator_event(id: str, collaborator_id: str):
    try:
        repository = PersistentEventRepository()
        organizer_repository = PersistentOrganizerRepository()
        event = RemoveCollaboratorEventCommand(
            repository, organizer_repository, id, collaborator_id
        ).execute()
        return event
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
