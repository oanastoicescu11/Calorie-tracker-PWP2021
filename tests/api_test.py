import json
import datetime
import pytest
from tapi import db, create_app
from tapi.constants import *
from tapi.models import Person, Meal, MealRecord
from tapi.resources.mealrecord import make_mealrecord_handle
# BEGIN Original fixture setup taken from the Exercise example and then modified further

import os
import tempfile
from sqlalchemy.engine import Engine
from sqlalchemy import event

CONTROL_COLLECTION = "collection"
APPLICATION_JSON = "application/json"


@pytest.fixture
def app():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()

    yield app
    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)


# TODO: check if this is needed at all
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# END of the Exercise example origin code
def add_person_to_db(person_id):
    p = Person()
    p.id = person_id
    db.session.add(p)
    db.session.commit()


def add_meal_to_db(meal_id):
    m = Meal()
    m.id = meal_id
    m.name = "Oatmeal"
    m.servings = 4
    m.description = "Simple breakfast Oatmeal cooked in water"
    db.session.add(m)
    db.session.commit()


def add_mealrecord_to_db(person_id, meal_id, timestamp):
    m = MealRecord()
    m.person_id = person_id
    m.meal_id = meal_id
    m.timestamp = timestamp
    m.amount = 4
    db.session.add(m)
    db.session.commit()


# from Juha's course exercise content, just a bit modified BEGIN
def assert_content_type(resp):
    assert resp.headers['Content-Type'] == MASON


def assert_control_collection(resp, href):
    assert_control(resp, CONTROL_COLLECTION, href)


def assert_namespace(resp):
    body = json.loads(resp.data)
    assert 'cameta' in body['@namespaces']


def assert_control_profile_error(resp):
    body = json.loads(resp.data)
    assert body["@error"] is not None
    assert body['resource_url'] is not None
    assert_control(resp, 'profile', ERROR_PROFILE)


def assert_self_url(resp, href):
    assert_control(resp, "self", href)


def assert_control(resp, control, href):
    body = json.loads(resp.data)
    assert body['@controls'][control]['href'] == href


def assert_post_control_properties(resp, control):
    body = json.loads(resp.data)
    assert body['@controls'][control]['schema']
    assert body['@controls'][control]['schema']['type']
    assert body['@controls'][control]['schema']['properties']
    assert body['@controls'][control]['schema']['required']
    assert body['@controls'][control]['method']
    assert body['@controls'][control]['encoding']
    assert body['@controls'][control]['href']


def assert_edit_control_properties(resp, control):
    assert_post_control_properties(resp, control)


def assert_control_delete(resp, href):
    body = json.loads(resp.data)
    delete = NS + ":delete"
    assert_control(resp, delete, href)
    assert body['@controls'][delete]['method'] == "DELETE"


# from Juha's course exercise content, just a bit modified END

def test_person_collection_200(app):
    with app.app_context():
        # create person for testing and put it into the db
        person_id = "123"
        add_person_to_db(person_id)
        # obtain test client and make request
        client = app.test_client()
        r = client.get(ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION, method="GET")
        # assert correct response code and data
        assert r.status_code == 200
        assert_content_type(r)
        body = json.loads(r.data)
        assert body['items'][0]['id'] == person_id
        assert_namespace(r)
        assert_self_url(r, ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION)
        assert_control(r, NS + ":persons-all", ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION)
        assert_control(r, NS + ":add-person", ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION)
        assert_post_control_properties(r, NS + ":add-person")


def test_get_person_200(app):
    with app.app_context():
        # create person for testing and put it into the db
        person_id = "123"
        add_person_to_db(person_id)
        # obtain test client and make request
        client = app.test_client()
        r = client.get(ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION + person_id + '/', method="GET")
        # assert correct response code and data
        assert r.status_code == 200
        assert_content_type(r)
        assert_control_collection(r, ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION)
        assert_self_url(r, ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION + person_id + '/')
        body = json.loads(r.data)
        assert body['id'] == person_id
        assert_namespace(r)
        assert_control_delete(r, ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION + person_id + '/')


