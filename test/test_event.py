from fastapi.testclient import TestClient
from pprint import pprint
import pytest

from app.app import app
from test.utils import generate_invalid, mock_date
import datetime

client = TestClient(app)

URI = 'api/events'
BOOKING_URI = 'api/bookings'
ORGANIZER_URI = 'api/organizers'


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


def create_event_body(fields={}):
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
        'scan_time': 5,
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
        # [('q1', 'a1'), ('q2', 'a2')],
    }

    for k, v in fields.items():
        body[k] = v

    return body


def create_event(fields={}):
    body = create_event_body(fields)
    response = client.post(URI, json=body)
    return response.json()


def add_event_fields(event, fields={}):
    for k, v in fields.items():
        event[k] = v

    return event


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
        'name': 'aname',
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

    invalid_variations = {
        'name': [None, '', 'a'],
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
        'scan_time': [None, '', 'a', 0, 13],
        'agenda': [
            None,
            [
                {
                    'time_init': '09:00',
                    'time_end': '12:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                }
            ],
            [
                {
                    'time_init': '09:00',
                    'time_end': '12:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                },
                {
                    'time_init': '09:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                },
            ],
        ],
        'vacants': [None, '', 'a', 0],
        'FAQ': [
            None,
            [
                {
                    'question': 'se pueden llevar alimentos?',
                }
            ],
            [
                {'question': 'se pueden llevar alimentos?', 'answer': 'Si se puede'},
                {'question': 'Otra pregunta'},
            ],
        ],
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
    assert data['detail'] == "event_not_found"


def test_get_event_exists(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    body = create_event({"date": "2024-04-02"})
    response = client.post(URI, json=body)
    id = response.json()['id']
    expected_response = body.copy()
    expected_response = add_event_fields(
        expected_response,
        {
            'id': id,
            'vacants_left': expected_response['vacants'],
            'state': 'Borrador',
            'verified_vacants': 0,
            'collaborators': [],
        },
    )

    response = client.get(f"{URI}/{id}")
    data = response.json()
    assert response.status_code == 200
    assert expected_response == data


def test_search_event_by_type():
    event1 = create_event({"name": "event 1", "type": "Danza"})
    event2 = create_event({"name": "event 2", "type": "Moda"})
    event3 = create_event({"name": "event 3", "type": "Danza"})

    response = client.get(f"{URI}?type=Danza")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 2
    assert all(map(lambda e: e['name'] in data_names, [event1, event3]))
    assert not any(map(lambda e: e['name'] in data_names, [event2]))


def test_search_event_by_organizer(monkeypatch):
    mock_date(monkeypatch, {"year": 2021, "month": 2, "day": 10, "hour": 15})
    event1 = create_event({"name": "event 1", "organizer": "omar"})
    event2 = create_event({"name": "event 2", "organizer": "juan"})
    event3 = create_event({"name": "event 3", "organizer": "omar"})
    event4 = create_event({"name": "event 4", "organizer": "gabriel"})

    response = client.get(f"{URI}?organizer=omar")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 2
    assert all(map(lambda e: e['name'] in data_names, [event1, event3]))
    assert not any(map(lambda e: e['name'] in data_names, [event2, event4]))


def test_search_event_by_location():
    event1 = create_event(
        {
            "name": "event 1",
            "location": {'description': 'location', 'lat': 24.0, 'lng': 24.0},
        }
    )
    event2 = create_event(
        {
            "name": "event 2",
            "location": {'description': 'location', 'lat': 24.0, 'lng': 40.0},
        }
    )
    event3 = create_event(
        {
            "name": "event 3",
            "location": {'description': 'location', 'lat': 24.0, 'lng': 23.0},
        }
    )
    event4 = create_event(
        {
            "name": "event 4",
            "location": {'description': 'location', 'lat': -10.0, 'lng': 24.0},
        }
    )

    response = client.get(f"{URI}?lat=24&lng=23.5&dist=105000")
    data = response.json()

    data_names = list(map(lambda e: e['name'], data))

    assert len(data) == 2
    assert all(map(lambda e: e['name'] in data_names, [event1, event3]))
    assert not any(map(lambda e: e['name'] in data_names, [event2, event4]))


def test_search_event_without_filters_returns_everything():
    event1 = create_event({"name": "event 1", "organizer": "omar", "type": "Danza"})
    event2 = create_event({"name": "event 2", "organizer": "juan", "type": "Danza"})
    event3 = create_event({"name": "event 3", "organizer": "Food", "type": "Moda"})
    event4 = create_event({"name": "event 4", "organizer": "omar", "type": "Moda"})

    response = client.get(f"{URI}")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 4
    assert all(map(lambda e: e['name'] in data_names, [event1, event2, event3, event4]))


def test_search_event_with_multiple_filters(monkeypatch):
    mock_date(monkeypatch, {"year": 2021, "month": 2, "day": 10, "hour": 15})
    event1 = create_event({"name": "event 1", "organizer": "omar", "type": "Moda"})
    event2 = create_event({"name": "event 2", "organizer": "juan", "type": "Moda"})
    event3 = create_event({"name": "event 3", "organizer": "Food", "type": "Danza"})
    event4 = create_event({"name": "event 4", "organizer": "omar", "type": "Danza"})

    response = client.get(f"{URI}?type=Moda&organizer=omar")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 1
    assert all(map(lambda e: e['name'] in data_names, [event1]))
    assert not any(map(lambda e: e['name'] in data_names, [event2, event3, event4]))


def test_search_event_with_limit_returns_given_amount():
    create_event({"name": "event 1", "organizer": "omar", "type": "Moda"})
    create_event({"name": "event 2", "organizer": "juan", "type": "Moda"})
    create_event({"name": "event 3", "organizer": "Food", "type": "Danza"})
    create_event({"name": "event 4", "organizer": "omar", "type": "Danza"})

    response = client.get(f"{URI}?limit=3")
    data = response.json()

    assert len(data) == 3


def test_search_event_by_name():
    event1 = create_event({"name": "event"})
    event2 = create_event({"name": "the eventual"})
    event3 = create_event({"name": "another"})

    response = client.get(f"{URI}?name=event")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 2
    assert all(map(lambda e: e['name'] in data_names, [event1, event2]))
    assert not any(map(lambda e: e['name'] in data_names, [event3]))


def test_event_create_with_empty_faq():
    body = create_event({"FAQ": []})
    response = client.post(URI, json=body)
    response_data = response.json()
    assert response.status_code == 201
    assert 'id' in response_data


def test_event_create_with_two_agenda():
    body = create_event(
        {
            "end_time": "14:00",
            "agenda": [
                {
                    'time_init': '09:00',
                    'time_end': '12:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                },
                {
                    'time_init': '12:00',
                    'time_end': '14:00',
                    'owner': 'Agustin',
                    'title': 'Noche de teatro en Bs As 2',
                    'description': 'Una noche de teatro unica 2',
                },
            ],
        }
    )
    response = client.post(URI, json=body)
    response_data = response.json()
    assert response.status_code == 201
    assert 'id' in response_data


def test_event_create_with_two_faq():
    body = create_event(
        {
            "FAQ": [
                {'question': 'se pueden llevar alimentos?', 'answer': 'Si se puede'},
                {'question': 'Otra pregunta', 'answer': 'No se puede'},
            ]
        }
    )
    response = client.post(URI, json=body)
    response_data = response.json()
    assert response.status_code == 201
    assert 'id' in response_data


def test_create_event_with_empty_space_in_agenda():
    body = create_event_body(
        {
            "agenda": [
                {
                    'time_init': '09:00',
                    'time_end': '10:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                },
                {
                    'time_init': '11:00',
                    'time_end': '12:00',
                    'owner': 'Agustin',
                    'title': 'Noche de teatro en Bs As 2',
                    'description': 'Una noche de teatro unica 2',
                },
            ]
        }
    )
    response = client.post(URI, json=body)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'agenda_can_not_have_empty_spaces'


def test_create_event_empty_agenda():
    body = create_event_body({"agenda": []})
    response = client.post(URI, json=body)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'agenda_can_not_be_empty'


def test_create_event_with_overlap_in_agenda():
    body = create_event_body(
        {
            "agenda": [
                {
                    'time_init': '09:00',
                    'time_end': '11:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                },
                {
                    'time_init': '10:00',
                    'time_end': '12:00',
                    'owner': 'Agustin',
                    'title': 'Noche de teatro en Bs As 2',
                    'description': 'Una noche de teatro unica 2',
                },
            ]
        }
    )
    response = client.post(URI, json=body)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'agenda_can_not_have_overlap'


def test_create_event_with_agenda_ending_after_event():
    body = create_event_body(
        {
            "agenda": [
                {
                    'time_init': '09:00',
                    'time_end': '11:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                },
                {
                    'time_init': '11:00',
                    'time_end': '13:00',
                    'owner': 'Agustin',
                    'title': 'Noche de teatro en Bs As 2',
                    'description': 'Una noche de teatro unica 2',
                },
            ]
        }
    )
    response = client.post(URI, json=body)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'agenda_can_not_end_after_event_end'


def test_create_event_has_vacants_left():
    number_of_vacants = 10
    body = create_event_body(
        {
            "vacants": number_of_vacants,
        }
    )
    response = client.post(URI, json=body)
    data = response.json()
    assert response.status_code == 201
    assert data['vacants_left'] == number_of_vacants


def test_publish_event():
    event = create_event()
    response = client.put(f"{URI}/{event['id']}/publish")
    data = response.json()
    assert response.status_code == 200
    assert data['state'] == 'Publicado'


def test_publish_event_twice():
    event = create_event()
    client.put(f"{URI}/{event['id']}/publish")
    response = client.put(f"{URI}/{event['id']}/publish")
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'event_is_not_in_borrador_statee'


def test_publish_non_existing_event():
    response = client.put(f"{URI}/1/publish")
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'event_not_found'


def test_search_event_only_pusblished():
    event1 = create_event({"name": "event1"})
    event2 = create_event({"name": "event2"})
    event3 = create_event({"name": "event3"})

    client.put(f"{URI}/{event1['id']}/publish")
    client.put(f"{URI}/{event2['id']}/publish")

    response = client.get(f"{URI}?only_published=True")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 2
    assert all(map(lambda e: e['name'] in data_names, [event1, event2]))
    assert not any(map(lambda e: e['name'] in data_names, [event3]))


def test_search_event_published_false():
    event1 = create_event({"name": "event1"})
    event2 = create_event({"name": "event2"})
    event3 = create_event({"name": "event3"})

    client.put(f"{URI}/{event1['id']}/publish")
    client.put(f"{URI}/{event2['id']}/publish")

    response = client.get(f"{URI}?only_published=False")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 3
    assert all(map(lambda e: e['name'] in data_names, [event1, event2, event3]))


def test_search_event_published_incorrect_value():
    response = client.get(f"{URI}?only_published=Fals")
    assert response.status_code == 422
    assert (
        response.json()['detail'][0]["msg"] == 'value could not be parsed to a boolean'
    )


def test_date(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 4, "day": 12, "hour": 1})
    assert datetime.datetime.now() == datetime.datetime(2023, 4, 12, 1)


def test_search_events_not_finished(monkeypatch):
    mock_date(monkeypatch, {"year": 2021, "month": 1, "day": 2, "hour": 1})
    event1 = create_event({"name": "event1", "date": "2021-01-01"})
    event2 = create_event({"name": "event2", "date": "2021-01-03"})
    event3 = create_event({"name": "event3", "date": "2024-01-04"})

    response = client.get(f"{URI}?not_finished=True")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 2
    assert all(map(lambda e: e['name'] in data_names, [event2, event3]))
    assert not any(map(lambda e: e['name'] in data_names, [event1]))


def test_search_events_not_finished_false(monkeypatch):
    mock_date(monkeypatch, {"year": 2021, "month": 1, "day": 2, "hour": 1})
    event1 = create_event({"name": "event1", "date": "2021-01-01"})
    event2 = create_event({"name": "event2", "date": "2021-01-03"})
    event3 = create_event({"name": "event3", "date": "2024-01-04"})

    response = client.get(f"{URI}?not_finished=False")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 3
    assert all(map(lambda e: e['name'] in data_names, [event1, event2, event3]))


def test_search_events_not_finished_2(monkeypatch):
    mock_date(monkeypatch, {"year": 2021, "month": 1, "day": 2, "hour": 1})
    event1 = create_event({"name": "event1", "date": "2020-01-01"})
    event2 = create_event({"name": "event2", "date": "2021-01-03"})
    event3 = create_event({"name": "event3", "date": "2022-01-04"})

    response = client.get(f"{URI}?not_finished=True")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 2
    assert all(map(lambda e: e['name'] in data_names, [event2, event3]))
    assert not any(map(lambda e: e['name'] in data_names, [event1]))


def test_search_events_not_finished_3(monkeypatch):
    mock_date(monkeypatch, {"year": 2021, "month": 2, "day": 2, "hour": 1})
    event1 = create_event({"name": "event1", "date": "2020-01-01"})
    event2 = create_event({"name": "event2", "date": "2021-02-04"})
    event3 = create_event({"name": "event3", "date": "2022-03-04"})

    response = client.get(f"{URI}?not_finished=True")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 2
    assert all(map(lambda e: e['name'] in data_names, [event2, event3]))
    assert not any(map(lambda e: e['name'] in data_names, [event1]))


def test_search_events_not_finished_with_time(monkeypatch):
    mock_date(monkeypatch, {"year": 2021, "month": 2, "day": 2, "hour": 15})
    event1 = create_event(
        {"name": "event1", "date": "2021-02-02", "end_time": "12:00:00"}
    )
    event2 = create_event(
        {
            "name": "event2",
            "date": "2021-02-02",
            "end_time": "16:00:00",
            "agenda": [
                {
                    'time_init': '09:00',
                    'time_end': '16:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                }
            ],
        }
    )
    event3 = create_event(
        {
            "name": "event3",
            "date": "2021-02-02",
            "end_time": "18:00:00",
            "agenda": [
                {
                    'time_init': '09:00',
                    'time_end': '18:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                }
            ],
        }
    )

    response = client.get(f"{URI}?not_finished=True")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 2
    assert all(map(lambda e: e['name'] in data_names, [event2, event3]))
    assert not any(map(lambda e: e['name'] in data_names, [event1]))


def test_search_event_finished(monkeypatch):
    mock_date(monkeypatch, {"year": 2021, "month": 2, "day": 2, "hour": 15})
    event = create_event({"name": "event1", "date": "2021-02-01"})
    response = client.get(f"{URI}")
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == event['name']
    assert data[0]['state'] == "Finalizado"


def test_search_event_finished_hour(monkeypatch):
    mock_date(monkeypatch, {"year": 2021, "month": 2, "day": 2, "hour": 15})
    event = create_event(
        {"name": "event1", "date": "2021-02-02", "end_time": "12:00:00"}
    )
    response = client.get(f"{URI}")
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == event['name']
    assert data[0]['state'] == "Finalizado"


def test_max_event_images():
    images = ["image" + str(i) for i in range(1, 11)]
    event_body = create_event_body({"images": images})
    response = client.post(URI, json=event_body)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'max_number_of_images_is_10'


def test_max_minus_one_event_images():
    images = ["image" + str(i) for i in range(1, 10)]
    event_body = create_event_body({"images": images})
    response = client.post(URI, json=event_body)
    assert response.status_code == 201


def test_max_event_faqs():
    faqs = [
        {"question": "question" + str(i), "answer": "answer" + str(i)}
        for i in range(1, 32)
    ]
    event_body = create_event_body({"FAQ": faqs})
    response = client.post(URI, json=event_body)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'max_number_of_faqs_is_30'


def test_max_minus_one_event_faqs():
    faqs = [
        {"question": "question" + str(i), "answer": "answer" + str(i)}
        for i in range(1, 31)
    ]
    event_body = create_event_body({"FAQ": faqs})
    response = client.post(URI, json=event_body)
    assert response.status_code == 201


def test_cancel_event(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    event = create_event({"date": "2024-02-02"})
    response = client.put(f"{URI}/{event['id']}/cancel")
    assert response.status_code == 200
    assert response.json()['state'] == 'Cancelado'


def test_cancel_published_event(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    event = create_event({"date": "2024-02-02"})
    client.put(f"{URI}/{event['id']}/publish")
    response = client.put(f"{URI}/{event['id']}/cancel")
    assert response.status_code == 200
    assert response.json()['state'] == 'Cancelado'


def test_cancel_non_existing_event():
    response = client.put(f"{URI}/1/cancel")
    assert response.status_code == 400
    assert response.json()['detail'] == 'event_not_found'


def create_updated_body(fields):
    body = {
        'name': 'new_aName',
        'description': 'new_aDescription',
        'location': {
            'description': 'new_a location description',
            'lat': 24.4,
            'lng': 33.23,
        },
        'type': 'Arte y Cultura',
        'images': ['new_image1', 'image2', 'image3'],
        'preview_image': 'new_preview_image',
        'date': '2023-03-29',
        'start_time': '10:00:00',
        'end_time': '13:00:00',
        'scan_time': 4,
        'agenda': [
            {
                'time_init': '10:00',
                'time_end': '13:00',
                'owner': 'new Pepe Cibrian',
                'title': 'new Noche de teatro en Bs As',
                'description': 'new Una noche de teatro unica',
            }
        ],
        'vacants': 4,
        'FAQ': [
            {
                'question': 'new se pueden llevar alimentos?',
                'answer': 'new No. No se permiten alimentos ni bebidas en el lugar',
            }
        ],
    }
    for k, v in fields.items():
        body[k] = v
    return body


def test_event_update_borrador(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})

    body = create_event_body({"date": "2024-02-02"})
    event = client.post(URI, json=body).json()
    id = event["id"]

    new_body = create_updated_body({"date": "2024-02-03", "vacants": 5})
    response = client.put(URI + f"/{id}", json=new_body)

    assert response.status_code == 201
    data = response.json()
    add_event_fields(
        new_body,
        {
            "id": event["id"],
            "state": "Borrador",
            "vacants_left": 5,
            "verified_vacants": event["verified_vacants"],
            "organizer": event["organizer"],
            'collaborators': [],
        },
    )
    assert data == new_body


def test_event_update_publicado(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})

    body = create_event_body({"date": "2024-02-02"})
    event = client.post(URI, json=body).json()
    id = event["id"]
    client.put(URI + f"/{id}/publish")

    new_body = create_updated_body({"date": "2024-02-03", "vacants": 5})
    response = client.put(URI + f"/{id}", json=new_body)

    assert response.status_code == 201
    data = response.json()
    add_event_fields(
        new_body,
        {
            "id": event["id"],
            "state": "Publicado",
            "vacants_left": 5,
            "verified_vacants": event["verified_vacants"],
            "organizer": event["organizer"],
            'collaborators': [],
        },
    )
    assert data == new_body


def test_event_update_cancelado(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})

    body = create_event_body({"date": "2024-02-02"})
    id = client.post(URI, json=body).json()["id"]
    client.put(URI + f"/{id}/cancel")

    new_body = create_updated_body({"date": "2024-02-03"})
    response = client.put(URI + f"/{id}", json=new_body)

    assert response.status_code == 400
    assert response.json()['detail'] == 'event_cannot_be_updated'


def test_event_update_terminado(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})

    body = create_event_body({"date": "2022-02-02"})
    event = client.post(URI, json=body).json()
    client.get(URI)
    id = event["id"]

    new_body = create_updated_body({"date": "2022-02-01"})
    response = client.put(URI + f"/{id}", json=new_body)

    assert response.status_code == 400
    assert response.json()['detail'] == 'event_cannot_be_updated'


def test_update_invalid(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    body = create_event_body({"date": "2024-02-02"})
    event = client.post(URI, json=body).json()
    id = event["id"]

    new_body = create_updated_body({"date": "2024-02-02"})

    invalid_variations = {
        'name': ['', 'a'],
        'description': ['', 'a'],
        'location': [
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
        'type': ['', 'NoExistente'],
        'images': [''],
        'preview_image': [''],
        'date': ['', 'a', '-03-29', '2023-03-29T16:00:00'],
        'start_time': ['', 'a', '25:00:00'],
        'end_time': ['', 'a', '25:00:00'],
        'scan_time': ['', 'a', 0, 13],
        'agenda': [
            [
                {
                    'time_init': '09:00',
                    'time_end': '12:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                }
            ],
            [
                {
                    'time_init': '09:00',
                    'time_end': '12:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                },
                {
                    'time_init': '09:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                },
            ],
        ],
        'vacants': ['', 'a', 0],
        'FAQ': [
            [
                {
                    'question': 'se pueden llevar alimentos?',
                }
            ],
            [
                {'question': 'se pueden llevar alimentos?', 'answer': 'Si se puede'},
                {'question': 'Otra pregunta'},
            ],
        ],
    }

    invalid_bodies = generate_invalid(new_body, invalid_variations)

    # NOTE: If one of this tests fails, we don´t get enough information
    # we just know that the hole suit failed.

    for inv_body in invalid_bodies:
        response = client.put(URI + f"/{id}", json=inv_body)
        try:
            assert response.status_code == 422
        except Exception:
            print("Failed body: \n")
            pprint(inv_body)
            raise


def update_event_with_less_vacants_than_left(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})

    body = create_event_body({"date": "2024-02-02", "vacants": 3})
    event = client.post(URI, json=body).json()
    client.put(URI + f"/{event['id']}/publish")
    booking_body = {
        "event_id": event['id'],
        "reserver_id": "123",
    }

    client.post(BOOKING_URI, json=booking_body)
    booking_body2 = {
        "event_id": event['id'],
        "reserver_id": "1232",
    }

    client.post(BOOKING_URI, json=booking_body2)
    id = event["id"]

    new_body = create_updated_body({"date": "2024-02-03", "vacants": 1})
    response = client.put(URI + f"/{id}", json=new_body)

    assert response.status_code == 400
    assert response.json()['detail'] == 'vacants_cannot_be_less_than_bookings'


def test_event_update_vacants(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})

    body = create_event_body({"date": "2024-02-02"})
    event = client.post(URI, json=body).json()
    client.put(URI + f"/{event['id']}/publish")
    id = event["id"]

    booking_body = {
        "event_id": event['id'],
        "reserver_id": "123",
    }

    client.post(BOOKING_URI, json=booking_body)

    new_body = create_updated_body({"date": "2024-02-03", "vacants": 5})
    response = client.put(URI + f"/{id}", json=new_body)

    assert response.status_code == 201
    data = response.json()
    add_event_fields(
        new_body,
        {
            "id": event["id"],
            "state": "Publicado",
            "vacants_left": 4,
            "verified_vacants": event["verified_vacants"],
            "organizer": event["organizer"],
            'collaborators': [],
        },
    )
    assert data == new_body


def test_suspend_event():
    event = create_event()
    client.put(f"{URI}/{event['id']}/publish")
    response = client.put(f"{URI}/{event['id']}/suspend")
    data = response.json()
    assert response.status_code == 200
    assert data['state'] == 'Suspendido'


def test_suspend_event_borrador():
    event = create_event()
    response = client.put(f"{URI}/{event['id']}/suspend")
    assert response.status_code == 400
    assert response.json()['detail'] == 'event_cannot_be_suspended'


def test_suspend_event_cancelado():
    event = create_event()
    client.put(f"{URI}/{event['id']}/cancel")
    response = client.put(f"{URI}/{event['id']}/suspend")
    assert response.status_code == 400
    assert response.json()['detail'] == 'event_cannot_be_suspended'


def test_get_event_finished(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    event = create_event({"date": "2023-02-01"})
    response = client.get(f"{URI}/{event['id']}")
    assert response.status_code == 200
    assert response.json()['state'] == 'Finalizado'


def test_suspend_event_finalizado(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    event = create_event()
    client.get(f"{URI}/{event['id']}")
    response = client.put(f"{URI}/{event['id']}/suspend")
    assert response.status_code == 400
    assert response.json()['detail'] == 'event_cannot_be_suspended'


def test_suspend_non_existing_event():
    response = client.put(f"{URI}/123/suspend")
    assert response.status_code == 400
    assert response.json()['detail'] == 'event_not_found'


def test_unsuspend_event():
    event = create_event()
    client.put(f"{URI}/{event['id']}/publish")
    client.put(f"{URI}/{event['id']}/suspend")
    response = client.put(f"{URI}/{event['id']}/unsuspend")
    data = response.json()
    assert response.status_code == 200
    assert data['state'] == 'Publicado'


def test_unsuspend_event_publicado():
    event = create_event()
    client.put(f"{URI}/{event['id']}/publish")
    response = client.put(f"{URI}/{event['id']}/unsuspend")
    assert response.status_code == 400
    assert response.json()['detail'] == 'event_cannot_be_unsuspended'


def test_unsuspend_event_cancelado():
    event = create_event()
    client.put(f"{URI}/{event['id']}/cancel")
    response = client.put(f"{URI}/{event['id']}/unsuspend")
    assert response.status_code == 400
    assert response.json()['detail'] == 'event_cannot_be_unsuspended'


def test_unsuspend_event_borrador():
    event = create_event()
    response = client.put(f"{URI}/{event['id']}/unsuspend")
    assert response.status_code == 400
    assert response.json()['detail'] == 'event_cannot_be_unsuspended'


def test_unsuspend_event_finalizado(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    event = create_event({"date": "2023-02-01"})
    client.get(f"{URI}/{event['id']}")
    response = client.put(f"{URI}/{event['id']}/unsuspend")
    assert response.status_code == 400
    assert response.json()['detail'] == 'event_cannot_be_unsuspended'


def test_unsuspend_non_existing_event():
    response = client.put(f"{URI}/123/unsuspend")
    assert response.status_code == 400
    assert response.json()['detail'] == 'event_not_found'


def test_suspend_organizer_event(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    event = create_event({"organizer": organizer['id'], "date": "2024-02-01"})
    client.put(f"{URI}/{event['id']}/publish")

    client.put(f"{ORGANIZER_URI}/{organizer['id']}/suspend")
    response = client.get(f"{URI}/{event['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data['state'] == 'Suspendido'


def test_suspend_organizer_event_borrador(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    event = create_event({"organizer": organizer['id'], "date": "2024-02-01"})

    client.put(f"{ORGANIZER_URI}/{organizer['id']}/suspend")
    response = client.get(f"{URI}/{event['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data['state'] == 'Borrador'


def test_suspend_organizer_event_cancelado(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    event = create_event({"organizer": organizer['id'], "date": "2024-02-01"})
    client.put(f"{URI}/{event['id']}/cancel")

    client.put(f"{ORGANIZER_URI}/{organizer['id']}/suspend")
    response = client.get(f"{URI}/{event['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data['state'] == 'Cancelado'


def test_suspend_organizer_event_terminado(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    event = create_event({"organizer": organizer['id'], "date": "2022-02-01"})

    client.put(f"{ORGANIZER_URI}/{organizer['id']}/suspend")
    response = client.get(f"{URI}/{event['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data['state'] == 'Finalizado'


def test_suspend_organizer_events(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    event1 = create_event({"organizer": organizer['id'], "date": "2024-02-01"})
    client.put(f"{URI}/{event1['id']}/publish")
    event2 = create_event({"organizer": organizer['id'], "date": "2024-02-01"})
    client.put(f"{URI}/{event2['id']}/publish")

    client.put(f"{ORGANIZER_URI}/{organizer['id']}/suspend")
    response = client.get(f"{URI}/{event1['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data['state'] == 'Suspendido'
    response = client.get(f"{URI}/{event2['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data['state'] == 'Suspendido'


def test_unsuspend_organizer_events(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    event1 = create_event({"organizer": organizer['id'], "date": "2024-02-01"})
    client.put(f"{URI}/{event1['id']}/publish")
    event2 = create_event({"organizer": organizer['id'], "date": "2024-02-01"})
    client.put(f"{URI}/{event2['id']}/publish")

    client.put(f"{ORGANIZER_URI}/{organizer['id']}/suspend")
    client.put(f"{ORGANIZER_URI}/{organizer['id']}/unsuspend")
    response = client.get(f"{URI}/{event1['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data['state'] == 'Publicado'
    response = client.get(f"{URI}/{event2['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data['state'] == 'Publicado'


def test_unsuspend_organizer_event_borrador(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    event1 = create_event({"organizer": organizer['id'], "date": "2024-02-01"})

    client.put(f"{ORGANIZER_URI}/{organizer['id']}/suspend")
    client.put(f"{ORGANIZER_URI}/{organizer['id']}/unsuspend")
    response = client.get(f"{URI}/{event1['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data['state'] == 'Borrador'


def test_unsuspend_organizer_event_cancelado(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    event1 = create_event({"organizer": organizer['id'], "date": "2024-02-01"})
    client.put(f"{URI}/{event1['id']}/cancel")

    client.put(f"{ORGANIZER_URI}/{organizer['id']}/suspend")
    client.put(f"{ORGANIZER_URI}/{organizer['id']}/unsuspend")
    response = client.get(f"{URI}/{event1['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data['state'] == 'Cancelado'


def test_unsuspend_organizer_event_terminado(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    event1 = create_event({"organizer": organizer['id'], "date": "2022-02-01"})

    client.put(f"{ORGANIZER_URI}/{organizer['id']}/suspend")
    client.put(f"{ORGANIZER_URI}/{organizer['id']}/unsuspend")
    response = client.get(f"{URI}/{event1['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data['state'] == 'Finalizado'


def test_add_collaborator():
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    collaborator = create_organizer_body({"id": "1234", "email": "collab@gmail.com"})
    collaborator = client.post(ORGANIZER_URI, json=collaborator).json()
    event = create_event({"organizer": organizer['id']})
    response = client.put(
        f"{URI}/{event['id']}/add_collaborator/{collaborator['email']}"
    )
    data = response.json()
    assert response.status_code == 200
    assert len(data['collaborators']) == 1
    assert data['collaborators'][0]["id"] == collaborator['id']
    assert data['collaborators'][0]["email"] == collaborator['email']


def test_add_collaborator_two():
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    collaborator = create_organizer_body({"id": "1234", "email": "collab@gmail.com"})
    collaborator = client.post(ORGANIZER_URI, json=collaborator).json()
    collaborator2 = create_organizer_body({"id": "1254", "email": "collab2@gmail.com"})
    collaborator2 = client.post(ORGANIZER_URI, json=collaborator2).json()

    event = create_event({"organizer": organizer['id']})
    client.put(f"{URI}/{event['id']}/add_collaborator/{collaborator['email']}")
    client.put(f"{URI}/{event['id']}/add_collaborator/{collaborator2['email']}")
    response = client.get(f"{URI}/{event['id']}")
    data = response.json()
    assert response.status_code == 200
    assert len(data['collaborators']) == 2
    assert data['collaborators'][0]["id"] == collaborator['id']
    assert data['collaborators'][0]["email"] == collaborator['email']
    assert data['collaborators'][1]["id"] == collaborator2['id']
    assert data['collaborators'][1]["email"] == collaborator2['email']


def test_add_collaborator_twice():
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    collaborator = create_organizer_body({"id": "1234", "email": "collab@gmail.com"})
    collaborator = client.post(ORGANIZER_URI, json=collaborator).json()

    event = create_event({"organizer": organizer['id']})
    client.put(f"{URI}/{event['id']}/add_collaborator/{collaborator['email']}")
    response = client.put(
        f"{URI}/{event['id']}/add_collaborator/{collaborator['email']}"
    )
    data = response.json()
    assert response.status_code == 200
    assert len(data['collaborators']) == 1
    assert data['collaborators'][0]["id"] == collaborator['id']
    assert data['collaborators'][0]["email"] == collaborator['email']


def test_add_collaborator_not_found():
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    event = create_event({"organizer": organizer['id']})
    response = client.put(f"{URI}/{event['id']}/add_collaborator/notfound@gmail.com")
    assert response.status_code == 400
    assert response.json()['detail'] == 'collaborator_not_found'


def test_add_collaborator_non_existing_event():
    collaborator = create_organizer_body()
    collaborator = client.post(ORGANIZER_URI, json=collaborator).json()
    response = client.put(f"{URI}/999999/add_collaborator/{collaborator['email']}")
    assert response.status_code == 400
    assert response.json()['detail'] == 'event_not_found'


def test_remove_collaborator():
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    collaborator = create_organizer_body({"id": "1234", "email": "collab@gmail.com"})
    collaborator = client.post(ORGANIZER_URI, json=collaborator).json()
    event = create_event({"organizer": organizer['id']})
    client.put(f"{URI}/{event['id']}/add_collaborator/{collaborator['email']}")
    response = client.put(
        f"{URI}/{event['id']}/remove_collaborator/{collaborator['id']}"
    )
    data = response.json()
    assert response.status_code == 200
    assert len(data['collaborators']) == 0


def test_remove_collaborator_twice():
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    collaborator = create_organizer_body({"id": "1234", "email": "collab@gmail.com"})
    collaborator = client.post(ORGANIZER_URI, json=collaborator).json()
    event = create_event({"organizer": organizer['id']})
    client.put(f"{URI}/{event['id']}/add_collaborator/{collaborator['email']}")
    client.put(f"{URI}/{event['id']}/remove_collaborator/{collaborator['id']}")
    response = client.put(
        f"{URI}/{event['id']}/remove_collaborator/{collaborator['id']}"
    )
    data = response.json()
    assert response.status_code == 200
    assert len(data['collaborators']) == 0


def test_remove_collaborator_non_existing():
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    event = create_event({"organizer": organizer['id']})
    response = client.put(f"{URI}/{event['id']}/remove_collaborator/999999")
    data = response.json()
    assert response.status_code == 200
    assert len(data['collaborators']) == 0


def test_remove_collaborator_two():
    organizer = create_organizer_body()
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    collaborator = create_organizer_body({"id": "1234", "email": "collab@gmail.com"})
    collaborator = client.post(ORGANIZER_URI, json=collaborator).json()
    collaborator2 = create_organizer_body({"id": "1254", "email": "collab2@gmail.com"})
    collaborator2 = client.post(ORGANIZER_URI, json=collaborator2).json()

    event = create_event({"organizer": organizer['id']})
    client.put(f"{URI}/{event['id']}/add_collaborator/{collaborator['email']}")
    client.put(f"{URI}/{event['id']}/add_collaborator/{collaborator2['email']}")

    client.put(f"{URI}/{event['id']}/remove_collaborator/{collaborator['id']}")
    response = client.get(f"{URI}/{event['id']}")
    data = response.json()
    assert response.status_code == 200
    assert len(data['collaborators']) == 1
    assert data['collaborators'][0]["id"] == collaborator2['id']
    assert data['collaborators'][0]["email"] == collaborator2['email']


def test_remove_collaborator_non_existing_event():
    collaborator = create_organizer_body()
    collaborator = client.post(ORGANIZER_URI, json=collaborator).json()
    response = client.put(f"{URI}/999999/remove_collaborator/{collaborator['email']}")
    assert response.status_code == 400
    assert response.json()['detail'] == 'event_not_found'


def test_search_event_collaborator(monkeypatch):
    mock_date(monkeypatch, {"year": 2021, "month": 2, "day": 10, "hour": 15})
    organizer = create_organizer_body({"id": "1234", "email": "collab@email.com"})
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    event1 = create_event({"name": "event 1", "organizer": "omar"})
    event2 = create_event({"name": "event 2", "organizer": "juan"})
    event3 = create_event({"name": "event 3", "organizer": "omar"})
    event4 = create_event({"name": "event 4", "organizer": "gabriel"})

    client.put(f"{URI}/{event2['id']}/add_collaborator/{organizer['email']}")
    client.put(f"{URI}/{event3['id']}/add_collaborator/{organizer['email']}")

    response = client.get(f"{URI}?organizer=1234")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 2
    assert all(map(lambda e: e['name'] in data_names, [event2, event3]))
    assert not any(map(lambda e: e['name'] in data_names, [event1, event4]))


def test_search_event_collaborator_empty():
    organizer = create_organizer_body({"id": "1234", "email": "collab@email.com"})
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    event1 = create_event({"name": "event 1", "organizer": "omar"})
    event2 = create_event({"name": "event 2", "organizer": "juan"})
    event3 = create_event({"name": "event 3", "organizer": "omar"})
    event4 = create_event({"name": "event 4", "organizer": "gabriel"})

    response = client.get(f"{URI}?organizer=1234")
    data = response.json()

    assert len(data) == 0


def test_search_event_collaborator_two(monkeypatch):
    mock_date(monkeypatch, {"year": 2021, "month": 2, "day": 10, "hour": 15})
    organizer = create_organizer_body({"id": "1234", "email": "collab@email.com"})
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    organizer2 = create_organizer_body({"id": "12342", "email": "collab2@email.com"})
    organizer2 = client.post(ORGANIZER_URI, json=organizer2).json()

    event1 = create_event({"name": "event 1", "organizer": "omar"})
    event2 = create_event({"name": "event 2", "organizer": "juan"})
    event3 = create_event({"name": "event 3", "organizer": "omar"})
    event4 = create_event({"name": "event 4", "organizer": "gabriel"})

    client.put(f"{URI}/{event2['id']}/add_collaborator/{organizer['email']}")
    client.put(f"{URI}/{event3['id']}/add_collaborator/{organizer['email']}")

    response = client.get(f"{URI}?organizer=12342")
    data = response.json()

    assert len(data) == 0


def test_search_event_collaborator_two_has_events(monkeypatch):
    mock_date(monkeypatch, {"year": 2021, "month": 2, "day": 10, "hour": 15})
    organizer = create_organizer_body({"id": "1234", "email": "collab@email.com"})
    organizer = client.post(ORGANIZER_URI, json=organizer).json()
    organizer2 = create_organizer_body({"id": "12342", "email": "collab2@email.com"})
    organizer2 = client.post(ORGANIZER_URI, json=organizer2).json()

    event1 = create_event({"name": "event 1", "organizer": "omar"})
    event2 = create_event({"name": "event 2", "organizer": "juan"})
    event3 = create_event({"name": "event 3", "organizer": "omar"})
    event4 = create_event({"name": "event 4", "organizer": "gabriel"})

    client.put(f"{URI}/{event2['id']}/add_collaborator/{organizer['email']}")
    client.put(f"{URI}/{event3['id']}/add_collaborator/{organizer['email']}")
    client.put(f"{URI}/{event4['id']}/add_collaborator/{organizer2['email']}")
    client.put(f"{URI}/{event3['id']}/add_collaborator/{organizer2['email']}")

    response = client.get(f"{URI}?organizer=1234")
    data = response.json()
    data_names = map(lambda e: e['name'], data)

    assert len(data) == 2
    assert all(map(lambda e: e['name'] in data_names, [event2, event3]))
    assert not any(map(lambda e: e['name'] in data_names, [event1, event4]))


def test_search_event_collaborator_has_events_and_is_organizer(monkeypatch):
    mock_date(monkeypatch, {"year": 2021, "month": 2, "day": 10, "hour": 15})
    organizer = create_organizer_body({"id": "1234", "email": "collab@email.com"})
    organizer = client.post(ORGANIZER_URI, json=organizer).json()

    event1 = create_event({"name": "event 1", "organizer": organizer["id"]})
    event2 = create_event({"name": "event 2", "organizer": "juan"})
    event3 = create_event({"name": "event 3", "organizer": "omar"})
    event4 = create_event({"name": "event 4", "organizer": "gabriel"})

    client.put(f"{URI}/{event2['id']}/add_collaborator/{organizer['email']}")
    client.put(f"{URI}/{event3['id']}/add_collaborator/{organizer['email']}")

    response = client.get(f"{URI}?organizer=1234")
    data = response.json()
    data_names = map(lambda e: e['name'], data)

    assert len(data) == 3
    assert all(map(lambda e: e['name'] in data_names, [event1, event2, event3]))
    assert not any(map(lambda e: e['name'] in data_names, [event4]))


def test_search_event_by_organizer_4_days_ago(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 10, "hour": 15})

    event1 = create_event(
        {"name": "event 1", "organizer": "omar", "date": "2023-02-05"}
    )
    event2 = create_event(
        {
            "name": "event 2",
            "organizer": "omar",
            "date": "2023-02-06",
            "start_time": "10:00",
            "end_time": "14:00",
            "agenda": [
                {
                    'time_init': '10:00',
                    'time_end': '14:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                }
            ],
        }
    )
    event3 = create_event(
        {"name": "event 3", "organizer": "omar", "date": "2023-02-07"}
    )
    event4 = create_event(
        {"name": "event 4", "organizer": "gabriel", "date": "2023-02-11"}
    )

    response = client.get(f"{URI}?organizer=omar")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 1
    assert all(map(lambda e: e['name'] in data_names, [event3]))
    assert not any(map(lambda e: e['name'] in data_names, [event2, event1, event4]))


def test_create_event_scan_time():
    body = create_event({"scan_time": 10})
    response = client.post(URI, json=body)
    response_data = response.json()
    assert response.status_code == 201
    assert response_data['scan_time'] == 10


def test_search_event_by_organizer_is_ordered_by_hour(monkeypatch):
    mock_date(monkeypatch, {"year": 2021, "month": 2, "day": 10, "hour": 15})
    event1 = create_event(
        {
            "name": "event 1",
            "organizer": "omar",
            "date": "2021-02-12",
            "start_time": "10:00",
            "end_time": "14:00",
            "agenda": [
                {
                    "time_init": "10:00",
                    "time_end": "14:00",
                    "owner": "Pepe Cibrian",
                    "title": "Noche de teatro en Bs As",
                    "description": "Una noche de teatro unica",
                }
            ],
        }
    )
    event2 = create_event({"name": "event 2", "organizer": "juan"})
    event3 = create_event(
        {
            "name": "event 3",
            "organizer": "omar",
            "date": "2021-02-12",
            "start_time": "09:00",
            "end_time": "14:00",
            "agenda": [
                {
                    "time_init": "09:00",
                    "time_end": "14:00",
                    "owner": "Pepe Cibrian",
                    "title": "Noche de teatro en Bs As",
                    "description": "Una noche de teatro unica",
                }
            ],
        }
    )
    event4 = create_event({"name": "event 4", "organizer": "gabriel"})

    response = client.get(f"{URI}?organizer=omar")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 2
    assert all(map(lambda e: e['name'] in data_names, [event3, event1]))
    assert not any(map(lambda e: e['name'] in data_names, [event2, event4]))


def test_search_event_by_organizer_is_ordered_by_date(monkeypatch):
    mock_date(monkeypatch, {"year": 2021, "month": 2, "day": 10, "hour": 15})
    event1 = create_event(
        {"name": "event 1", "organizer": "omar", "date": "2021-02-12"}
    )
    event2 = create_event({"name": "event 2", "organizer": "juan"})
    event3 = create_event(
        {
            "name": "event 3",
            "organizer": "omar",
            "date": "2021-02-11",
        }
    )
    event4 = create_event({"name": "event 4", "organizer": "gabriel"})

    response = client.get(f"{URI}?organizer=omar")
    data = response.json()

    data_names = map(lambda e: e['name'], data)

    assert len(data) == 2
    assert all(map(lambda e: e['name'] in data_names, [event3, event1]))
    assert not any(map(lambda e: e['name'] in data_names, [event2, event4]))


def test_create_event_with_end_time_less_than_start_time():
    body = create_event_body({"start_time": "14:00:00", "end_time": "10:00:00"})
    response = client.post(URI, json=body)
    assert response.status_code == 400
    assert response.json()['detail'] == 'end_time_must_be_greater_than_start_time'


def test_create_event_with_end_time_same_than_start_time():
    body = create_event_body({"start_time": "14:00:00", "end_time": "14:00:00"})
    response = client.post(URI, json=body)
    assert response.status_code == 400
    assert response.json()['detail'] == 'end_time_must_be_greater_than_start_time'


def test_create_event_with_agenda_not_ending():
    body = create_event_body(
        {
            "agenda": [
                {
                    'time_init': '09:00',
                    'time_end': '10:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                },
                {
                    'time_init': '10:00',
                    'time_end': '11:00',
                    'owner': 'Agustin',
                    'title': 'Noche de teatro en Bs As 2',
                    'description': 'Una noche de teatro unica 2',
                },
            ]
        }
    )
    response = client.post(URI, json=body)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'agenda_can_not_end_before_event_ends'


def update_event_time_error(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})

    body = create_event_body(
        {
            "date": "2024-02-02",
            "start_time": "10:00",
            "end_time": "12:00",
            "agenda": [
                {
                    'time_init': '10:00',
                    'time_end': '12:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                }
            ],
        }
    )
    event = client.post(URI, json=body).json()
    id = event['id']

    new_body = create_updated_body(
        {
            "start_time": "11:00",
            "end_time": "10:00",
            "agenda": [
                {
                    'time_init': '11:00',
                    'time_end': '10:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                }
            ],
        }
    )
    response = client.put(URI + f"/{id}", json=new_body)

    assert response.status_code == 400
    assert response.json()['detail'] == 'end_time_must_be_greater_than_start_time'


def test_update_event_start_time_but_not_agenda(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})

    body = create_event_body(
        {
            "date": "2024-02-02",
            "start_time": "10:00",
            "end_time": "12:00",
            "agenda": [
                {
                    'time_init': '10:00',
                    'time_end': '12:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                }
            ],
        }
    )
    event = client.post(URI, json=body).json()
    id = event['id']

    new_body = create_updated_body({"start_time": "10:00", "agenda": None})
    response = client.put(URI + f"/{id}", json=new_body)

    assert response.status_code == 400
    assert response.json()['detail'] == 'time_can_not_be_updated_without_agenda'


def test_update_event_end_time_but_not_agenda(monkeypatch):
    mock_date(monkeypatch, {"year": 2023, "month": 2, "day": 2, "hour": 15})

    body = create_event_body(
        {
            "date": "2024-02-02",
            "start_time": "10:00",
            "end_time": "12:00",
            "agenda": [
                {
                    'time_init': '10:00',
                    'time_end': '12:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                }
            ],
        }
    )
    event = client.post(URI, json=body).json()
    id = event['id']

    new_body = create_updated_body({"end_time": "16:00", "agenda": None})
    response = client.put(URI + f"/{id}", json=new_body)

    assert response.status_code == 400
    assert response.json()['detail'] == 'time_can_not_be_updated_without_agenda'


def test_update_event_with_empty_space_in_agenda():
    body = create_event_body(
        {
            "date": "2024-02-02",
            "start_time": "09:00",
            "end_time": "13:00",
            "agenda": [
                {
                    'time_init': '09:00',
                    'time_end': '13:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                }
            ],
        }
    )
    event = client.post(URI, json=body).json()
    id = event['id']

    new_body = create_updated_body(
        {
            "agenda": [
                {
                    'time_init': '09:00',
                    'time_end': '10:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                },
                {
                    'time_init': '11:00',
                    'time_end': '13:00',
                    'owner': 'Agustin',
                    'title': 'Noche de teatro en Bs As 2',
                    'description': 'Una noche de teatro unica 2',
                },
            ]
        }
    )
    response = client.put(URI + f"/{id}", json=new_body)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'agenda_can_not_have_empty_spaces'


def test_update_event_with_overlap_in_agenda():
    body = create_event_body(
        {
            "date": "2024-02-02",
            "start_time": "09:00",
            "end_time": "13:00",
            "agenda": [
                {
                    'time_init': '09:00',
                    'time_end': '13:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                }
            ],
        }
    )
    event = client.post(URI, json=body).json()
    id = event['id']

    new_body = create_updated_body(
        {
            "agenda": [
                {
                    'time_init': '09:00',
                    'time_end': '11:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                },
                {
                    'time_init': '10:00',
                    'time_end': '13:00',
                    'owner': 'Agustin',
                    'title': 'Noche de teatro en Bs As 2',
                    'description': 'Una noche de teatro unica 2',
                },
            ]
        }
    )
    response = client.put(URI + f"/{id}", json=new_body)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'agenda_can_not_have_overlap'


def test_update_event_with_agenda_ending_after_event():
    body = create_event_body(
        {
            "date": "2024-02-02",
            "start_time": "09:00",
            "end_time": "13:00",
            "agenda": [
                {
                    'time_init': '09:00',
                    'time_end': '13:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                }
            ],
        }
    )
    event = client.post(URI, json=body).json()
    id = event['id']

    new_body = create_updated_body(
        {
            "agenda": [
                {
                    'time_init': '09:00',
                    'time_end': '11:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                },
                {
                    'time_init': '11:00',
                    'time_end': '14:00',
                    'owner': 'Agustin',
                    'title': 'Noche de teatro en Bs As 2',
                    'description': 'Una noche de teatro unica 2',
                },
            ]
        }
    )
    response = client.put(URI + f"/{id}", json=new_body)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'agenda_can_not_end_after_event_end'


def test_update_event_with_agenda_not_ending():
    body = create_event_body(
        {
            "date": "2024-02-02",
            "start_time": "09:00",
            "end_time": "13:00",
            "agenda": [
                {
                    'time_init': '09:00',
                    'time_end': '13:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                }
            ],
        }
    )
    event = client.post(URI, json=body).json()
    id = event['id']

    new_body = create_updated_body(
        {
            "agenda": [
                {
                    'time_init': '09:00',
                    'time_end': '10:00',
                    'owner': 'Pepe Cibrian',
                    'title': 'Noche de teatro en Bs As',
                    'description': 'Una noche de teatro unica',
                },
                {
                    'time_init': '10:00',
                    'time_end': '11:00',
                    'owner': 'Agustin',
                    'title': 'Noche de teatro en Bs As 2',
                    'description': 'Una noche de teatro unica 2',
                },
            ]
        }
    )
    response = client.put(URI + f"/{id}", json=new_body)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'agenda_can_not_end_before_event_ends'
