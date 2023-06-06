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
    event_borrador = create_event({"date": "2022-05-10", "organizer": organizer["id"]})
    event_publicado1 = create_event(
        {"date": "2022-05-10", "organizer": organizer["id"]}
    )
    event_publicado2 = create_event(
        {"date": "2022-05-10", "organizer": organizer["id"]}
    )
    event_cancelado = create_event({"date": "2022-05-10", "organizer": organizer["id"]})
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
            "organizer": organizer["id"],
        }
    )
    event_terminado2 = create_event(
        {"date": "2022-05-07", "organizer": organizer["id"]}
    )
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


def test_stat_event_state_with_some_0(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 6, 'hour': 2})
    organizer = create_organizer()
    event_borrador = create_event({"date": "2022-05-10", "organizer": organizer["id"]})
    event_publicado1 = create_event(
        {"date": "2022-05-10", "organizer": organizer["id"]}
    )
    event_publicado2 = create_event(
        {"date": "2022-05-10", "organizer": organizer["id"]}
    )
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
            "organizer": organizer["id"],
        }
    )
    event_terminado2 = create_event(
        {"date": "2022-05-07", "organizer": organizer["id"]}
    )
    event_suspendido = create_event(
        {"date": "2022-05-10", "organizer": organizer["id"]}
    )

    client.put(f'api/events/{event_publicado1["id"]}/publish')
    client.put(f'api/events/{event_publicado2["id"]}/publish')

    client.put(f'api/events/{event_suspendido["id"]}/publish')
    client.put(f'api/events/{event_suspendido["id"]}/suspend')

    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 8, 'hour': 16})

    response = client.get(URI + '?start_date=2022-05-05&end_date=2022-05-07')
    assert response.status_code == 200
    data = response.json()
    assert data["event_states"] == {
        "Borrador": 1,
        "Publicado": 2,
        "Cancelado": 0,
        "Finalizado": 2,
        "Suspendido": 1,
    }


def test_stat_event_state_diferrent_dates(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 4, 'hour': 2})
    organizer = create_organizer()
    event_borrador = create_event({"date": "2022-05-10", "organizer": organizer["id"]})
    event_publicado1 = create_event(
        {"date": "2022-05-10", "organizer": organizer["id"]}
    )
    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 5, 'hour': 2})
    event_publicado2 = create_event(
        {"date": "2022-05-10", "organizer": organizer["id"]}
    )
    event_cancelado = create_event({"date": "2022-05-10", "organizer": organizer["id"]})
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
            "organizer": organizer["id"],
        }
    )
    event_terminado2 = create_event(
        {"date": "2022-05-07", "organizer": organizer["id"]}
    )
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
        "Borrador": 0,
        "Publicado": 1,
        "Cancelado": 1,
        "Finalizado": 2,
        "Suspendido": 1,
    }


