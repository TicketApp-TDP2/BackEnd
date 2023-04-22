from fastapi.testclient import TestClient
import pytest

from app.app import app

client = TestClient(app)


def favourites_uri(id: str):
    return f"api/users/{id}/favourites"


def delete_favourites_uri(user_id: str, event_id: str):
    return f"api/users/{user_id}/favourites/{event_id}"


def create_user():
    body = {
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email@mail.com',
        'identification_number': '40400400',
        'phone_number': '1180808080',
        "birth_date": "1990-01-01",
        'id': 'anId',
    }
    response = client.post("api/users", json=body)
    return response.json()


def create_event():
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

    response = client.post("api/events", json=body)
    return response.json()


@pytest.fixture(autouse=True)
def clear_db():
    # This runs before each test

    yield

    # Ant this runs after each test
    client.post('api/reset')


def test_user_not_exists():
    response = client.get(favourites_uri('notexists'))
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == "user_not_found"


def test_user_without_favourites():
    # Create user
    user = create_user()
    user_id = user['id']

    # Get user favourites
    response = client.get(favourites_uri(user_id))
    data = response.json()
    assert response.status_code == 200
    assert data == []


def test_create_favourite_succesfully():
    # Create user
    user = create_user()
    user_id = user['id']

    # Create event
    event = create_event()
    event_id = event['id']

    # Create favourite

    favourite = {'event_id': event_id}

    response = client.post(favourites_uri(user_id), json=favourite)

    assert response.status_code == 201
    assert response.json() == favourite


def test_user_with_one_favourite():
    # Create user
    user = create_user()
    user_id = user['id']

    # Create event
    event = create_event()
    event_id = event['id']

    # Create favourite
    favourite = {'event_id': event_id}
    client.post(favourites_uri(user_id), json=favourite)

    # Get user favourites
    response = client.get(favourites_uri(user_id))
    data = response.json()

    assert response.status_code == 200
    assert data == [event]


def test_user_with_multiple_favourites():
    # Create user
    user = create_user()
    user_id = user['id']

    # Create first event
    event_1 = create_event()
    event_id = event_1['id']

    # Create first favourite
    favourite = {'event_id': event_id}
    client.post(favourites_uri(user_id), json=favourite)

    # Create second event
    event_2 = create_event()
    event_id = event_2['id']

    # Create second favourite
    favourite = {'event_id': event_id}
    client.post(favourites_uri(user_id), json=favourite)

    # Get user favourites
    response = client.get(favourites_uri(user_id))
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert event_1 in data
    assert event_2 in data


def test_create_favourite_user_not_exists():
    # Create event
    event = create_event()
    event_id = event['id']

    # Create favourite
    favourite = {'event_id': event_id}
    response = client.post(favourites_uri('notexists'), json=favourite)
    data = response.json()

    assert response.status_code == 400
    assert data['detail'] == 'user_not_found'


def test_create_favourite_event_not_exists():
    # Create user
    user = create_user()
    user_id = user['id']

    # Create favourite
    favourite = {'event_id': 'notexists'}
    response = client.post(favourites_uri(user_id), json=favourite)
    data = response.json()

    assert response.status_code == 400
    assert data['detail'] == 'event_not_found'


def test_delete_favourite_returns_empty_array():
    # Create user
    user = create_user()
    user_id = user['id']

    # Create event
    event = create_event()
    event_id = event['id']

    # Create favourite
    favourite = {'event_id': event_id}
    client.post(favourites_uri(user_id), json=favourite)

    # Delete favourite
    delete_response = client.delete(
        delete_favourites_uri(user_id=user_id, event_id=event_id)
    )

    # Get user favourites
    get_response = client.get(favourites_uri(user_id))
    data = get_response.json()

    assert delete_response.status_code == 200
    assert get_response.status_code == 200
    assert data == []


def test_delete_favourite_user_with_multiple_favourites():
    # Create user
    user = create_user()
    user_id = user['id']

    # Create first event
    event_1 = create_event()
    event_id = event_1['id']

    # Create first favourite
    favourite = {'event_id': event_id}
    client.post(favourites_uri(user_id), json=favourite)

    # Create second event
    event_2 = create_event()
    event_id = event_2['id']

    # Create second favourite
    favourite = {'event_id': event_id}
    client.post(favourites_uri(user_id), json=favourite)

    # Delete favourite
    client.delete(delete_favourites_uri(user_id=user_id, event_id=event_1['id']))

    # Get user favourites
    response = client.get(favourites_uri(user_id))
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert event_1 not in data
    assert event_2 in data


def test_delete_favourite_user_not_exist():
    user_id = 'not-exists'
    event_id = 'not-exists'

    response = client.delete(delete_favourites_uri(user_id=user_id, event_id=event_id))

    data = response.json()

    assert response.status_code == 400
    assert data['detail'] == 'user_not_found'


def test_delete_favourite_favourite_not_exist_is_ignored():
    user = create_user()
    user_id = user['id']
    event_id = 'not-exists'

    response = client.delete(delete_favourites_uri(user_id=user_id, event_id=event_id))

    # Get user favourites
    favourites_response = client.get(favourites_uri(user_id))
    favourites = favourites_response.json()

    assert response.status_code == 200
    assert favourites == []
