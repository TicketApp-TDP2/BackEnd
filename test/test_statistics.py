from fastapi.testclient import TestClient
import pytest
from test.utils import generate_invalid, mock_date

from app.app import app

client = TestClient(app)

URI = 'api/stats'


def create_user(fields={}):
    body = {
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email@mail.com',
        'identification_number': '40400400',
        'phone_number': '1180808080',
        "birth_date": "1990-01-01",
        "id": "784578",
    }

    for k, v in fields.items():
        body[k] = v

    response = client.post("api/users", json=body)
    return response.json()


def create_organizer(fields={}):
    body = {
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email@mail.com',
        'profession': 'profession',
        'about_me': 'about_me',
        'profile_picture': 'profile_picture',
        'id': '123',
    }

    for k, v in fields.items():
        body[k] = v

    response = client.post("api/organizers", json=body)
    return response.json()


def create_event(fields={}):
    body = {
        'name': 'aName',
        'description': 'aDescription',
        'location': {
            'description': 'a location description',
            'lat': 23.4,
            'lng': 32.23,
        },
        'type': 'Danza',
        'images': ['image1', 'image2', 'image3'],
        'preview_image': 'preview_image',
        'date': '2023-03-29',
        'start_time': '09:00:00',
        'end_time': '12:00:00',
        'scan_time': 10,
        'organizer': 'anOwner',
        'agenda': [
            {
                'time_init': '09:00',
                'time_end': '12:00',
                'owner': 'Pepe Cibrian',
                'title': 'Noche de teatro en Bs As',
                'description': 'Una noche de teatro unica',
            }
        ],
        'vacants': 3,
        'FAQ': [
            {
                'question': 'se pueden llevar alimentos?',
                'answer': 'No. No se permiten alimentos ni bebidas en el lugar',
            }
        ],
    }

    for k, v in fields.items():
        body[k] = v

    response = client.post("api/events", json=body)
    return response.json()


@pytest.fixture(autouse=True)
def clear_db():
    # This runs before each test

    yield

    # Ant this runs after each test
    client.post('api/reset')


def test_stat_event_state(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 6, 'hour': 2})
    organizer = create_organizer()
    event_borrador = create_event({"date": "2022-05-10"})
    event_publicado1 = create_event({"date": "2022-05-10"})
    event_publicado2 = create_event({"date": "2022-05-10"})
    event_cancelado = create_event({"date": "2022-05-10"})
    event_terminado = create_event(
        {
            "date": "2022-05-08",
            "start_time": "14:00",
            "end_time": "15:00",
            'agenda': [
                {
                    'time_init': '14:00',
                    'time_end': '15:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                }
            ],
        }
    )
    event_terminado2 = create_event({"date": "2022-05-07"})
    event_suspendido = create_event(
        {"date": "2022-05-10", "organizer": organizer["id"]}
    )

    client.put(f'api/events/{event_publicado1["id"]}/publish')
    client.put(f'api/events/{event_publicado2["id"]}/publish')

    client.put(f'api/events/{event_cancelado["id"]}/cancel')

    client.put(f'api/events/{event_suspendido["id"]}/publish')
    client.put(f'api/events/{event_suspendido["id"]}/suspend')

    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 8, 'hour': 16})

    response = client.get(URI + '?start_date=2022-05-05&end_date=2022-05-07')
    assert response.status_code == 200
    data = response.json()
    assert data["event_states"] == {
        "Borrador": 1,
        "Publicado": 2,
        "Cancelado": 1,
        "Finalizado": 2,
        "Suspendido": 1,
    }


# test alguno con 0
