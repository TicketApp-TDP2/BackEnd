from __future__ import annotations
from datetime import date, time
from enum import Enum
import uuid


class Location:
    def __init__(self, description: str, lat: float, lng: float):
        self.description = description
        self.lat = lat
        self.lng = lng


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
        organizer: str,
        agenda: list[tuple[str, str, str, str, str]],
        vacants: int,
        FAQ: list[tuple[str, str]],
        id: str,
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
        self.organizer = organizer
        self.agenda = agenda
        self.vacants = vacants
        self.FAQ = FAQ
        self.id = id

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
        organizer: str,
        agenda: list[tuple[str, str, str, str, str]],
        vacants: int,
        FAQ: list[tuple[str, str]],
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
            organizer=organizer,
            agenda=agenda,
            vacants=vacants,
            FAQ=FAQ,
        )
