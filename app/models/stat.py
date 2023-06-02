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
    def __init__(self, name: str, events: int):
        self.name = name
        self.events = events


class AppStats:
    def __init__(
        self, event_states: EventStatesStat, top_organizers: list[OrganizerStat]
    ):
        self.event_states = event_states
        self.top_organizers = top_organizers
