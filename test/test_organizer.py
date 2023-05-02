from fastapi.testclient import TestClient
import pytest
from test.utils import generate_invalid

from app.app import app

client = TestClient(app)

URI = 'api/organizers'


@pytest.fixture(autouse=True)
def clear_db():
    # This runs before each test

    yield

    # Ant this runs after each test
    client.post('api/reset')


def test_get_organizer_not_exists():
    response = client.get(URI + "/notexists")
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == "organizer_not_found"


def create_organizer_body(fields={}):
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

    return body


def test_organizer_create_succesfully():
    body = create_organizer_body()
    response = client.post(URI, json=body)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    body["id"] = data["id"]
    body["suspended"] = False
    assert body == data


def test_organizer_create_existing_organizer_fails():
    body = create_organizer_body()
    # Created first time
    client.post(URI, json=body)
    # Try to create again
    response = client.post(URI, json=body)

    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == "organizer_already_exists"


def test_organizer_create_wrong_body():
    body = create_organizer_body()

    invalid_variations = {
        'first_name': [None, '', 'aa'],
        'email': [None, '', 'email', 'a', 'email.com'],
        'id': [None, ''],
    }

    invalid_bodies = generate_invalid(body, invalid_variations)

    # NOTE: If one of this tests fails, we don´t get enough information
    # we just know that the hole suit failed.

    for inv_body in invalid_bodies:
        response = client.post(URI, json=inv_body)
        assert response.status_code == 422


def test_organizer_create_and_retrieve_successfully():
    body = create_organizer_body()
    id = client.post(URI, json=body).json()["id"]
    response = client.get(URI + f"/{id}")
    data = response.json()
    body["id"] = id
    body["suspended"] = False
    assert body == data


def test_organizer_update():
    body = create_organizer_body()
    id = client.post(URI, json=body).json()["id"]
    new_body = {
        "first_name": "new_first_name",
        "last_name": "new_last_name",
        "profession": "new_profession",
        "about_me": "new_about_me",
        "profile_picture": "new_profile_picture",
    }
    response = client.put(URI + f"/{id}", json=new_body)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == new_body["first_name"]
    assert data["last_name"] == new_body["last_name"]
    assert data["profession"] == new_body["profession"]
    assert data["about_me"] == new_body["about_me"]
    assert data["profile_picture"] == new_body["profile_picture"]


def test_create_without_last_name():
    body = create_organizer_body()
    body.pop('last_name')
    response = client.post(URI, json=body)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data['last_name'] == body["first_name"]


def test_suspend_organizer():
    body = create_organizer_body()
    id = client.post(URI, json=body).json()["id"]
    response = client.put(URI + f"/{id}/suspend")
    assert response.status_code == 200
    data = response.json()
    assert data["suspended"] is True


def test_get_organizer_suspended():
    body = create_organizer_body()
    id = client.post(URI, json=body).json()["id"]
    client.put(URI + f"/{id}/suspend")
    response = client.get(URI + f"/{id}")
    assert response.status_code == 200
    data = response.json()
    assert data["suspended"] is True


def test_unsuspend_organizer():
    body = create_organizer_body()
    id = client.post(URI, json=body).json()["id"]
    client.put(URI + f"/{id}/suspend")
    response = client.put(URI + f"/{id}/unsuspend")
    assert response.status_code == 200
    data = response.json()
    assert data["suspended"] is False


def test_get_organizer_unsuspended():
    body = create_organizer_body()
    id = client.post(URI, json=body).json()["id"]
    client.put(URI + f"/{id}/suspend")
    client.put(URI + f"/{id}/unsuspend")
    response = client.get(URI + f"/{id}")
    assert response.status_code == 200
    data = response.json()
    assert data["suspended"] is False


def test_suspend_organizer_twice():
    body = create_organizer_body()
    id = client.post(URI, json=body).json()["id"]
    client.put(URI + f"/{id}/suspend")
    response = client.put(URI + f"/{id}/suspend")
    assert response.status_code == 200
    data = response.json()
    assert data["suspended"] is True


def test_unsuspend_organizer_twice():
    body = create_organizer_body()
    id = client.post(URI, json=body).json()["id"]
    client.put(URI + f"/{id}/suspend")
    client.put(URI + f"/{id}/unsuspend")
    response = client.put(URI + f"/{id}/unsuspend")
    assert response.status_code == 200
    data = response.json()
    assert data["suspended"] is False


def test_suspend_non_existing_organizer():
    response = client.put(URI + f"/123/suspend")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "organizer_not_found"


def test_unsuspend_non_existing_organizer():
    response = client.put(URI + f"/123/unsuspend")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "organizer_not_found"