def test_get_person_404(app):
    with app.app_context():
        person_id = "this person does not exist"
        client = app.test_client()
        r = client.get(ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION + person_id + '/', method="GET")
        # assert correct response code and data
        assert r.status_code == 404
        assert_content_type(r)
        assert_control_profile_error(r)


VALID_PERSON = {'id': '123'}
INVALID_PERSON_DATA = [
    {'name': 'this person does not have id field defined'},
    {
        'id': "too long id as it can be at most of 127 \
        characters long and this is at least longer than \
        that, in fact this is just about long enough to \
        go over with 159 chars"},
    {'id': "special characters like #$%^^"},
    {'id': None},
    {'id': ""}]


def test_post_person_201(app):
    with app.app_context():
        client = app.test_client()
        r = client.post(
            ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION,
            data=json.dumps(VALID_PERSON),
            content_type=APPLICATION_JSON,
            method='POST')
        assert r.status_code == 201
        # Location URL is absolute
        assert (r.headers['Location']).startswith("http://")
        assert (r.headers['Location']).endswith(
            ROUTE_ENTRYPOINT +
            ROUTE_PERSON_COLLECTION +
            VALID_PERSON['id'] + '/')


def test_post_person_409(app):
    with app.app_context():
        client = app.test_client()
        r = client.post(
            ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION,
            data=json.dumps(VALID_PERSON),
            content_type=APPLICATION_JSON,
            method='POST')
        assert r.status_code == 201
        r = client.post(
            ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION,
            data=json.dumps(VALID_PERSON),
            content_type=APPLICATION_JSON,
            method='POST')
        assert r.status_code == 409
        assert_content_type(r)
        assert_control_profile_error(r)


def test_post_meal_415(app):
    with app.app_context():
        client = app.test_client()
        invalid_content_type = 'text/plain'
        r = client.post(
            ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION,
            data=json.dumps(VALID_PERSON),
            content_type=invalid_content_type,
            method='POST')
        assert r.status_code == 415
        assert_content_type(r)
        assert_control_profile_error(r)


def test_post_person_400(app):
    with app.app_context():
        client = app.test_client()
        for d in INVALID_PERSON_DATA:
            r = client.post(
                ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION,
                data=json.dumps(d),
                content_type=APPLICATION_JSON,
                method='POST')
            assert r.status_code == 400
            assert_content_type(r)
            assert_control_profile_error(r)


def test_delete_person_204(app):
    with app.app_context():
        client = app.test_client()
        r = client.post(
            ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION,
            data=json.dumps(VALID_PERSON),
            content_type=APPLICATION_JSON,
            method='POST')
        assert r.status_code == 201
        r = client.delete(ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION + VALID_PERSON['id'] + '/', method="DELETE")
        assert r.status_code == 204


def test_delete_person_404(app):
    with app.app_context():
        client = app.test_client()
        r = client.delete(ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION + VALID_PERSON['id'] + '/', method="DELETE")
        assert r.status_code == 404
        assert_content_type(r)
        assert_control_profile_error(r)


def test_meal_collection_200(app):
    with app.app_context():
        # create meal for testing and put it into the db
        meal_id = "oatmeal"
        add_meal_to_db(meal_id)
        # obtain test client and make request
        client = app.test_client()
        r = client.get(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION, method="GET")
        # assert correct response code and data
        assert r.status_code == 200
        assert_content_type(r)
        body = json.loads(r.data)
        assert body['items'][0]['id'] == meal_id
        assert_namespace(r)
        assert_self_url(r, ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION)
        assert_control(r, NS + ":meals-all", ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION)
        assert_control(r, NS + ":add-meal", ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION)
        assert_post_control_properties(r, NS + ":add-meal")


