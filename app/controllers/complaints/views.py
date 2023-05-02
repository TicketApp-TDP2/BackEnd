from fastapi.exceptions import HTTPException
from app.repositories.complaints import PersistentComplaintRepository
from app.repositories.event import PersistentEventRepository
from fastapi import status, APIRouter, Depends
from app.config.logger import setup_logger
from app.schemas.complaints import (
    ComplaintCreateSchema,
    ComplaintSchema,
    ComplaintOrganizerRankingSchema,
    ComplaintEventRankingSchema,
    FilterComplaint,
)
from app.commands.complaints import (
    CreateComplaintCommand,
    GetComplaintCommand,
    GetComplaintsByOrganizerCommand,
    GetComplaintsByEventCommand,
    GetComplaintsRankingByOrganizerCommand,
    GetComplaintsRankingByEventCommand,
)
from app.utils.error import TicketAppError
from typing import List
from app.parsers.filter_parser import FilterComplaintsParser


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
async def get_complaint_by_organizer(id: str, params: FilterComplaint = Depends()):
    try:
        filter = FilterComplaintsParser().parse(params)
        repository = PersistentComplaintRepository()
        complaints = GetComplaintsByOrganizerCommand(repository, id, filter).execute()
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
async def get_complaint_by_event(id: str, params: FilterComplaint = Depends()):
    try:
        filter = FilterComplaintsParser().parse(params)
        repository = PersistentComplaintRepository()
        complaints = GetComplaintsByEventCommand(repository, id, filter).execute()
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
async def get_complaint_ranking_by_organizer(params: FilterComplaint = Depends()):
    try:
        filter = FilterComplaintsParser().parse(params)
        repository = PersistentComplaintRepository()
        ranking = GetComplaintsRankingByOrganizerCommand(repository, filter).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )

    return ranking


@router.get(
    '/complaints/ranking/event',
    status_code=status.HTTP_200_OK,
    response_model=List[ComplaintEventRankingSchema],
    tags=["Complaints"],
)
async def get_complaint_ranking_by_event(params: FilterComplaint = Depends()):
    try:
        filter = FilterComplaintsParser().parse(params)
        repository = PersistentComplaintRepository()
        ranking = GetComplaintsRankingByEventCommand(repository, filter).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )

    return ranking
