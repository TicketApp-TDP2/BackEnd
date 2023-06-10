class EventBookingsByHourStat:
    def __init__(
        self,
        time: str,
        bookings: int,
    ):
        self.time = time
        self.bookings = bookings


class EventStatesStat:
    def __init__(
        self,
        Borrador: int,
        Publicado: int,
        Finalizado: int,
        Cancelado: int,
        Suspendido: int,
    ):
        self.Borrador = Borrador
        self.Publicado = Publicado
        self.Finalizado = Finalizado
        self.Cancelado = Cancelado
        self.Suspendido = Suspendido


class OrganizerStat:
    def __init__(self, name: str, verified_bookings: int, id: str):
        self.name = name
        self.verified_bookings = verified_bookings
        self.id = id


class VerifiedBookingStat:
    def __init__(self, date: str, bookings: int):
        self.date = date
        self.bookings = bookings


class ComplaintsByTimeStat:
    def __init__(self, date: str, complaints: int):
        self.date = date
        self.complaints = complaints


class SuspendedEventStat:
    def __init__(self, date: str, suspended: int):
        self.date = date
        self.suspended = suspended


class EventByTimeStat:
    def __init__(self, date: str, events: int):
        self.date = date
        self.events = events


class EventPublishedByTimeStat:
    def __init__(self, date: str, events: int):
        self.date = date
        self.events = events


class AppStats:
    def __init__(
        self,
        event_states: EventStatesStat,
        top_organizers: list[OrganizerStat],
        verified_bookings: list[VerifiedBookingStat],
        complaints_by_time: list[ComplaintsByTimeStat],
        suspended_by_time: list[SuspendedEventStat],
        events_by_time: list[EventByTimeStat],
        events_published_by_time: list[EventPublishedByTimeStat],
    ):
        self.event_states = event_states
        self.top_organizers = top_organizers
        self.verified_bookings = verified_bookings
        self.complaints_by_time = complaints_by_time
        self.suspended_by_time = suspended_by_time
        self.events_by_time = events_by_time
        self.events_published_by_time = events_published_by_time
