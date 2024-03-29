import json
from app.repositories.event import (
    EventRepository,
)
from app.repositories.organizers import OrganizerRepository
from app.repositories.bookings import BookingRepository
from app.repositories.complaints import ComplaintRepository
from app.config.logger import setup_logger
from app.schemas.stats import StatParams, AppStatsSchema
from app.models.stat import AppStats, OrganizerStat

logger = setup_logger(__name__)


class GetStatsCommand:
    def __init__(
        self,
        event_repository: EventRepository,
        organizer_repository: OrganizerRepository,
        booking_repository: BookingRepository,
        complaint_repository: ComplaintRepository,
        params: StatParams,
    ):
        self.event_repository = event_repository
        self.params = params
        self.organizer_repository = organizer_repository
        self.booking_repository = booking_repository
        self.complaint_repository = complaint_repository

    def execute(self) -> AppStatsSchema:
        self.event_repository.update_state_all_events()
        event_states_stat = self.event_repository.get_event_states_stat(
            self.params.start_date, self.params.end_date
        )
        top_organizers_stat = self.event_repository.get_top_organizers_stat(
            self.params.start_date, self.params.end_date
        )
        top_organizers_stat = [
            OrganizerStat(
                name=self.get_organizer_name(organizer.id),
                verified_bookings=organizer.verified_bookings,
                id=organizer.id,
            )
            for organizer in top_organizers_stat
        ]
        verified_bookings_stat = self.booking_repository.get_verified_bookings_stat(
            self.params.start_date, self.params.end_date, self.params.group_by
        )
        complaints_by_time = self.complaint_repository.get_complaints_by_time(
            self.params.start_date, self.params.end_date
        )

        suspended_by_time = self.event_repository.get_suspended_by_time(
            self.params.start_date, self.params.end_date
        )

        events_by_time = self.event_repository.get_events_by_time(
            self.params.start_date, self.params.end_date
        )

        events_published_by_time = self.event_repository.get_events_published_by_time(
            self.params.start_date, self.params.end_date
        )

        stats = AppStats(
            event_states=event_states_stat,
            top_organizers=top_organizers_stat,
            verified_bookings=verified_bookings_stat,
            complaints_by_time=complaints_by_time,
            suspended_by_time=suspended_by_time,
            events_by_time=events_by_time,
            events_published_by_time=events_published_by_time,
        )
        return AppStatsSchema.from_model(stats)

    def get_organizer_name(self, organizer_id: str) -> str:
        organizer = self.organizer_repository.get_organizer(organizer_id)
        return f"{organizer.first_name} {organizer.last_name}"