def test_stat_top_organizers(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 6, 'hour': 2})
    organizer = create_organizer(
        {
            "first_name": "organizer1",
            "last_name": "a",
            "id": "123",
            "email": "organizer1@mail.com",
        }
    )
    organizer2 = create_organizer(
        {
            "first_name": "organizer2",
            "last_name": "b",
            "id": "223",
            "email": "organizer2@mail.com",
        }
    )
    organizer3 = create_organizer(
        {
            "first_name": "organizer3",
            "last_name": "c",
            "id": "323",
            "email": "organizer3@mail.com",
        }
    )
    organizer4 = create_organizer(
        {
            "first_name": "organizer4",
            "last_name": "d",
            "id": "423",
            "email": "organizer4@mail.com",
        }
    )

    user = create_user({"id": "123", "email": "user@mail.com"})
    user2 = create_user({"id": "1223", "email": "user2@mail.com"})

    event = create_event(
        {"organizer": organizer["id"], "date": "2022-05-10"}
    )  # Publicado
    client.put(f'api/events/{event["id"]}/publish')
    booking_body = {
        "event_id": event['id'],
        "reserver_id": user['id'],
    }
    response = client.post('api/bookings', json=booking_body)
    body = {"event_id": event["id"]}
    client.put('api/bookings' + f'/{response.json()["id"]}/verify', json=body)
    create_event({"organizer": organizer["id"], "date": "2022-05-10"})  # Borrador

    event = create_event(
        {"organizer": organizer2["id"], "date": "2022-05-10"}
    )  # Publicado
    client.put(f'api/events/{event["id"]}/publish')
    booking_body = {
        "event_id": event['id'],
        "reserver_id": user['id'],
    }
    response = client.post('api/bookings', json=booking_body)
    body = {"event_id": event["id"]}
    client.put('api/bookings' + f'/{response.json()["id"]}/verify', json=body)
    booking_body = {
        "event_id": event['id'],
        "reserver_id": user2['id'],
    }
    response = client.post('api/bookings', json=booking_body)
    body = {"event_id": event["id"]}
    client.put('api/bookings' + f'/{response.json()["id"]}/verify', json=body)

    event = create_event(
        {"organizer": organizer2["id"], "date": "2022-05-06"}
    )  # Terminado
    client.put(f'api/events/{event["id"]}/publish')

    event = create_event(
        {"organizer": organizer3["id"], "date": "2022-05-10"}
    )  # Cancelado
    client.put(f'api/events/{event["id"]}/cancel')

    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 7, 'hour': 2})
    response = client.get(URI + '?start_date=2022-05-05&end_date=2022-05-07')
    assert response.status_code == 200
    data = response.json()
    assert data["top_organizers"] == [
        {"name": "organizer2 b", "verified_bookings": 2, 'id': '223'},
        {"name": "organizer1 a", "verified_bookings": 1, 'id': '123'},
    ]


def test_stat_top_organizers_different_dates(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 4, 'hour': 2})
    organizer = create_organizer(
        {
            "first_name": "organizer1",
            "last_name": "a",
            "id": "123",
            "email": "organizer1@mail.com",
        }
    )
    organizer2 = create_organizer(
        {
            "first_name": "organizer2",
            "last_name": "b",
            "id": "223",
            "email": "organizer2@mail.com",
        }
    )
    organizer3 = create_organizer(
        {
            "first_name": "organizer3",
            "last_name": "c",
            "id": "323",
            "email": "organizer3@mail.com",
        }
    )
    organizer4 = create_organizer(
        {
            "first_name": "organizer4",
            "last_name": "d",
            "id": "423",
            "email": "organizer4@mail.com",
        }
    )

    user = create_user({"id": "123", "email": "user@mail.com"})
    user2 = create_user({"id": "1223", "email": "user2@mail.com"})

    event = create_event(
        {"organizer": organizer["id"], "date": "2022-05-10"}
    )  # Publicado
    client.put(f'api/events/{event["id"]}/publish')
    booking_body = {
        "event_id": event['id'],
        "reserver_id": user['id'],
    }
    response = client.post('api/bookings', json=booking_body)
    body = {"event_id": event["id"]}
    client.put('api/bookings' + f'/{response.json()["id"]}/verify', json=body)

    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 5, 'hour': 2})
    event = create_event(
        {"organizer": organizer["id"], "date": "2022-05-10"}
    )  # Publicado
    client.put(f'api/events/{event["id"]}/publish')
    booking_body = {
        "event_id": event['id'],
        "reserver_id": user['id'],
    }
    response = client.post('api/bookings', json=booking_body)
    body = {"event_id": event["id"]}
    client.put('api/bookings' + f'/{response.json()["id"]}/verify', json=body)

    event = create_event(
        {"organizer": organizer2["id"], "date": "2022-05-10"}
    )  # Publicado
    client.put(f'api/events/{event["id"]}/publish')
    booking_body = {
        "event_id": event['id'],
        "reserver_id": user['id'],
    }
    response = client.post('api/bookings', json=booking_body)
    body = {"event_id": event["id"]}
    client.put('api/bookings' + f'/{response.json()["id"]}/verify', json=body)

    event = create_event(
        {"organizer": organizer2["id"], "date": "2022-05-06"}
    )  # Terminado
    client.put(f'api/events/{event["id"]}/publish')
    booking_body = {
        "event_id": event['id'],
        "reserver_id": user['id'],
    }
    response = client.post('api/bookings', json=booking_body)
    body = {"event_id": event["id"]}
    client.put('api/bookings' + f'/{response.json()["id"]}/verify', json=body)

    event = create_event({"organizer": organizer3["id"], "date": "2022-05-06"})

    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 7, 'hour': 2})
    response = client.get(URI + '?start_date=2022-05-05&end_date=2022-05-07')
    assert response.status_code == 200
    data = response.json()
    assert data["top_organizers"] == [
        {"name": "organizer2 b", "verified_bookings": 2, "id": "223"},
        {"name": "organizer1 a", "verified_bookings": 1, "id": "123"},
    ]


