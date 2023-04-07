from fastapi.testclient import TestClient
import pytest
from test.utils import generate_invalid

from app.app import app

client = TestClient(app)

URI = 'api/users'


@pytest.fixture(autouse=True)
def clear_db():
    # This runs before each test

    yield

    # Ant this runs after each test
    client.post('api/reset')


def test_get_user_not_exists():
    response = client.get(URI + "/notexists")
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == "User not found"


def create_user_body(fields={}):
    body = {
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email@mail.com',
        'identification_number': '40400400',
        'phone_number': '1180808080',
        "birth_date": "1990-01-01",
        "id":"784578"
    }

    for k, v in fields.items():
        body[k] = v

    return body


def test_user_create_succesfully():
    body = create_user_body()
    response = client.post(URI, json=body)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    body["id"] = data["id"]
    assert body == data


def test_user_create_existing_user_fails():
    body = create_user_body()
    # Created first time
    client.post(URI, json=body)
    # Try to create again
    response = client.post(URI, json=body)

    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == "User already exists"


def test_user_create_wrong_body():
    body = create_user_body()

    invalid_variations = {
        'first_name': [None, '', 'aa'],
        'last_name': [None, '', 'aa'],
        'email': [None, '', 'email', 'a', 'email.com'],
        #'birth_date': [None, '', 'a', 'aa'],
    }

    invalid_bodies = generate_invalid(body, invalid_variations)

    # NOTE: If one of this tests fails, we don´t get enough information
    # we just know that the hole suit failed.

    for inv_body in invalid_bodies:
        response = client.post(URI, json=inv_body)
        assert response.status_code == 422


def test_user_create_and_retrieve_successfully():
    body = create_user_body()
    id = client.post(URI, json=body).json()["id"]
    response = client.get(URI + f"/{id}")
    data = response.json()
    body["id"] = id
    assert body == data
