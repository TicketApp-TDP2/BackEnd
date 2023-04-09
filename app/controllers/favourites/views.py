from fastapi.exceptions import HTTPException
from app.commands.favourites.favourites import (
    AddFavouriteCommand,
    DeleteFavouriteCommand,
    GetFavouritesCommand,
)
from app.repositories.event import PersistentEventRepository
from typing import List
from fastapi import status, APIRouter
from app.config.logger import setup_logger
from app.repositories.users import PersistentUserRepository
from app.schemas.event import (
    EventSchema,
)
from app.schemas.favourite import FavouriteSchema
from app.utils.error import TicketAppError


logger = setup_logger(name=__name__)
router = APIRouter()


@router.post(
    '/users/{user_id}/favourites',
    status_code=status.HTTP_201_CREATED,
    response_model=FavouriteSchema,
    tags=["Users"]
)
async def add_favourite(user_id: str, favourite_body: FavouriteSchema):
    try:
        user_repository = PersistentUserRepository()
        event_repository = PersistentEventRepository()
        AddFavouriteCommand(
            user_repository, event_repository, user_id, favourite_body
        ).execute()

        return favourite_body
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )


@router.delete(
    '/users/{user_id}/favourites/{event_id}',
    status_code=status.HTTP_200_OK,
    tags=["Users"]
)
async def delete_favourite(user_id: str, event_id: str):
    try:
        user_repository = PersistentUserRepository()
        DeleteFavouriteCommand(user_repository, user_id, event_id).execute()
        return True
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )


@router.get(
    '/users/{user_id}/favourites',
    status_code=status.HTTP_200_OK,
    response_model=List[EventSchema],
    tags=["Users"]
)
async def get_favourites(user_id: str):
    try:
        user_repository = PersistentUserRepository()
        event_repository = PersistentEventRepository()
        favourites = GetFavouritesCommand(
            user_repository, event_repository, user_id
        ).execute()

    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )

    return favourites