def test_get_meal_200(app):
    with app.app_context():
        # create meal for testing and put it into the db
        meal_id = "oatmeal"
        add_meal_to_db(meal_id)
        # obtain test client and make request
        client = app.test_client()
        r = client.get(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + '/', method="GET")
        # assert correct response code and data
        assert r.status_code == 200
        assert_content_type(r)
        assert_self_url(r, ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + '/')
        assert_control_collection(r, ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION)
        assert_control(r, 'profile', URL_PROFILE)
        body = json.loads(r.data)
        assert body['id'] == meal_id
        assert_namespace(r)
        assert_control_delete(r, ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + '/')
        assert_control(r, NS + ":meals-all", ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION)
        assert_edit_control_properties(r, NS + ":edit-meal")


def test_get_meal_404(app):
    with app.app_context():
        # create meal for testing and put it into the db
        meal_id = "this meal does not exists"
        # obtain test client and make request
        client = app.test_client()
        r = client.get(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + '/', method="GET")
        # assert correct response code and data
        assert r.status_code == 404
        assert_content_type(r)
        assert_control_profile_error(r)


VALID_MEAL = {
    'id': 'myoatmeal',
    'name': 'My Oatmeal',
    'description': 'normal oatmeal',
    'servings': 3
}


def test_post_meal_201(app):
    with app.app_context():
        client = app.test_client()
        r = client.post(
            ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION,
            data=json.dumps(VALID_MEAL),
            content_type=APPLICATION_JSON,
            method='POST')
        assert r.status_code == 201
        # Location URL is absolute
        assert (r.headers['Location']).startswith("http://")
        assert (r.headers['Location']).endswith(ROUTE_ENTRYPOINT +
                                                ROUTE_MEAL_COLLECTION +
                                                VALID_MEAL['id'] + '/')


def test_post_meal_409(app):
    with app.app_context():
        client = app.test_client()
        r = client.post(
            ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION,
            data=json.dumps(VALID_MEAL),
            content_type=APPLICATION_JSON,
            method='POST')
        assert r.status_code == 201
        r = client.post(
            ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION,
            data=json.dumps(VALID_MEAL),
            content_type=APPLICATION_JSON,
            method='POST')
        assert r.status_code == 409
        assert_content_type(r)
        assert_control_profile_error(r)


INVALID_MEAL_DATA = [
    {'id': '',
     'name': 'emptyid',
     'description': 'normal oatmeal',
     'servings': 3},
    {'name': 'missingid',
     'description': 'normal oatmeal',
     'servings': 3},
    {'id': 'my oatmeal',
     'name': 'space in id',
     'description': 'normal oatmeal',
     'servings': 3},
    {'id': 'foobar%$^&',
     'name': 'illegal characters in id',
     'description': 'normal oatmeal',
     'servings': 3},
    {'id': str().ljust(200, 'a'),
     'name': 'too long id',
     'description': 'normal oatmeal',
     'servings': 3},
    {'id': 'oatmeal',
     'name': 'too long name' + str().ljust(200, 'a'),
     'description': 'normal oatmeal',
     'servings': 3},
    {'id': 'oatmealnamemissing',
     'description': 'normal oatmeal',
     'servings': 3},
    {'id': 'oatmeal',
     'name': 'too long desc',
     'description': 'normal oatmeal' + str().ljust(10000, 'a'),
     'servings': 3},
    {'id': 'servingsmissing',
     'name': 'too long name',
     'description': 'normal oatmeal'},
    {'id': 'oatmeal',
     'name': 'servings is string',
     'description': 'normal oatmeal',
     'servings': "3"},
]


def test_post_meal_400(app):
    with app.app_context():
        client = app.test_client()
        for d in INVALID_MEAL_DATA:
            r = client.post(
                ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION,
                data=json.dumps(d),
                content_type=APPLICATION_JSON,
                method='POST')
            assert r.status_code == 400
            assert_content_type(r)
            assert_control_profile_error(r)


