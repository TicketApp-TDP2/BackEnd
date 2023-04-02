from fastapi.exceptions import HTTPException
from app.repositories.event import PersistentEventRepository
from app.commands.events.events import SearchEventsCommand
from app.parsers.search_parser import SearchEventsParser
from typing import List
from fastapi import Depends, status, APIRouter
from app.config.logger import setup_logger
from app.schemas.event import (
    EventCreateSchema,
    EventSchema,
    SearchEvent,
)
from app.commands.events import (
    CreateEventCommand,
    GetEventCommand,
)
from app.utils.error import TicketAppError


logger = setup_logger(name=__name__)
router = APIRouter()


@router.post(
    '/events',
    status_code=status.HTTP_201_CREATED,
    response_model=EventSchema, tags=["Events"]
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
    response_model=EventSchema, tags=["Events"]
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
    response_model=List[EventSchema], tags=["Events"]
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
