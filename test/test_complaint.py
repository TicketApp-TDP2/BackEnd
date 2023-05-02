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
    event = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    response = client.post(URI, json=complaint_body)
    response_data = response.json()

    assert response.status_code == 201
    assert 'id' in response_data
    complaint_body["id"] = response_data["id"]
    complaint_body["organizer_id"] = organizer['id']
    complaint_body["date"] = response_data["date"]
    assert response_data == complaint_body


def test_complaint_create_without_description():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
    }

    response = client.post(URI, json=complaint_body)
    response_data = response.json()

    assert response.status_code == 201
    assert 'id' in response_data
    complaint_body["id"] = response_data["id"]
    complaint_body["description"] = ""
    complaint_body["organizer_id"] = organizer['id']
    complaint_body["date"] = response_data["date"]
    assert response_data == complaint_body


def test_complaint_create_with_missing_data():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    invalid_variations = {
        'event_id': [None, ''],
        'complainer_id': [None, ''],
        'type': [None, '', 'invalid_type'],
    }

    invalid_bodies = generate_invalid(complaint_body, invalid_variations)

    for inv_body in invalid_bodies:
        response = client.post(URI, json=inv_body)
        try:
            assert response.status_code == 422
        except Exception:
            print("Failed body: \n")
            pprint(inv_body)
            raise


def test_complaint_create_twice():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body1 = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    complaint_body2 = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Otros",
        "description": "description",
    }

    response1 = client.post(URI, json=complaint_body1)
    response2 = client.post(URI, json=complaint_body2)
    response_data1 = response1.json()
    response_data2 = response2.json()

    assert response1.status_code == 201
    assert 'id' in response_data1
    complaint_body1["id"] = response_data1["id"]
    complaint_body1["organizer_id"] = organizer['id']
    complaint_body1["date"] = response_data1["date"]
    assert response_data1 == complaint_body1

    assert response2.status_code == 201
    assert 'id' in response_data2
    complaint_body2["id"] = response_data2["id"]
    complaint_body2["organizer_id"] = organizer['id']
    complaint_body2["date"] = response_data2["date"]
    assert response_data2 == complaint_body2


def test_complaint_create_with_2_complainers():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer1 = create_user({'email': 'complainer@mail.com', 'id': '234'})
    complainer2 = create_user({'email': 'complainer2@mail.com', 'id': '2348'})
    event = create_event({'organizer': organizer['id']})

    complaint_body1 = {
        "event_id": event['id'],
        "complainer_id": complainer1['id'],
        "type": "Spam",
        "description": "description",
    }

    complaint_body2 = {
        "event_id": event['id'],
        "complainer_id": complainer2['id'],
        "type": "Otros",
        "description": "description",
    }

    response1 = client.post(URI, json=complaint_body1)
    response2 = client.post(URI, json=complaint_body2)
    response_data1 = response1.json()
    response_data2 = response2.json()

    assert response1.status_code == 201
    assert 'id' in response_data1
    complaint_body1["id"] = response_data1["id"]
    complaint_body1["organizer_id"] = organizer['id']
    complaint_body1["date"] = response_data1["date"]
    assert response_data1 == complaint_body1

    assert response2.status_code == 201
    assert 'id' in response_data2
    complaint_body2["id"] = response_data2["id"]
    complaint_body2["organizer_id"] = organizer['id']
    complaint_body2["date"] = response_data2["date"]
    assert response_data2 == complaint_body2


