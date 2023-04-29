from fastapi.exceptions import HTTPException
from app.repositories.complaints import PersistentComplaintRepository
from fastapi import status, APIRouter
from app.config.logger import setup_logger
from app.schemas.complaints import ComplaintCreateSchema, ComplaintSchema
from app.commands.complaints import CreateComplaintCommand
from app.utils.error import TicketAppError


logger = setup_logger(name=__name__)
router = APIRouter()


@router.post(
    '/complaints', status_code=status.HTTP_201_CREATED, response_model=ComplaintSchema
)
async def create_complaint(complaint_body: ComplaintCreateSchema):
    try:
        repository = PersistentComplaintRepository()
        complaint = CreateComplaintCommand(repository, complaint_body).execute()
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
    return complaint
