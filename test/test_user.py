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


def create_user_body(fields={}):
    body = {
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email@mail.com',
        'identification_number': '40400400',
        'phone_number': '1180808080',
        'host': False,
        'password': "1234",
        "birth_date": "1990-01-01",
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
    body["cards"] = []
    assert body == data
