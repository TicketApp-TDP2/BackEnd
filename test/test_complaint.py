from fastapi.testclient import TestClient
from pprint import pprint
import pytest
from test.utils import generate_invalid, mock_date

from app.app import app

client = TestClient(app)

URI = 'api/complaints'
USERS_URI = 'api/users'
ORGANIZERS_URI = 'api/organizers'
EVENTS_URI = 'api/events'


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


def test_complaint_create_succesfully():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'owner': organizer['id']})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
        "organizer_id": organizer['id'],
    }

    response = client.post(URI, json=complaint_body)
    response_data = response.json()

    assert response.status_code == 201
    assert 'id' in response_data
    complaint_body["id"] = response_data["id"]
    assert response_data == complaint_body


def test_complaint_create_without_description():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'owner': organizer['id']})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "organizer_id": organizer['id'],
    }

    response = client.post(URI, json=complaint_body)
    response_data = response.json()

    assert response.status_code == 201
    assert 'id' in response_data
    complaint_body["id"] = response_data["id"]
    complaint_body["description"] = ""
    assert response_data == complaint_body


"""
def test_booking_create_with_missing_data(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 2})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver = create_user({'email': 'reserver@mail.com', 'id': '234'})
    event = create_event({'owner': organizer['id']})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    booking_body = {
        "event_id": event['id'],
        "reserver_id": reserver['id'],
    }

    invalid_variations = {
        'event_id': [None, ''],
        'reserver_id': [None, ''],
    }

    invalid_bodies = generate_invalid(booking_body, invalid_variations)

    for inv_body in invalid_bodies:
        response = client.post(URI, json=inv_body)
        try:
            assert response.status_code == 422
        except Exception:
            print("Failed body: \n")
            pprint(inv_body)
            raise


def test_booking_create_duplicated(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 2})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver = create_user({'email': 'reserver@mail.com', 'id': '234'})
    event = create_event({'owner': organizer['id']})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    booking_body = {
        "event_id": event['id'],
        "reserver_id": reserver['id'],
    }

    client.post(URI, json=booking_body)
    response = client.post(URI, json=booking_body)
    response_data = response.json()

    assert response.status_code == 400
    assert response_data['detail'] == "booking_already_exists"


def test_booking_create_with_2_reservers(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 2})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver1 = create_user({'email': 'reserver@mail.com', 'id': '234'})
    reserver2 = create_user({'email': 'reserver2@mail.com', 'id': '345'})
    event = create_event({'owner': organizer['id']})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    booking_body1 = {
        "event_id": event['id'],
        "reserver_id": reserver1['id'],
    }

    booking_body2 = {
        "event_id": event['id'],
        "reserver_id": reserver2['id'],
    }

    response1 = client.post(URI, json=booking_body1)
    response2 = client.post(URI, json=booking_body2)
    response_data1 = response1.json()
    response_data2 = response2.json()

    assert response1.status_code == 201
    assert 'id' in response_data1
    booking_body1["id"] = response_data1["id"]
    booking_body1["verified"] = False
    assert response_data1 == booking_body1

    assert response2.status_code == 201
    assert 'id' in response_data2
    booking_body2["id"] = response_data2["id"]
    booking_body2["verified"] = False
    assert response_data2 == booking_body2


def test_booking_get_by_reserver_empty():
    reserver = create_user()
    reserver_id = reserver['id']

    response = client.get(USERS_URI + f"/{reserver_id}/" + RESERVED_URI)
    assert response.status_code == 200
    assert response.json() == []


def test_booking_get_by_reserver_one(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 2})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver = create_user({'email': 'reserver@mail.com', 'id': '234'})
    event = create_event({'owner': organizer['id']})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    booking_body = {"event_id": event['id'], "reserver_id": reserver['id']}

    client.post(URI, json=booking_body)
    reserver_id = reserver['id']

    response = client.get(USERS_URI + f"/{reserver_id}/" + RESERVED_URI)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    booking_body["id"] = data[0]["id"]
    booking_body["verified"] = False
    assert data[0] == booking_body


def test_booking_get_by_reserver_two(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 2})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver = create_user({'email': 'reserver@mail.com', 'id': '234'})
    event1 = create_event({'owner': organizer['id']})
    client.put(f"{EVENTS_URI}/{event1['id']}/publish")
    event2 = create_event({'owner': organizer['id']})
    client.put(f"{EVENTS_URI}/{event2['id']}/publish")

    booking_body1 = {"event_id": event1['id'], "reserver_id": reserver['id']}

    booking_body2 = {"event_id": event2['id'], "reserver_id": reserver['id']}
    reserver_id = reserver['id']

    client.post(URI, json=booking_body1)
    client.post(URI, json=booking_body2)

    response = client.get(USERS_URI + f"/{reserver_id}/" + RESERVED_URI)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    booking_body1["id"] = data[0]["id"]
    booking_body1["verified"] = False
    booking_body2["id"] = data[1]["id"]
    booking_body2["verified"] = False
    assert data[0] == booking_body1
    assert data[1] == booking_body2


def test_booking_vacants_left_is_one_less(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 2})
    number_of_vacants = 10
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver = create_user({'email': 'reserver@mail.com', 'id': '234'})
    event = create_event({'owner': organizer['id'], 'vacants': number_of_vacants})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    event_id = event['id']
    booking_body = {"event_id": event_id, "reserver_id": reserver['id']}
    client.post(URI, json=booking_body)

    response = client.get(f'api/events/{event_id}')
    data = response.json()
    assert data['id'] == event_id
    assert data['vacants_left'] == number_of_vacants - 1


def test_booking_vacants_left_is_two_less(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 2})
    number_of_vacants = 10
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver1 = create_user({'email': 'reserver1@mail.com', 'id': '2341'})
    reserver2 = create_user({'email': 'reserver2@mail.com', 'id': '2342'})
    event = create_event({'owner': organizer['id'], 'vacants': number_of_vacants})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    event_id = event['id']
    booking_body1 = {"event_id": event_id, "reserver_id": reserver1['id']}
    client.post(URI, json=booking_body1)
    booking_body2 = {"event_id": event_id, "reserver_id": reserver2['id']}
    client.post(URI, json=booking_body2)

    response = client.get(f'api/events/{event_id}')
    data = response.json()
    assert data['id'] == event_id
    assert data['vacants_left'] == number_of_vacants - 2


def test_booking_no_more_vacants(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 2})
    number_of_vacants = 1
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver1 = create_user({'email': 'reserver1@mail.com', 'id': '2341'})
    reserver2 = create_user({'email': 'reserver2@mail.com', 'id': '2342'})
    event = create_event({'owner': organizer['id'], 'vacants': number_of_vacants})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    event_id = event['id']
    booking_body1 = {"event_id": event_id, "reserver_id": reserver1['id']}
    client.post(URI, json=booking_body1)

    booking_body2 = {"event_id": event_id, "reserver_id": reserver2['id']}
    response = client.post(URI, json=booking_body2)

    assert response.status_code == 400
    assert response.json() == {'detail': 'no_more_vacants_left'}


def test_verify_booking(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 2})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver = create_user({'email': 'reserver@mail.com', 'id': '234'})
    event = create_event({'owner': organizer['id']})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    event_id = event['id']
    booking_body = {"event_id": event_id, "reserver_id": reserver['id']}
    response = client.post(URI, json=booking_body)
    data = response.json()

    booking_id = data['id']

    body = {"event_id": event_id}
    response = client.put(URI + f'/{booking_id}/verify', json=body)
    assert response.status_code == 200


def test_verify_non_existing_booking(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 2})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    event = create_event({'owner': organizer['id']})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    non_existing_booking_id = "123"
    event_id = event['id']
    body = {"event_id": event_id}

    response = client.put(URI + f'/{non_existing_booking_id}/verify', json=body)
    assert response.status_code == 400
    assert response.json() == {'detail': 'booking_not_found'}


def test_verify_booking_with_wrong_event_id(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 2})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver = create_user({'email': 'reserver@mail.com', 'id': '234'})
    event = create_event({'owner': organizer['id']})
    event2 = create_event({'owner': organizer['id']})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")
    client.put(f"{EVENTS_URI}/{event2['id']}/publish")

    event_id1 = event['id']
    event_id2 = event2['id']
    booking_body = {"event_id": event_id1, "reserver_id": reserver['id']}
    response = client.post(URI, json=booking_body)
    data = response.json()
    booking_id = data['id']

    body = {"event_id": event_id2}
    response = client.put(URI + f'/{booking_id}/verify', json=body)
    assert response.status_code == 400
    assert response.json() == {'detail': 'incorrect_event'}


def test_verify_booking_twice(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 2})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver = create_user({'email': 'reserver@mail.com', 'id': '234'})
    event = create_event({'owner': organizer['id']})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    event_id = event['id']
    booking_body = {"event_id": event_id, "reserver_id": reserver['id']}
    response = client.post(URI, json=booking_body)
    data = response.json()
    booking_id = data['id']

    body = {"event_id": event_id}
    client.put(URI + f'/{booking_id}/verify', json=body)
    response = client.put(URI + f'/{booking_id}/verify', json=body)
    assert response.status_code == 400
    assert response.json() == {'detail': 'booking_already_verified'}


def test_booking_with_non_published_event(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 2})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver = create_user({'email': 'reserver@mail.com', 'id': '234'})
    event = create_event({'owner': organizer['id']})

    booking_body = {
        "event_id": event['id'],
        "reserver_id": reserver['id'],
    }

    response = client.post(URI, json=booking_body)

    assert response.status_code == 400
    assert response.json() == {'detail': 'event_not_published'}


def test_booking_with_finished_event(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 0})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver = create_user({'email': 'reserver@mail.com', 'id': '234'})
    event = create_event({'owner': organizer['id'], 'date': '2020-01-01'})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    booking_body = {
        "event_id": event['id'],
        "reserver_id": reserver['id'],
    }

    response = client.post(URI, json=booking_body)

    assert response.status_code == 400
    assert response.json() == {'detail': 'event_already_finished'}


def test_booking_with_finished_event_hour(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver = create_user({'email': 'reserver@mail.com', 'id': '234'})
    event = create_event(
        {
            'owner': organizer['id'],
            'date': '2022-01-01',
        }
    )
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    booking_body = {
        "event_id": event['id'],
        "reserver_id": reserver['id'],
    }

    response = client.post(URI, json=booking_body)

    assert response.status_code == 400
    assert response.json() == {'detail': 'event_already_finished'}


def test_event_has_0_verified_after_booking(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 2})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver = create_user({'email': 'reserver@mail.com', 'id': '234'})
    event = create_event({'owner': organizer['id']})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    booking_body = {
        "event_id": event['id'],
        "reserver_id": reserver['id'],
    }

    client.post(URI, json=booking_body)
    response = client.get(f"{EVENTS_URI}/{event['id']}")
    assert response.status_code == 200
    assert response.json()['verified_vacants'] == 0


def test_event_has_1_verified_after_booking_verified(monkeypatch):
    mock_date(monkeypatch, {'year': 2022, 'month': 1, 'day': 1, 'hour': 2})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    reserver = create_user({'email': 'reserver@mail.com', 'id': '234'})
    event = create_event({'owner': organizer['id']})
    client.put(f"{EVENTS_URI}/{event['id']}/publish")

    booking_body = {
        "event_id": event['id'],
        "reserver_id": reserver['id'],
    }

    booking_id = client.post(URI, json=booking_body).json()['id']
    client.put(URI + f'/{booking_id}/verify', json={'event_id': event['id']})

    response = client.get(f"{EVENTS_URI}/{event['id']}")
    assert response.status_code == 200
    assert response.json()['verified_vacants'] == 1
"""