def test_create_complaint_with_non_existing_event():
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})

    complaint_body = {
        "event_id": "123",
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    response = client.post(URI, json=complaint_body)

    assert response.status_code == 400
    assert response.json() == {'detail': 'event_not_found'}


def test_complaint_get_non_existent():
    response = client.get(URI + "/123")
    assert response.status_code == 404
    assert response.json() == {'detail': 'complaint_not_found'}


def test_complaint_get_one():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    response = client.post(URI, json=complaint_body)
    id = response.json()['id']

    response = client.get(URI + f"/{id}")
    assert response.status_code == 200
    data = response.json()
    complaint_body["id"] = id
    complaint_body["organizer_id"] = organizer['id']
    complaint_body["date"] = data["date"]
    assert data == complaint_body


def test_complaint_get_two():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer1 = create_user({'email': 'complainer1@mail.com', 'id': '234'})
    complainer2 = create_user({'email': 'complainer2@mail.com', 'id': '2345'})
    event = create_event({'organizer': organizer['id']})

    complaint_body1 = {
        "event_id": event['id'],
        "complainer_id": complainer1['id'],
        "type": "Spam",
        "description": "description",
    }

    complaint_body2 = {
        "event_id": event['id'],
        "complainer_id": complainer2['id'],
        "type": "Spam",
        "description": "description",
    }

    response = client.post(URI, json=complaint_body1)
    id1 = response.json()['id']
    complaint_body1["id"] = id1
    complaint_body1["organizer_id"] = organizer['id']
    complaint_body1["date"] = response.json()["date"]

    response = client.post(URI, json=complaint_body2)
    id2 = response.json()['id']
    complaint_body2["id"] = id2
    complaint_body2["organizer_id"] = organizer['id']
    complaint_body2["date"] = response.json()["date"]

    response = client.get(URI + f"/{id1}")
    assert response.status_code == 200
    data = response.json()
    assert data == complaint_body1

    response = client.get(URI + f"/{id2}")
    assert response.status_code == 200
    data = response.json()
    assert data == complaint_body2


def test_complaint_get_by_organizer_empty():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})

    response = client.get(URI + f"/organizer/{organizer['id']}")
    assert response.status_code == 200
    assert response.json() == []


