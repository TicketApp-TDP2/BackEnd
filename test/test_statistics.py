from fastapi.testclient import TestClient
import pytest
from test.utils import generate_invalid

from app.app import app

client = TestClient(app)

URI = 'api/stats'


@pytest.fixture(autouse=True)
def clear_db():
    # This runs before each test

    yield

    # Ant this runs after each test
    client.post('api/reset')
