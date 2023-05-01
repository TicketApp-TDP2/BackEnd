from app.repositories.complaints import Filter
from app.schemas.complaints import FilterComplaint
from datetime import date


class FilterComplaintsParser:
    def parse(self, filter: FilterComplaint) -> Filter:
        return Filter(
            start=date.fromisoformat(filter.start) if filter.start else None,
            end=date.fromisoformat(filter.end) if filter.end else None,
        )