def test_complaint_get_by_organizer_one():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)

    response = client.get(URI + f"/organizer/{organizer['id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    complaint_body["id"] = data[0]["id"]
    complaint_body["organizer_id"] = organizer['id']
    complaint_body["date"] = data[0]["date"]
    assert data[0] == complaint_body


def test_complaint_get_by_organizer_two():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})
    event2 = create_event({'organizer': organizer['id']})

    complaint_body1 = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    complaint_body2 = {
        "event_id": event2['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body1)
    client.post(URI, json=complaint_body2)

    response = client.get(URI + f"/organizer/{organizer['id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    complaint_body1["id"] = data[0]["id"]
    complaint_body1["organizer_id"] = organizer['id']
    complaint_body1["date"] = data[0]["date"]
    complaint_body2["id"] = data[1]["id"]
    complaint_body2["organizer_id"] = organizer['id']
    complaint_body2["date"] = data[1]["date"]
    assert data[0] == complaint_body1
    assert data[1] == complaint_body2


def test_get_complaint_by_organizer_two_organizers():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    organizer2 = create_organizer({'email': 'email2@mail.com', 'id': '1234'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})
    event2 = create_event({'organizer': organizer2['id']})

    complaint_body1 = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    complaint_body2 = {
        "event_id": event2['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body1)
    client.post(URI, json=complaint_body2)

    response = client.get(URI + f"/organizer/{organizer['id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    complaint_body1["id"] = data[0]["id"]
    complaint_body1["organizer_id"] = organizer['id']
    complaint_body1["date"] = data[0]["date"]
    assert data[0] == complaint_body1


def test_complaint_get_by_event_empty():
    event = create_event({'organizer': "123"})

    response = client.get(URI + f"/event/{event['id']}")
    assert response.status_code == 200
    assert response.json() == []


def test_complaint_get_by_event_one():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)

    response = client.get(URI + f"/event/{event['id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    complaint_body["id"] = data[0]["id"]
    complaint_body["organizer_id"] = organizer['id']
    complaint_body["date"] = data[0]["date"]
    assert data[0] == complaint_body


def test_complaint_get_by_event_two():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body1 = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    complaint_body2 = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body1)
    client.post(URI, json=complaint_body2)

    response = client.get(URI + f"/event/{event['id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    complaint_body1["id"] = data[0]["id"]
    complaint_body1["organizer_id"] = organizer['id']
    complaint_body1["date"] = data[0]["date"]
    complaint_body2["id"] = data[1]["id"]
    complaint_body2["organizer_id"] = organizer['id']
    complaint_body2["date"] = data[1]["date"]
    assert data[0] == complaint_body1
    assert data[1] == complaint_body2


def test_get_complaint_by_event_two_events():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    organizer2 = create_organizer({'email': 'email2@mail.com', 'id': '1232'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})
    event2 = create_event({'organizer': organizer2['id']})

    complaint_body1 = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    complaint_body2 = {
        "event_id": event2['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body1)
    client.post(URI, json=complaint_body2)

    response = client.get(URI + f"/event/{event['id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    complaint_body1["id"] = data[0]["id"]
    complaint_body1["organizer_id"] = organizer['id']
    complaint_body1["date"] = data[0]["date"]
    assert data[0] == complaint_body1


def test_complaint_ranking_by_organizer_empty():
    response = client.get(URI + "/ranking/organizer")
    assert response.status_code == 200
    assert response.json() == []


def test_complaint_ranking_by_organizer_one():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)

    response = client.get(URI + "/ranking/organizer")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0] == {'organizer_id': organizer['id'], 'complaints': 1}


def test_complaint_ranking_by_organizer_two():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)
    client.post(URI, json=complaint_body)

    response = client.get(URI + "/ranking/organizer")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0] == {'organizer_id': organizer['id'], 'complaints': 2}


def test_complaint_ranking_by_organizer_two_organizers():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    organizer2 = create_organizer({'email': 'email2@mail.com', 'id': '1232'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})
    event2 = create_event({'organizer': organizer2['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)

    complaint_body2 = {
        "event_id": event2['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body2)
    client.post(URI, json=complaint_body2)

    response = client.get(URI + "/ranking/organizer")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0] == {'organizer_id': organizer2['id'], 'complaints': 2}
    assert data[1] == {'organizer_id': organizer['id'], 'complaints': 1}


def test_complaint_ranking_by_event_empty():
    response = client.get(URI + "/ranking/event")
    assert response.status_code == 200
    assert response.json() == []


def test_complaint_ranking_by_event_one():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)

    response = client.get(URI + "/ranking/event")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0] == {'event_id': event['id'], 'complaints': 1}


def test_complaint_ranking_by_event_two():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)
    client.post(URI, json=complaint_body)

    response = client.get(URI + "/ranking/event")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0] == {'event_id': event['id'], 'complaints': 2}


def test_complaint_ranking_by_event_two_events():
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})
    event2 = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)

    complaint_body2 = {
        "event_id": event2['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body2)
    client.post(URI, json=complaint_body2)

    response = client.get(URI + "/ranking/event")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0] == {'event_id': event2['id'], 'complaints': 2}
    assert data[1] == {'event_id': event['id'], 'complaints': 1}


def test_create_complaint_with_valid_date(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    response = client.post(URI, json=complaint_body)
    response_data = response.json()

    assert response.status_code == 201
    assert response_data["date"] == "2023-02-02"


def test_complaint_ranking_by_organizer_two_with_date_filter(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 1, "hour": 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)
    mock_date(monkeypatch, {"year": 2023, "month": 4, "day": 1, "hour": 15})
    client.post(URI, json=complaint_body)

    response = client.get(URI + "/ranking/organizer?start=2023-01-01&end=2023-03-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0] == {'organizer_id': organizer['id'], 'complaints': 1}


def test_complaint_ranking_by_organizer_two_with_date_filter_end(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 1, "hour": 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)
    mock_date(monkeypatch, {"year": 2023, "month": 4, "day": 1, "hour": 15})
    client.post(URI, json=complaint_body)

    response = client.get(URI + "/ranking/organizer?start=2023-03-01&end=2023-05-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0] == {'organizer_id': organizer['id'], 'complaints': 1}


def test_complaint_ranking_by_organizer_two_organizers_with_date_filter(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 1, "hour": 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    organizer2 = create_organizer({'email': 'email2@mail.com', 'id': '1232'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})
    event2 = create_event({'organizer': organizer2['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)

    complaint_body2 = {
        "event_id": event2['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body2)
    mock_date(monkeypatch, {"year": 2023, "month": 4, "day": 1, "hour": 15})
    client.post(URI, json=complaint_body2)

    response = client.get(URI + "/ranking/organizer?start=2023-01-01&end=2023-03-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0] == {'organizer_id': organizer2['id'], 'complaints': 1} or data[
        0
    ] == {'organizer_id': organizer['id'], 'complaints': 1}
    assert data[1] == {'organizer_id': organizer['id'], 'complaints': 1} or data[1] == {
        'organizer_id': organizer2['id'],
        'complaints': 1,
    }


def test_complaint_ranking_by_organizer_two_organizers_with_date_filter_one(
    monkeypatch,
):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 1, "hour": 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    organizer2 = create_organizer({'email': 'email2@mail.com', 'id': '1232'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})
    event2 = create_event({'organizer': organizer2['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)
    mock_date(monkeypatch, {"year": 2023, "month": 4, "day": 1, "hour": 15})

    complaint_body2 = {
        "event_id": event2['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body2)
    client.post(URI, json=complaint_body2)

    response = client.get(URI + "/ranking/organizer?start=2023-03-01&end=2023-04-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0] == {'organizer_id': organizer2['id'], 'complaints': 2}


def test_complaint_ranking_by_event_two_with_date_filter(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 1, "hour": 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)
    mock_date(monkeypatch, {"year": 2023, "month": 4, "day": 1, "hour": 15})
    client.post(URI, json=complaint_body)

    response = client.get(URI + "/ranking/event?start=2023-03-01&end=2023-04-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0] == {'event_id': event['id'], 'complaints': 1}


def test_complaint_ranking_by_event_two_with_date_filter_start(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 1, "hour": 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)
    mock_date(monkeypatch, {"year": 2023, "month": 4, "day": 1, "hour": 15})
    client.post(URI, json=complaint_body)

    response = client.get(URI + "/ranking/event?start=2023-01-01&end=2023-03-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0] == {'event_id': event['id'], 'complaints': 1}


def test_complaint_ranking_by_event_two_events_with_date_filter(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 1, "hour": 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})
    event2 = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)

    complaint_body2 = {
        "event_id": event2['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body2)
    mock_date(monkeypatch, {"year": 2023, "month": 4, "day": 1, "hour": 15})
    client.post(URI, json=complaint_body2)

    response = client.get(URI + "/ranking/event?start=2023-01-01&end=2023-03-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0] == {'event_id': event2['id'], 'complaints': 1} or data[0] == {
        'event_id': event['id'],
        'complaints': 1,
    }
    assert data[1] == {'event_id': event['id'], 'complaints': 1} or data[1] == {
        'event_id': event2['id'],
        'complaints': 1,
    }


def test_complaint_ranking_by_event_two_events_with_date_filter_one(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 1, "hour": 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})
    event2 = create_event({'organizer': organizer['id']})

    complaint_body = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body)

    complaint_body2 = {
        "event_id": event2['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    mock_date(monkeypatch, {"year": 2023, "month": 4, "day": 1, "hour": 15})
    client.post(URI, json=complaint_body2)
    client.post(URI, json=complaint_body2)

    response = client.get(URI + "/ranking/event?start=2023-03-01&end=2023-04-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0] == {'event_id': event2['id'], 'complaints': 2}


def test_complaint_get_by_event_two_with_date_filter(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 1, "hour": 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body1 = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description1",
    }

    complaint_body2 = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description2",
    }

    client.post(URI, json=complaint_body1)
    mock_date(monkeypatch, {"year": 2023, "month": 4, "day": 1, "hour": 15})
    client.post(URI, json=complaint_body2)

    response = client.get(URI + f"/event/{event['id']}?start=2023-03-01&end=2023-04-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    complaint_body2["id"] = data[0]["id"]
    complaint_body2["organizer_id"] = organizer['id']
    complaint_body2["date"] = data[0]["date"]
    assert data[0] == complaint_body2


def test_complaint_get_by_event_two_with_date_filter_start(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 1, "hour": 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})

    complaint_body1 = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description1",
    }

    complaint_body2 = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description2",
    }

    client.post(URI, json=complaint_body1)
    mock_date(monkeypatch, {"year": 2023, "month": 4, "day": 1, "hour": 15})
    client.post(URI, json=complaint_body2)

    response = client.get(URI + f"/event/{event['id']}?start=2023-01-01&end=2023-02-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    complaint_body1["id"] = data[0]["id"]
    complaint_body1["organizer_id"] = organizer['id']
    complaint_body1["date"] = data[0]["date"]
    assert data[0] == complaint_body1


def test_get_complaint_by_event_two_events_with_date_filter(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 1, "hour": 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    organizer2 = create_organizer({'email': 'email2@mail.com', 'id': '1232'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})
    event2 = create_event({'organizer': organizer2['id']})

    complaint_body1 = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description1",
    }

    complaint_body2 = {
        "event_id": event2['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description2",
    }

    client.post(URI, json=complaint_body1)
    mock_date(monkeypatch, {"year": 2023, "month": 4, "day": 1, "hour": 15})
    client.post(URI, json=complaint_body2)

    response = client.get(URI + f"/event/{event['id']}?start=2023-03-01&end=2023-04-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_complaint_get_by_organizer_two_with_date_filter(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 1, "hour": 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})
    event2 = create_event({'organizer': organizer['id']})

    complaint_body1 = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description1",
    }

    complaint_body2 = {
        "event_id": event2['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description2",
    }

    client.post(URI, json=complaint_body1)
    mock_date(monkeypatch, {"year": 2023, "month": 4, "day": 1, "hour": 15})
    client.post(URI, json=complaint_body2)

    response = client.get(
        URI + f"/organizer/{organizer['id']}?start=2023-03-01&end=2023-04-01"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    complaint_body2["id"] = data[0]["id"]
    complaint_body2["organizer_id"] = organizer['id']
    complaint_body2["date"] = data[0]["date"]
    assert data[0] == complaint_body2


def test_complaint_get_by_organizer_two_with_date_filter_end(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 1, "hour": 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})
    event2 = create_event({'organizer': organizer['id']})

    complaint_body1 = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description1",
    }

    complaint_body2 = {
        "event_id": event2['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description2",
    }

    client.post(URI, json=complaint_body1)
    mock_date(monkeypatch, {"year": 2023, "month": 4, "day": 1, "hour": 15})
    client.post(URI, json=complaint_body2)

    response = client.get(
        URI + f"/organizer/{organizer['id']}?start=2023-01-01&end=2023-03-01"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    complaint_body1["id"] = data[0]["id"]
    complaint_body1["organizer_id"] = organizer['id']
    complaint_body1["date"] = data[0]["date"]
    assert data[0] == complaint_body1


def test_get_complaint_by_organizer_two_organizers_with_date_filter(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 1, "hour": 15})
    organizer = create_organizer({'email': 'email@mail.com', 'id': '123'})
    organizer2 = create_organizer({'email': 'email2@mail.com', 'id': '1234'})
    complainer = create_user({'email': 'complainer@mail.com', 'id': '234'})
    event = create_event({'organizer': organizer['id']})
    event2 = create_event({'organizer': organizer2['id']})

    complaint_body1 = {
        "event_id": event['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    complaint_body2 = {
        "event_id": event2['id'],
        "complainer_id": complainer['id'],
        "type": "Spam",
        "description": "description",
    }

    client.post(URI, json=complaint_body1)
    client.post(URI, json=complaint_body2)

    response = client.get(
        URI + f"/organizer/{organizer['id']}?start=2023-03-01&end=2023-04-01"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
