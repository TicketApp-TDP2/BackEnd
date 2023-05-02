from fastapi.testclient import TestClient
from pprint import pprint
import pytest

from app.app import app
from test.utils import generate_invalid, mock_date
import datetime

client = TestClient(app)

URI = 'api/events'
BOOKING_URI = 'api/bookings'


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


def test_search_event_by_organizer():
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


def test_search_event_with_multiple_filters():
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
        {"name": "event2", "date": "2021-02-02", "end_time": "16:00:00"}
    )
    event3 = create_event(
        {"name": "event3", "date": "2021-02-02", "end_time": "18:00:00"}
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