def test_stat_top_organizers_more_than_10(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 6, 'hour': 2})
    organizers = [
        create_organizer(
            {
                "first_name": f"organizer{i}",
                "last_name": f"{i}",
                "id": f"{i}23",
                "email": f"organizer{i}@mail.com",
            }
        )
        for i in range(1, 12)
    ]
    user = create_user({"id": "123", "email": "user@mail.com"})

    for organizer in organizers:
        event = create_event({"organizer": organizer["id"], "date": "2022-05-10"})
        client.put(f'api/events/{event["id"]}/publish')
        booking_body = {
            "event_id": event['id'],
            "reserver_id": user['id'],
        }
        response = client.post('api/bookings', json=booking_body)
        body = {"event_id": event["id"]}
        client.put('api/bookings' + f'/{response.json()["id"]}/verify', json=body)

    response = client.get(URI + '?start_date=2022-05-05&end_date=2022-05-07')
    assert response.status_code == 200
    data = response.json()
    assert len(data["top_organizers"]) == 10


def test_stat_booking_verified_by_day(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 6, 'hour': 2})
    organizer = create_organizer(
        {
            "first_name": "organizer1",
            "last_name": "a",
            "id": "123",
            "email": "organizer1@mail.com",
        }
    )

    events = [
        create_event({"organizer": organizer["id"], "date": "2022-05-10"})
        for i in range(3)
    ]
    for event in events:
        client.put(f'api/events/{event["id"]}/publish')

    users = [
        create_user({"id": f"123{i}", "email": f"user{i}@mail.com"}) for i in range(3)
    ]
    bookings = []
    for event in events:
        for user in users:
            booking_body = {
                "event_id": event['id'],
                "reserver_id": user['id'],
            }
            response = client.post('api/bookings', json=booking_body)
            bookings.append(response.json()["id"])

    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 7, 'hour': 2})
    body = {"event_id": events[0]["id"]}
    client.put('api/bookings' + f'/{bookings[0]}/verify', json=body)
    client.put('api/bookings' + f'/{bookings[1]}/verify', json=body)

    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 8, 'hour': 2})
    body = {"event_id": events[1]["id"]}
    client.put('api/bookings' + f'/{bookings[3]}/verify', json=body)
    client.put('api/bookings' + f'/{bookings[4]}/verify', json=body)
    client.put('api/bookings' + f'/{bookings[5]}/verify', json=body)

    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 9, 'hour': 2})
    body = {"event_id": events[2]["id"]}
    client.put('api/bookings' + f'/{bookings[6]}/verify', json=body)
    client.put('api/bookings' + f'/{bookings[7]}/verify', json=body)

    response = client.get(URI + '?start_date=2022-05-07&end_date=2022-05-10')
    assert response.status_code == 200
    data = response.json()
    assert data["verified_bookings"] == [
        {"date": "2022-05-07", "bookings": 2},
        {"date": "2022-05-08", "bookings": 3},
        {"date": "2022-05-09", "bookings": 2},
    ]


