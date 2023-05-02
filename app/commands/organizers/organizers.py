from app.schemas.organizers import (
    OrganizerCreateSchema,
    OrganizerSchema,
    OrganizerUpdateSchema,
)
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
            last_name=self.organizer_data.last_name
            if self.organizer_data.last_name
            else self.organizer_data.first_name,
            email=self.organizer_data.email,
            profession=self.organizer_data.profession,
            about_me=self.organizer_data.about_me,
            profile_picture=self.organizer_data.profile_picture,
            id=self.organizer_data.id,
            suspended=False,
        )
        already_exists = self.organizer_repository.organizer_exists_by_email(
            organizer.email
        ) or self.organizer_repository.organizer_exists(organizer.id)
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


class UpdateOrganizerCommand:
    def __init__(
        self,
        organizer_repository: OrganizerRepository,
        update: OrganizerUpdateSchema,
        id: str,
    ):
        self.organizer_repository = organizer_repository
        self.update = update
        self.id = id

    def execute(self) -> OrganizerSchema:
        organizer = self.organizer_repository.get_organizer(self.id)
        organizer = Organizer(
            first_name=self.update.first_name or organizer.first_name,
            last_name=self.update.last_name or organizer.last_name,
            email=organizer.email,
            id=organizer.id,
            profession=self.update.profession or organizer.profession,
            about_me=self.update.about_me or organizer.about_me,
            profile_picture=self.update.profile_picture,
            suspended=organizer.suspended,
        )
        organizer = self.organizer_repository.update_organizer(organizer)

        return OrganizerSchema.from_model(organizer)


class SuspendOrganizerCommand:
    def __init__(self, organizer_repository: OrganizerRepository, _id: str):
        self.organizer_repository = organizer_repository
        self.id = _id

    def execute(self) -> OrganizerSchema:
        exists = self.organizer_repository.organizer_exists(self.id)
        if not exists:
            raise OrganizerNotFoundError
        organizer = self.organizer_repository.suspend_organizer(self.id)
        return OrganizerSchema.from_model(organizer)


class UnSuspendOrganizerCommand:
    def __init__(self, organizer_repository: OrganizerRepository, _id: str):
        self.organizer_repository = organizer_repository
        self.id = _id

    def execute(self) -> OrganizerSchema:
        exists = self.organizer_repository.organizer_exists(self.id)
        if not exists:
            raise OrganizerNotFoundError
        organizer = self.organizer_repository.unsuspend_organizer(self.id)
        return OrganizerSchema.from_model(organizer)
