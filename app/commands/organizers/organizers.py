from app.schemas.organizers import OrganizerCreateSchema, OrganizerSchema
from app.models.organizer import Organizer
from .errors import OrganizerAlreadyExistsError, OrganizerNotFoundError
from app.repositories.organizers import (
    OrganizerRepository,
)
from app.config.logger import setup_logger
import uuid

logger = setup_logger(__name__)


class CreateOrganizerCommand:
    def __init__(
        self,
        organizer_repository: OrganizerRepository,
        organizer: OrganizerCreateSchema,
    ):
        self.organizer_repository = organizer_repository
        self.organizer_data = organizer

    def execute(self) -> OrganizerSchema:
        organizer = Organizer(
            first_name=self.organizer_data.first_name,
            last_name=self.organizer_data.last_name,
            email=self.organizer_data.email,
            birth_date=self.organizer_data.birth_date,
            identification_number=self.organizer_data.identification_number,
            phone_number=self.organizer_data.phone_number,
            id=str(uuid.uuid4()),
        )
        already_exists = self.organizer_repository.organizer_exists_by_email(
            organizer.email
        )
        if already_exists:
            raise OrganizerAlreadyExistsError
        organizer = self.organizer_repository.add_organizer(organizer)

        return OrganizerSchema.from_model(organizer)


class GetOrganizerCommand:
    def __init__(self, organizer_repository: OrganizerRepository, _id: str):
        self.organizer_repository = organizer_repository
        self.id = _id

    def execute(self) -> OrganizerSchema:

        exists = self.organizer_repository.organizer_exists(self.id)
        if not exists:
            raise OrganizerNotFoundError
        organizer = self.organizer_repository.get_organizer(self.id)

        return OrganizerSchema.from_model(organizer)