def test_put_meal_204(app):
    with app.app_context():
        client = app.test_client()
        meal_id = 'oatmeal'
        m = Meal()
        m.id = meal_id
        m.name = "Oatmeal"
        m.servings = 4
        m.description = "Simple breakfast Oatmeal cooked in water"
        db.session.add(m)
        db.session.commit()

        name = 'new name'
        desc = 'new desc'
        meal = {
            'id': meal_id,
            'name': name,
            'servings': 4,
            'description': desc
        }

        r = client.put(
            ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + '/',
            data=json.dumps(meal),
            content_type=APPLICATION_JSON,
            method='put')
        assert r.status_code == 204
        assert_content_type(r)


def test_put_meal_404(app):
    with app.app_context():
        client = app.test_client()
        meal = {
            'id': 'thisiddoesnotexist',
            'name': 'some meal',
            'servings': 4,
            'description': 'some description'
        }
        r = client.put(
            ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + 'thisiddoesnotexist' + '/',
            data=json.dumps(meal),
            content_type=APPLICATION_JSON,
            method='put')
        assert r.status_code == 404
        assert_content_type(r)


def test_put_meal_400(app):
    with app.app_context():
        client = app.test_client()
        meal_id = 'oatmeal'
        m = Meal()
        m.id = meal_id
        m.name = "Oatmeal"
        m.servings = 4
        m.description = "Simple breakfast Oatmeal cooked in water"
        db.session.add(m)
        db.session.commit()

        name = 'new name'
        desc = 'new desc'
        meal = {
            'id': meal_id,
            'name': name,
            'servings': 4,
            'description': desc
        }

        r = client.put(
            ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + '/',
            data=json.dumps(meal),
            content_type=APPLICATION_JSON,
            method='put')
        assert r.status_code == 204

        for d in INVALID_MEAL_DATA:
            r = client.put(
                ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + '/',
                data=json.dumps(d),
                content_type=APPLICATION_JSON,
                method='put')
            assert r.status_code == 400
            assert_content_type(r)


def test_put_meal_415(app):
    with app.app_context():
        client = app.test_client()
        meal_id = 'oatmeal'
        m = Meal()
        m.id = meal_id
        m.name = "Oatmeal"
        m.servings = 4
        m.description = "Simple breakfast Oatmeal cooked in water"
        db.session.add(m)
        db.session.commit()

        name = 'new name'
        desc = 'new desc'
        meal = {
            'id': meal_id,
            'name': name,
            'servings': 4,
            'description': desc
        }
        invalid_content_type = 'text/plain'

        r = client.put(
            ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + '/',
            data=json.dumps(meal),
            content_type=invalid_content_type,
            method='put')
        assert r.status_code == 415
        assert_content_type(r)
        assert_control_profile_error(r)


def test_get_mealrecord_200(app):
    with app.app_context():
        # create meal for testing and put it into the db
        meal_id = "oatmeal"
        person_id = "123"
        timestamp = datetime.now()
        add_mealrecord_to_db(person_id, meal_id, timestamp)
        # obtain test client and make request
        client = app.test_client()
        r = client.get(ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION +
                       make_mealrecord_handle(person_id, meal_id, timestamp) + '/', method="GET")
        # assert correct response code and data
        assert r.status_code == 200
        assert_content_type(r)
        assert_self_url(r, ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION +
                        make_mealrecord_handle(person_id, meal_id, timestamp) + '/')
        assert_control_collection(r, ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION)
        assert_control(r, 'profile', URL_PROFILE)
        body = json.loads(r.data)
        assert body['person_id'] == person_id
        assert body['meal_id'] == meal_id
        assert body['timestamp'] == timestamp

        assert_namespace(r)
        assert_control_delete(r, ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION +
                              make_mealrecord_handle(person_id, meal_id, timestamp) + '/')
        assert_control(r, NS + ":meals-all", ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION)
        assert_edit_control_properties(r, NS + ":edit-meal")