def test_stat_booking_verified_by_month(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 4, 'day': 6, 'hour': 2})
    organizer = create_organizer(
        {
            "first_name": "organizer1",
            "last_name": "a",
            "id": "123",
            "email": "organizer1@mail.com",
        }
    )

    events = [
        create_event({"organizer": organizer["id"], "date": "2022-08-10"})
        for i in range(3)
    ]
    for event in events:
        client.put(f'api/events/{event["id"]}/publish')

    users = [
        create_user({"id": f"123{i}", "email": f"user{i}@mail.com"}) for i in range(3)
    ]
    bookings = []
    for event in events:
        for user in users:
            booking_body = {
                "event_id": event['id'],
                "reserver_id": user['id'],
            }
            response = client.post('api/bookings', json=booking_body)
            bookings.append(response.json()["id"])

    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 7, 'hour': 2})
    body = {"event_id": events[0]["id"]}
    client.put('api/bookings' + f'/{bookings[0]}/verify', json=body)
    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 15, 'hour': 2})
    client.put('api/bookings' + f'/{bookings[1]}/verify', json=body)

    mock_date(monkeypatch, {'year': 2022, 'month': 6, 'day': 8, 'hour': 2})
    body = {"event_id": events[1]["id"]}
    client.put('api/bookings' + f'/{bookings[3]}/verify', json=body)
    mock_date(monkeypatch, {'year': 2022, 'month': 6, 'day': 12, 'hour': 2})
    client.put('api/bookings' + f'/{bookings[4]}/verify', json=body)
    client.put('api/bookings' + f'/{bookings[5]}/verify', json=body)

    mock_date(monkeypatch, {'year': 2022, 'month': 7, 'day': 9, 'hour': 2})
    body = {"event_id": events[2]["id"]}
    client.put('api/bookings' + f'/{bookings[6]}/verify', json=body)
    client.put('api/bookings' + f'/{bookings[7]}/verify', json=body)

    response = client.get(
        URI + '?start_date=2022-05-07&end_date=2022-07-10&group_by=month'
    )
    assert response.status_code == 200
    data = response.json()
    assert data["verified_bookings"] == [
        {"date": "2022-05", "bookings": 2},
        {"date": "2022-06", "bookings": 3},
        {"date": "2022-07", "bookings": 2},
    ]


def test_stat_booking_verified_by_year(monkeypatch):
    mock_date(monkeypatch, {'year': 2020, 'month': 4, 'day': 6, 'hour': 2})
    organizer = create_organizer(
        {
            "first_name": "organizer1",
            "last_name": "a",
            "id": "123",
            "email": "organizer1@mail.com",
        }
    )

    events = [
        create_event({"organizer": organizer["id"], "date": "2022-08-10"})
        for i in range(3)
    ]
    for event in events:
        client.put(f'api/events/{event["id"]}/publish')

    users = [
        create_user({"id": f"123{i}", "email": f"user{i}@mail.com"}) for i in range(3)
    ]
    bookings = []
    for event in events:
        for user in users:
            booking_body = {
                "event_id": event['id'],
                "reserver_id": user['id'],
            }
            response = client.post('api/bookings', json=booking_body)
            bookings.append(response.json()["id"])

    mock_date(monkeypatch, {'year': 2020, 'month': 5, 'day': 7, 'hour': 2})
    body = {"event_id": events[0]["id"]}
    client.put('api/bookings' + f'/{bookings[0]}/verify', json=body)
    mock_date(monkeypatch, {'year': 2020, 'month': 7, 'day': 15, 'hour': 2})
    client.put('api/bookings' + f'/{bookings[1]}/verify', json=body)

    mock_date(monkeypatch, {'year': 2021, 'month': 6, 'day': 8, 'hour': 2})
    body = {"event_id": events[1]["id"]}
    client.put('api/bookings' + f'/{bookings[3]}/verify', json=body)
    mock_date(monkeypatch, {'year': 2021, 'month': 6, 'day': 12, 'hour': 2})
    client.put('api/bookings' + f'/{bookings[4]}/verify', json=body)
    client.put('api/bookings' + f'/{bookings[5]}/verify', json=body)

    mock_date(monkeypatch, {'year': 2022, 'month': 7, 'day': 9, 'hour': 2})
    body = {"event_id": events[2]["id"]}
    client.put('api/bookings' + f'/{bookings[6]}/verify', json=body)
    client.put('api/bookings' + f'/{bookings[7]}/verify', json=body)

    response = client.get(
        URI + '?start_date=2020-05-07&end_date=2022-07-10&group_by=year'
    )
    assert response.status_code == 200
    data = response.json()
    assert data["verified_bookings"] == [
        {"date": "2020", "bookings": 2},
        {"date": "2021", "bookings": 3},
        {"date": "2022", "bookings": 2},
    ]


