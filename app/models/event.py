from __future__ import annotations
from datetime import date, time
from enum import Enum
import uuid


class Location:
    def __init__(self, description: str, lat: float, lng: float):
        self.description = description
        self.lat = lat
        self.lng = lng


class Agenda:
    def __init__(
        self, time_init: str, time_end: str, owner: str, title: str, description: str
    ):
        self.time_init = time_init
        self.time_end = time_end
        self.owner = owner
        self.title = title
        self.description = description


class Faq:
    def __init__(self, question: str, answer: str):
        self.question = question
        self.answer = answer


class Collaborator:
    def __init__(self, id: str, email: str):
        self.id = id
        self.email = email

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Type(Enum):
    Arte_y_Cultura = "Arte y Cultura"
    Musica = "Música"
    Danza = "Danza"
    Moda = "Moda"
    Bellas_Artes = "Bellas Artes"
    Cine = "Cine"
    Turismo = "Turismo"
    Deporte = "Deporte"
    Gastronomia = "Gastronomía"
    Educacion = "Educación"
    Empresa = "Empresa"
    Capacitacion = "Capacitación"
    Entretenimiento = "Entretenimiento"
    Tecnologia = "Tecnología"
    Infantil = "Infantil"
    Debate = "Debate"
    Conmemoracion = "Conmemoración"
    Religion = "Religión"
    Convencion = "Convención"


class State(Enum):
    Borrador = "Borrador"
    Publicado = "Publicado"
    Finalizado = "Finalizado"
    Cancelado = "Cancelado"
    Suspendido = "Suspendido"


class Event:
    def __init__(
        self,
        name: str,
        description: str,
        location: Location,
        type: Type,
        images: list[str],
        preview_image: str,
        date: date,
        start_time: time,
        end_time: time,
        scan_time: int,
        organizer: str,
        agenda: list[Agenda],
        vacants: int,
        vacants_left: int,
        FAQ: list[Faq],
        id: str,
        state: State,
        verified_vacants: int,
        collaborators: list[Collaborator],
    ):
        self.name = name
        self.description = description
        self.location = location
        self.type = type
        self.images = images
        self.preview_image = preview_image
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.scan_time = scan_time
        self.organizer = organizer
        self.agenda = agenda
        self.vacants = vacants
        self.vacants_left = vacants_left
        self.FAQ = FAQ
        self.id = id
        self.state = state
        self.verified_vacants = verified_vacants
        self.collaborators = collaborators

    @classmethod
    def new(
        cls,
        name: str,
        description: str,
        location: Location,
        type: Type,
        images: list[str],
        preview_image: str,
        date: date,
        start_time: time,
        end_time: time,
        scan_time: int,
        organizer: str,
        agenda: list[Agenda],
        vacants: int,
        vacants_left: int,
        FAQ: list[Faq],
    ) -> Event:
        return Event(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            location=location,
            type=type,
            images=images,
            preview_image=preview_image,
            date=date,
            start_time=start_time,
            end_time=end_time,
            scan_time=scan_time,
            organizer=organizer,
            agenda=agenda,
            vacants=vacants,
            vacants_left=vacants_left,
            FAQ=FAQ,
            state=State.Borrador,
            verified_vacants=0,
            collaborators=[],
        )
