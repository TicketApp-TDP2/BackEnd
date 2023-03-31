from fastapi.testclient import TestClient
from pprint import pprint
import pytest

from app.app import app
from test.utils import generate_invalid

client = TestClient(app)

URI = 'api/events'


def create_event(fields={}):
    body = {
        'title': 'aTitle',
        'description': 'aDescription',
        'location': {
            'description': 'a location description',
            'lat': 23.4,
            'lng': 32.23,
        },
        'type': 'aTypeToBeDefined',
        'images': ['image1', 'image2', 'image3'],
        'preview_image': 'preview_image',
        'date': '2023-03-29',
        'start_time': '16:00:00',
        'end_time': '18:00:00',
        'organizer': 'anOwner',
        'agenda': 'str',  # TO DEFINE
        'vacants': 3,
        'FAQ': [('q1', 'a1'), ('q2', 'a2')],
    }

    for k, v in fields.items():
        body[k] = v

    response = client.post(URI, json=body)
    return response.json()


@pytest.fixture(autouse=True)
def clear_db():
    # This runs before each test

    yield

    # Ant this runs after each test
    client.post('api/reset')


def test_event_create_succesfully():
    body = create_event()
    response = client.post(URI, json=body)
    response_data = response.json()
    assert response.status_code == 201
    assert 'id' in response_data


def test_event_create_with_wrong_body():
    body = {
        'title': 'aTitle',
        'description': 'aDescription',
        'location': {
            'description': 'a location description',
            'lat': 23.4,
            'lng': 32.23,
        },
        'type': 'aTypeToBeDefined',  # CHECK REAL TYPES
        'images': ['image1', 'image2', 'image3'],
        'preview_image': 'preview_image',
        'date': '2023-03-29',
        'start_time': '16:00:00',
        'end_time': '18:00:00',
        'organizer': 'anOwner',
        'agenda': 'str',  # TO DEFINE
        'vacants': 3,
        'FAQ': [('q1', 'a1'), ('q2', 'a2')],
    }

    invalid_variations = {
        'title': [None, '', 'a'],
        'description': [None, '', 'a'],
        'location': [
            None,
            '',
            3,
            {
                'description': 'a location description',
                'lng': 32.23,
            },
            {
                'description': 'a location description',
                'lng': 32.23,
                'lat': '',
            },
        ],
        'type': [None, '', 'NoExistente'],
        'images': [None, ''],
        'preview_image': [None, ''],
        'date': [None, '', 'a', '-03-29', '2023-03-29T16:00:00'],
        'organizer': [None, ''],
        'start_time': [None, '', 'a', '25:00:00'],
        'end_time': [None, '', 'a', '25:00:00'],
        'agenda': [None, ''],
        'vacants': [None, '', 'a', 0],
        'FAQ': [None, '', 'a', [('a')], [('a', 'b', 'c')], [('a', 'b'), ('c')]],
    }

    invalid_bodies = generate_invalid(body, invalid_variations)

    # NOTE: If one of this tests fails, we don´t get enough information
    # we just know that the hole suit failed.

    for inv_body in invalid_bodies:
        response = client.post(URI, json=inv_body)
        try:
            assert response.status_code == 422
        except Exception:
            print("Failed body: \n")
            pprint(inv_body)
            raise


def test_get_event_not_exists():
    response = client.get(URI + "/notexists")
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == "Event not found"


def test_get_event_exists():
    body = create_event()
    response = client.post(URI, json=body)
    id = response.json()['id']
    expected_response = body.copy()
    expected_response['id'] = id

    response = client.get(f"{URI}/{id}")
    data = response.json()
    assert response.status_code == 200
    assert expected_response == data


def test_search_event_by_type():
    event1 = create_event({"title": "event 1", "type": "aTypeToBeDefined"})
    event2 = create_event({"title": "event 2", "type": "anotherTypeToBeDefined"})
    event3 = create_event({"title": "event 3", "type": "aTypeToBeDefined"})

    response = client.get(f"{URI}?type=aTypeToBeDefined")
    data = response.json()

    data_titles = map(lambda e: e['title'], data)

    assert len(data) == 2
    assert all(map(lambda e: e['title'] in data_titles, [event1, event3]))
    assert not any(map(lambda e: e['title'] in data_titles, [event2]))


