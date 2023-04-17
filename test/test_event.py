from fastapi.testclient import TestClient
from pprint import pprint
import pytest

from app.app import app
from test.utils import generate_invalid, mock_date
import datetime

client = TestClient(app)

URI = 'api/events'


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
    assert data['detail'] == "Event not found"


def test_get_event_exists():
    body = create_event()
    response = client.post(URI, json=body)
    id = response.json()['id']
    expected_response = body.copy()
    expected_response = add_event_fields(
        expected_response,
        {'id': id, 'vacants_left': expected_response['vacants'], 'state': 'Borrador'},
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
    assert data['detail'] == 'Agenda can not have empty spaces'


def test_create_event_empty_agenda():
    body = create_event_body({"agenda": []})
    response = client.post(URI, json=body)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'Agenda can not be empty'


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
    assert data['detail'] == 'Agenda can not have overlap'


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
    assert data['detail'] == 'Agenda can not end after event end'


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
    assert data['detail'] == 'Event is not in Borrador state'


def test_publish_non_existing_event():
    response = client.put(f"{URI}/1/publish")
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'Event not found'


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
    assert data['detail'] == 'Max number of images is 10'


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
    assert data['detail'] == 'Max number of faqs is 30'


def test_max_minus_one_event_faqs():
    faqs = [
        {"question": "question" + str(i), "answer": "answer" + str(i)}
        for i in range(1, 31)
    ]
    event_body = create_event_body({"FAQ": faqs})
    response = client.post(URI, json=event_body)
    assert response.status_code == 201
