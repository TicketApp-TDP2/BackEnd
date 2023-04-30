from fastapi.exceptions import HTTPException
from app.repositories.complaints import PersistentComplaintRepository
from app.repositories.event import PersistentEventRepository
from fastapi import status, APIRouter
from app.config.logger import setup_logger
from app.schemas.complaints import (
    ComplaintCreateSchema,
    ComplaintSchema,
    ComplaintOrganizerRankingSchema,
)
from app.commands.complaints import (
    CreateComplaintCommand,
    GetComplaintCommand,
    GetComplaintsByOrganizerCommand,
    GetComplaintsByEventCommand,
    GetComplaintsRankingByOrganizerCommand,
)
from app.utils.error import TicketAppError
from typing import List


logger = setup_logger(name=__name__)
router = APIRouter()


@router.post(
    '/complaints', status_code=status.HTTP_201_CREATED, response_model=ComplaintSchema
)
async def create_complaint(complaint_body: ComplaintCreateSchema):
    try:
        repository = PersistentComplaintRepository()
        event_repository = PersistentEventRepository()
        complaint = CreateComplaintCommand(
            repository, event_repository, complaint_body
        ).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
    return complaint


@router.get(
    '/complaints/{id}',
    status_code=status.HTTP_200_OK,
    response_model=ComplaintSchema,
    tags=["Complaints"],
)
async def get_complaint(id: str):
    try:
        repository = PersistentComplaintRepository()
        complaint = GetComplaintCommand(repository, id).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )

    return complaint


@router.get(
    '/complaints/organizer/{id}',
    status_code=status.HTTP_200_OK,
    response_model=List[ComplaintSchema],
    tags=["Complaints"],
)
async def get_complaint_by_organizer(id: str):
    try:
        repository = PersistentComplaintRepository()
        complaints = GetComplaintsByOrganizerCommand(repository, id).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )

    return complaints


@router.get(
    '/complaints/event/{id}',
    status_code=status.HTTP_200_OK,
    response_model=List[ComplaintSchema],
    tags=["Complaints"],
)
async def get_complaint_by_event(id: str):
    try:
        repository = PersistentComplaintRepository()
        complaints = GetComplaintsByEventCommand(repository, id).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )

    return complaints


@router.get(
    '/complaints/ranking/organizer',
    status_code=status.HTTP_200_OK,
    response_model=List[ComplaintOrganizerRankingSchema],
    tags=["Complaints"],
)
async def get_complaint_ranking_by_organizer():
    try:
        repository = PersistentComplaintRepository()
        ranking = GetComplaintsRankingByOrganizerCommand(repository).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )

    return ranking