def test_search_event_by_organizer():
    event1 = create_event({"title": "event 1", "organizer": "omar"})
    event2 = create_event({"title": "event 2", "organizer": "juan"})
    event3 = create_event({"title": "event 3", "organizer": "omar"})
    event4 = create_event({"title": "event 4", "organizer": "gabriel"})

    response = client.get(f"{URI}?organizer=omar")
    data = response.json()

    data_titles = map(lambda e: e['title'], data)

    assert len(data) == 2
    assert all(map(lambda e: e['title'] in data_titles, [event1, event3]))
    assert not any(map(lambda e: e['title'] in data_titles, [event2, event4]))


def test_search_event_by_location():
    event1 = create_event(
        {
            "title": "event 1",
            "location": {'description': 'location', 'lat': 24.0, 'lng': 24.0},
        }
    )
    event2 = create_event(
        {
            "title": "event 2",
            "location": {'description': 'location', 'lat': 24.0, 'lng': 40.0},
        }
    )
    event3 = create_event(
        {
            "title": "event 3",
            "location": {'description': 'location', 'lat': 24.0, 'lng': 23.0},
        }
    )
    event4 = create_event(
        {
            "title": "event 4",
            "location": {'description': 'location', 'lat': -10.0, 'lng': 24.0},
        }
    )

    response = client.get(f"{URI}?lat=24&lng=23.5&dist=105000")
    data = response.json()

    data_titles = list(map(lambda e: e['title'], data))

    assert len(data) == 2
    assert all(map(lambda e: e['title'] in data_titles, [event1, event3]))
    assert not any(map(lambda e: e['title'] in data_titles, [event2, event4]))


def test_search_event_without_filters_returns_everything():
    event1 = create_event(
        {"title": "event 1", "organizer": "omar", "type": "aTypeToBeDefined"}
    )
    event2 = create_event(
        {"title": "event 2", "organizer": "juan", "type": "aTypeToBeDefined"}
    )
    event3 = create_event(
        {"title": "event 3", "organizer": "Food", "type": "anotherTypeToBeDefined"}
    )
    event4 = create_event(
        {"title": "event 4", "organizer": "omar", "type": "anotherTypeToBeDefined"}
    )

    response = client.get(f"{URI}")
    data = response.json()

    data_titles = map(lambda e: e['title'], data)

    assert len(data) == 4
    assert all(
        map(lambda e: e['title'] in data_titles, [event1, event2, event3, event4])
    )


def test_search_event_with_multiple_filters():
    event1 = create_event(
        {"title": "event 1", "organizer": "omar", "type": "anotherTypeToBeDefined"}
    )
    event2 = create_event(
        {"title": "event 2", "organizer": "juan", "type": "anotherTypeToBeDefined"}
    )
    event3 = create_event(
        {"title": "event 3", "organizer": "Food", "type": "aTypeToBeDefined"}
    )
    event4 = create_event(
        {"title": "event 4", "organizer": "omar", "type": "aTypeToBeDefined"}
    )

    response = client.get(f"{URI}?type=anotherTypeToBeDefined&organizer=omar")
    data = response.json()

    data_titles = map(lambda e: e['title'], data)

    assert len(data) == 1
    assert all(map(lambda e: e['title'] in data_titles, [event1]))
    assert not any(map(lambda e: e['title'] in data_titles, [event2, event3, event4]))


def test_search_event_with_limit_returns_given_amount():
    create_event(
        {"title": "event 1", "organizer": "omar", "type": "anotherTypeToBeDefined"}
    )
    create_event(
        {"title": "event 2", "organizer": "juan", "type": "anotherTypeToBeDefined"}
    )
    create_event({"title": "event 3", "organizer": "Food", "type": "aTypeToBeDefined"})
    create_event({"title": "event 4", "organizer": "omar", "type": "aTypeToBeDefined"})

    response = client.get(f"{URI}?limit=3")
    data = response.json()

    assert len(data) == 3


def test_search_event_by_title():
    event1 = create_event({"title": "event"})
    event2 = create_event({"title": "the eventual"})
    event3 = create_event({"title": "another"})

    response = client.get(f"{URI}?title=event")
    data = response.json()

    data_titles = map(lambda e: e['title'], data)

    assert len(data) == 2
    assert all(map(lambda e: e['title'] in data_titles, [event1, event2]))
    assert not any(map(lambda e: e['title'] in data_titles, [event3]))