def test_stat_booking_verified_by_year_date_filter(monkeypatch):
    mock_date(monkeypatch, {'year': 2020, 'month': 4, 'day': 6, 'hour': 2})
    organizer = create_organizer(
        {
            "first_name": "organizer1",
            "last_name": "a",
            "id": "123",
            "email": "organizer1@mail.com",
        }
    )

    events = [
        create_event({"organizer": organizer["id"], "date": "2022-08-10"})
        for i in range(3)
    ]
    for event in events:
        client.put(f'api/events/{event["id"]}/publish')

    users = [
        create_user({"id": f"123{i}", "email": f"user{i}@mail.com"}) for i in range(3)
    ]
    bookings = []
    for event in events:
        for user in users:
            booking_body = {
                "event_id": event['id'],
                "reserver_id": user['id'],
            }
            response = client.post('api/bookings', json=booking_body)
            bookings.append(response.json()["id"])

    mock_date(monkeypatch, {'year': 2020, 'month': 5, 'day': 7, 'hour': 2})
    body = {"event_id": events[0]["id"]}
    client.put('api/bookings' + f'/{bookings[0]}/verify', json=body)
    mock_date(monkeypatch, {'year': 2020, 'month': 7, 'day': 15, 'hour': 2})
    client.put('api/bookings' + f'/{bookings[1]}/verify', json=body)

    mock_date(monkeypatch, {'year': 2021, 'month': 6, 'day': 8, 'hour': 2})
    body = {"event_id": events[1]["id"]}
    client.put('api/bookings' + f'/{bookings[3]}/verify', json=body)
    mock_date(monkeypatch, {'year': 2021, 'month': 6, 'day': 12, 'hour': 2})
    client.put('api/bookings' + f'/{bookings[4]}/verify', json=body)
    client.put('api/bookings' + f'/{bookings[5]}/verify', json=body)

    mock_date(monkeypatch, {'year': 2022, 'month': 7, 'day': 9, 'hour': 2})
    body = {"event_id": events[2]["id"]}
    client.put('api/bookings' + f'/{bookings[6]}/verify', json=body)
    client.put('api/bookings' + f'/{bookings[7]}/verify', json=body)

    response = client.get(
        URI + '?start_date=2022-05-07&end_date=2022-07-10&group_by=year'
    )
    assert response.status_code == 200
    data = response.json()
    assert data["verified_bookings"] == [{"date": "2022", "bookings": 2}]


def test_complaint_stat(monkeypatch):
    mock_date(monkeypatch, {'year': 2020, 'month': 4, 'day': 6, 'hour': 2})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})
    complainer2 = create_user({'email': 'complainer2@mail.com', 'id': '2342'})
    event2 = create_event({'organizer': organizer['id']})

    mock_date(monkeypatch, {'year': 2022, 'month': 4, 'day': 6, 'hour': 2})
    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }
    client.post("api/complaints", json=complaint_body)
    mock_date(monkeypatch, {'year': 2022, 'month': 4, 'day': 12, 'hour': 2})
    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer2['id'],
        "type": "Spam",
        "description": "description",
    }
    client.post("api/complaints", json=complaint_body)
    mock_date(monkeypatch, {'year': 2022, 'month': 5, 'day': 6, 'hour': 2})
    complaint_body = {
        "event_id": event2['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }
    client.post("api/complaints", json=complaint_body)
    mock_date(monkeypatch, {'year': 2022, 'month': 6, 'day': 6, 'hour': 2})
    complaint_body = {
        "event_id": event2['id'],
        "complainer_id": complainer2['id'],
        "type": "Spam",
        "description": "description",
    }
    client.post("api/complaints", json=complaint_body)

    response = client.get(URI + '?start_date=2022-01-07&end_date=2022-07-10')
    assert response.status_code == 200
    data = response.json()
    assert data["complaints_by_time"] == [
        {"date": "2022-04", "complaints": 2},
        {"date": "2022-05", "complaints": 1},
        {"date": "2022-06", "complaints": 1},
    ]
