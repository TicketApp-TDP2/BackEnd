import json
from app.repositories.event import (
    EventRepository,
)
from app.config.logger import setup_logger
from app.schemas.stats import StatParams, AppStatsSchema
from app.models.stat import AppStats

logger = setup_logger(__name__)


class GetStatsCommand:
    def __init__(
        self,
        event_repository: EventRepository,
        params: StatParams,
    ):
        self.event_repository = event_repository
        self.params = params

    def execute(self) -> AppStatsSchema:
        self.event_repository.update_state_all_events()
        event_states_stat = self.event_repository.get_event_states_stat(
            self.params.start_date, self.params.end_date
        )
        stats = AppStats(event_states=event_states_stat)
        return AppStatsSchema.from_model(stats)
