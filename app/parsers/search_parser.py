from app.parsers.errors import LocationIncompleteError
from app.repositories.event import Search, SearchLocation
from app.schemas.event import SearchEvent


class SearchEventsParser:
    def parse(self, search: SearchEvent) -> Search:
        lat, lng = search.lat, search.lng

        if (lat and not lng) or (not lat and lng):
            raise LocationIncompleteError

        location = None
        if lat and lng:
            location = SearchLocation(lat=lat, lng=lng, dist=search.dist)

        return Search(
            location=location,
            organizer=search.organizer,
            type=search.type,
            limit=search.limit,
            name=search.name,
            only_published=search.only_published,
        )
