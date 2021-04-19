import json
import datetime
import pytest
from tapi import db, create_app
from tapi.constants import *
from tapi.models import Person, Meal, MealRecord, MealPortion, Portion
# BEGIN Original fixture setup taken from the Exercise example and then modified further
from tapi.utils import make_mealrecord_handle, myconverter, make_mealportion_handle

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
    body = json.loads(resp.data, object_hook=date_hook)
    assert 'cameta' in body['@namespaces']


def assert_control_profile_error(resp):
    body = json.loads(resp.data, object_hook=date_hook)
    assert body["@error"] is not None
    assert body['resource_url'] is not None
    assert_control(resp, 'profile', ERROR_PROFILE)


def assert_self_url(resp, href):
    assert_control(resp, "self", href)


def assert_control(resp, control, href):
    body = json.loads(resp.data)
    assert body['@controls'][control]['href'] == href


def assert_post_control_properties(resp, control):
    body = json.loads(resp.data, object_hook=date_hook)
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
    body = json.loads(resp.data, object_hook=date_hook)
    delete = NS + ":delete"
    assert_control(resp, delete, href)
    assert body['@controls'][delete]['method'] == "DELETE"


# from Juha's course exercise content, just a bit modified END


def date_hook(json_dict):
    # for json to load date object
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        except:
            pass
    return json_dict


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


def test_delete_meal_204(app):
    with app.app_context():
        client = app.test_client()
        r = client.post(
            ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION,
            data=json.dumps(VALID_MEAL),
            content_type=APPLICATION_JSON,
            method='POST')
        assert r.status_code == 201
        r = client.delete(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + VALID_MEAL['id'] + '/', method="DELETE")
        assert r.status_code == 204


def test_delete_meal_404(app):
    with app.app_context():
        client = app.test_client()
        meal_id = "imaginary-id-not-existing-in-the-db"
        r = client.delete(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + '/', method="DELETE")
        assert r.status_code == 404
        assert_content_type(r)
        assert_control_profile_error(r)

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


def test_post_meal_415_bad_response(app):
    with app.app_context():
        client = app.test_client()
        # Let's send an empty data for as JSON content, (BadResponse)
        data = None
        r = client.post(
            ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION,
            data=data,
            content_type=APPLICATION_JSON,
            method='POST')
        assert r.status_code == 415
        assert_content_type(r)
        assert_control_profile_error(r)


def test_post_meal_415_invalid_content_type(app):
    with app.app_context():
        client = app.test_client()
        # Let's send application/xml as content type
        r = client.post(
            ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION,
            data=json.dumps(VALID_MEAL),
            content_type="application/xml",
            method='POST')
        assert r.status_code == 415
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


def test_put_meal_415_bad_request(app):
    with app.app_context():
        client = app.test_client()
        # Let's put None as data
        r = client.put(
            ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + "123" + '/',
            data=None,
            content_type=APPLICATION_JSON,
            method='put')
        assert r.status_code == 415
        assert_content_type(r)
        assert_control_profile_error(r)


def test_put_meal_415_invalid_content_type(app):
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
        # Set content type to text/plain
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
        person_id = "123"
        add_person_to_db(person_id)

        meal_id = 'oatmeal'
        add_meal_to_db(meal_id)

        timestamp = datetime.datetime.now()
        add_mealrecord_to_db(person_id, meal_id, timestamp)
        # obtain test client and make request
        client = app.test_client()
        r = client.get(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + ROUTE_MEALRECORD_COLLECTION + 
                       make_mealrecord_handle(person_id, meal_id, timestamp) + '/', method="GET")
        # assert correct response code and data
        assert r.status_code == 200
        assert_content_type(r)
        assert_self_url(r, ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + ROUTE_MEALRECORD_COLLECTION + 
                        make_mealrecord_handle(person_id, meal_id, timestamp) + '/')
        assert_control_collection(r, ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION)
        assert_control(r, 'profile', URL_PROFILE)
        body = json.loads(r.data, object_hook=date_hook)
        assert body['person_id'] == person_id
        assert body['meal_id'] == meal_id
        assert body['timestamp'] == timestamp

        assert_namespace(r)
        assert_control_delete(r, ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + ROUTE_MEALRECORD_COLLECTION +
                              make_mealrecord_handle(person_id, meal_id, timestamp) + '/')
        assert_control(r, NS + ":mealrecords-all", ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION)
        assert_edit_control_properties(r, NS + ":edit-mealrecord")


def test_mealrecord_collection_200(app):
    with app.app_context():
        # create meal and person for testing and put it into the db
        person_id = "123"
        add_person_to_db(person_id)

        meal_id = 'oatmeal'
        add_meal_to_db(meal_id)

        timestamp = datetime.datetime.now()
        add_mealrecord_to_db(person_id, meal_id, timestamp)

        # obtain test client and make request
        client = app.test_client()
        r = client.get(ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION, method="GET")
        # assert correct response code and data
        assert r.status_code == 200
        assert_content_type(r)
        body = json.loads(r.data, object_hook=date_hook)
        assert body['items'][0]['meal_id'] == meal_id
        assert body['items'][0]['person_id'] == person_id
        assert body['items'][0]['timestamp'] == timestamp

        assert_namespace(r)
        assert_self_url(r, ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION)
        assert_control(r, NS + ":mealrecords-all", ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION)
        assert_control(r, NS + ":add-mealrecord", ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION)
        assert_post_control_properties(r, NS + ":add-mealrecord")


def test_post_mealrecord_415(app):
    with app.app_context():
        client = app.test_client()
        invalid_content_type = 'text/plain'
        r = client.post(
            ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION,
            data=json.dumps(VALID_PERSON),
            content_type=invalid_content_type,
            method='POST')
        assert r.status_code == 415
        assert_content_type(r)
        assert_control_profile_error(r)


INVALID_MEALRECORD_DATA = [
    {"person_id": "meal-id-missing", "timestamp": datetime.datetime.now()},
    {"meal_id": "person-id-missing", "timestamp": datetime.datetime.now()},
    {"meal_id": "timestamp-missing", "person_id": "my-person"},
    {}
]


def test_post_mealrecord_415_bad_response(app):
    with app.app_context():
        client = app.test_client()

        # Let's send an empty data for as JSON content, (BadResponse)
        data = None
        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION
        r = client.post(endpoint, data=data, content_type=APPLICATION_JSON, method="POST")

        assert r.status_code == 415
        assert_content_type(r)
        assert_control_profile_error(r)


def test_post_mealrecord_415_not_json(app):
    with app.app_context():
        client = app.test_client()

        # Let's send an empty data for as JSON content, (BadResponse)
        data = None
        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION
        r = client.post(endpoint, data=data, content_type="application/xml", method="POST")

        assert r.status_code == 415
        assert_content_type(r)
        assert_control_profile_error(r)


def test_post_mealrecord_400(app):
    with app.app_context():
        client = app.test_client()

        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION
        for d in INVALID_MEALRECORD_DATA:
            print(d)
            r = client.post(endpoint, data=json.dumps(d, default=myconverter), content_type=APPLICATION_JSON, method="POST")
            assert r.status_code == 400
            assert_content_type(r)
            assert_control_profile_error(r)


def test_get_mealrecord_404(app):
    with app.app_context():
        # create meal and person for testing and put it into the db
        person_id = "123"
        add_person_to_db(person_id)

        meal_id = 'oatmeal'
        add_meal_to_db(meal_id)
        # do not put mealrecord into db
        timestamp = datetime.datetime.now()

        # obtain test client and make request
        client = app.test_client()
        r = client.get(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + ROUTE_MEALRECORD_COLLECTION +
                       make_mealrecord_handle(person_id, meal_id, timestamp) + '/', method="GET")
        # assert correct response code and data
        assert r.status_code == 404
        assert_content_type(r)
        assert_control_profile_error(r)


def test_post_mealrecord_201(app):
    with app.app_context():
        client = app.test_client()
        # create meal and person for testing and put it into the db
        person_id = "123"
        add_person_to_db(person_id)

        meal_id = 'oatmeal'
        add_meal_to_db(meal_id)

        timestamp = datetime.datetime.now()

        MEALRECORD = {
            'meal_id': meal_id,
            'person_id': person_id,
            'amount': 3.5,
            'timestamp': timestamp
        }
        r = client.post(
            ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION,
            data=json.dumps(MEALRECORD, default=myconverter),
            content_type=APPLICATION_JSON,
            method='POST')
        assert r.status_code == 201
        # Location URL is absolute
        assert (r.headers['Location']).startswith("http://")
        assert (r.headers['Location']).endswith(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id +
                                                ROUTE_MEALRECORD_COLLECTION +
                                                make_mealrecord_handle(MEALRECORD['person_id'],
                                                                       MEALRECORD['meal_id'],
                                                                       MEALRECORD['timestamp']) + '/')


def test_delete_mealrecord_204(app):
    with app.app_context():
        # create mealrecord for testing and put it into the db

        person_id = "123"
        add_person_to_db(person_id)

        meal_id = 'oatmeal'
        add_meal_to_db(meal_id)

        timestamp = datetime.datetime.now()
        add_mealrecord_to_db(person_id, meal_id, timestamp)

        client = app.test_client()
        # create meal and person for testing and put it into the db

        r = client.delete(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + ROUTE_MEALRECORD_COLLECTION +
                          make_mealrecord_handle(person_id, meal_id, timestamp) + '/',
                          method="DELETE")

        assert r.status_code == 204
        mr = MealRecord.query.filter(MealRecord.meal_id == meal_id, MealRecord.person_id == person_id).first()
        assert mr is None


def test_deleted_mealrecord_404(app):
    with app.app_context():
        # create mealrecord for testing and put it into the db

        person_id = "123"
        add_person_to_db(person_id)

        meal_id = 'oatmeal'
        add_meal_to_db(meal_id)

        timestamp = datetime.datetime.now()
        add_mealrecord_to_db(person_id, meal_id, timestamp)

        client = app.test_client()
        # create meal and person for testing and put it into the db

        r = client.delete(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + ROUTE_MEALRECORD_COLLECTION +
                          make_mealrecord_handle(person_id, meal_id, timestamp) + '/',
                          method="DELETE")

        assert r.status_code == 204

        r = client.delete(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + ROUTE_MEALRECORD_COLLECTION +
                          make_mealrecord_handle(person_id, meal_id, timestamp) + '/',
                          method="DELETE")
        assert r.status_code == 404


def test_put_mealrecord_415(app):
    with app.app_context():
        # create meal for testing and put it into the db

        person_id = "123"
        add_person_to_db(person_id)

        meal_id = 'oatmeal'
        add_meal_to_db(meal_id)

        timestamp = datetime.datetime.now()
        add_mealrecord_to_db(person_id, meal_id, timestamp)
        client = app.test_client()

        MEALRECORD = {
            'meal_id': meal_id,
            'person_id': person_id,
            'amount': 3.5,
            'timestamp': timestamp
        }

        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + ROUTE_MEALRECORD_COLLECTION + \
                   make_mealrecord_handle(person_id, meal_id, timestamp) + '/'

        r = client.put(endpoint, data=json.dumps(MEALRECORD, default=myconverter), content_type=APPLICATION_JSON, method="PUT")
        # assert correct response code and data
        assert r.status_code == 204
        mr = MealRecord.query.filter(
            MealRecord.person_id == person_id,
            MealRecord.meal_id == meal_id,
            MealRecord.timestamp == timestamp
        ).first()
        assert mr is not None
        assert mr.amount == 3.5


def test_put_mealrecord_415_not_json(app):
    with app.app_context():
        client = app.test_client()
        mid = 'imaginary-meal-which-does-not-exist-in-the-db'
        pid = 'imaginary-person-which-does-not-exist-in-the-db'
        timestamp = datetime.datetime.now()

        # Let's send an empty data for as JSON content, (BadResponse)
        data = None
        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + ROUTE_MEALRECORD_COLLECTION + \
                   make_mealrecord_handle(pid, mid, timestamp) + '/'

        r = client.put(endpoint, data=data, content_type=APPLICATION_JSON, method="PUT")

        assert r.status_code == 415
        assert_content_type(r)
        assert_control_profile_error(r)


def test_put_mealrecord_415_wrong_content_type(app):
    with app.app_context():
        client = app.test_client()
        mid = 'imaginary-meal-which-does-not-exist-in-the-db'
        pid = 'imaginary-person-which-does-not-exist-in-the-db'
        timestamp = datetime.datetime.now()

        data = None
        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + ROUTE_MEALRECORD_COLLECTION + \
                   make_mealrecord_handle(pid, mid, timestamp) + '/'
        # Let's send application/xml
        r = client.put(endpoint, data=None, content_type="application/xml", method="PUT")

        assert r.status_code == 415
        assert_content_type(r)
        assert_control_profile_error(r)


def test_put_mealrecord_400(app):
    with app.app_context():
        client = app.test_client()
        mid = 'imaginary-meal-which-does-not-exist-in-the-db'
        pid = 'imaginary-person-which-does-not-exist-in-the-db'
        timestamp = datetime.datetime.now()

        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + ROUTE_MEALRECORD_COLLECTION +\
                   make_mealrecord_handle(pid, mid, timestamp) + '/'

        for d in INVALID_MEALRECORD_DATA:
            r = client.put(endpoint, data=json.dumps(d, default=myconverter), content_type=APPLICATION_JSON, method="PUT")
            assert r.status_code == 400
            assert_content_type(r)
            assert_control_profile_error(r)


def test_put_mealrecord_204(app):
    with app.app_context():
        # create meal for testing and put it into the db

        person_id = "123"
        add_person_to_db(person_id)

        meal_id = 'oatmeal'
        add_meal_to_db(meal_id)

        timestamp = datetime.datetime.now()
        add_mealrecord_to_db(person_id, meal_id, timestamp)
        client = app.test_client()

        MEALRECORD = {
            'meal_id': meal_id,
            'person_id': person_id,
            'amount': 3.5,
            'timestamp': timestamp
        }

        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + ROUTE_MEALRECORD_COLLECTION +\
                   make_mealrecord_handle(person_id, meal_id, timestamp) + '/'
        print(endpoint)
        r = client.put(endpoint, data=json.dumps(MEALRECORD, default=myconverter), content_type=APPLICATION_JSON, method="PUT")

        assert r.status_code == 204


def test_put_mealrecord_404(app):
    with app.app_context():
        # create meal for testing and put it into the db
        mid = 'imaginary-meal-which-does-not-exist-in-the-db'
        pid = 'imaginary-person-which-does-not-exist-in-the-db'
        timestamp = datetime.datetime.now()

        client = app.test_client()

        MEALRECORD = {
            'meal_id': mid,
            'person_id': pid,
            'amount': 3.5,
            'timestamp': timestamp
        }
        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + ROUTE_MEALRECORD_COLLECTION +\
                   make_mealrecord_handle(pid, mid, timestamp) + '/'
        r = client.put(endpoint, data=json.dumps(MEALRECORD, default=myconverter), content_type=APPLICATION_JSON, method="PUT")
        # Olive oil soup is total of 2.5 servings and has 10g of oil per serving

        assert r.status_code == 404
        assert_content_type(r)
        assert_control_profile_error(r)


def test_post_mealportion_201(app):
    with app.app_context():
        # create meal for testing and put it into the db

        pid = "olive-oil"
        name = "Olive oil"
        density = 0.89
        fat = 100
        calories = 720

        portion = Portion()
        portion.id = pid
        portion.calories = calories
        portion.name = name
        portion.density = density
        portion.fat = fat

        db.session.add(portion)
        db.session.commit()

        soup = Meal()
        mid = "olive-oil-soup"
        soup.id = mid
        soup.name = "Olive oil Soup"
        soup.servings = 2.5

        db.session.add(soup)
        db.session.commit()

        client = app.test_client()

        MEALPORTION = {
            'meal_id': mid,
            'portion_id': pid,
            'weight_per_serving': 10,
        }
        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/"
        print(endpoint)
        r = client.post(endpoint, data=json.dumps(MEALPORTION), content_type=APPLICATION_JSON, method="POST")
        # Olive oil soup is total of 2.5 servings and has 10g of oil per serving

        assert r.status_code == 201
        # Location URL is absolute
        assert r.headers['Location'].startswith("http://")
        assert r.headers['Location'].endswith(
            ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/" +
            make_mealportion_handle(MEALPORTION['meal_id'], MEALPORTION['portion_id']) + '/')


def test_post_mealportion_415_bad_response(app):
    with app.app_context():
        client = app.test_client()
        mid = 'imaginary-meal-which-does-not-exist-in-the-db'

        # Let's send an empty data for as JSON content, (BadResponse)
        data = None
        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/"
        r = client.post(endpoint, data=data, content_type=APPLICATION_JSON, method="POST")

        assert r.status_code == 415
        assert_content_type(r)
        assert_control_profile_error(r)


def test_post_mealportion_415_not_json(app):
    with app.app_context():
        client = app.test_client()
        mid = 'imaginary-meal-which-does-not-exist-in-the-db'

        # Let's send an empty data for as JSON content, (BadResponse)
        data = None
        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/"
        r = client.post(endpoint, data=data, content_type="application/xml", method="POST")

        assert r.status_code == 415
        assert_content_type(r)
        assert_control_profile_error(r)


INVALID_MEALPORTION_DATA = [
    {"portion_id": "meal-id-missing", "weight_per_serving": 20},
    {"meal_id": "portion-id-missing", "weight_per_serving": 20},
    {"meal_id": "weight-per-serving-missing", "portion_id": "my-portion"},
    {}
]


def test_post_mealportion_400(app):
    with app.app_context():
        client = app.test_client()
        mid = 'imaginary-meal-which-does-not-exist-in-the-db'

        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/"
        for d in INVALID_MEALPORTION_DATA:
            print(d)
            r = client.post(endpoint, data=json.dumps(d), content_type=APPLICATION_JSON, method="POST")
            assert r.status_code == 400
            assert_content_type(r)
            assert_control_profile_error(r)


def test_post_mealportion_409(app):
    with app.app_context():
        # create meal for testing and put it into the db

        pid = "olive-oil"
        name = "Olive oil"
        density = 0.89
        fat = 100
        calories = 720

        portion = Portion()
        portion.id = pid
        portion.calories = calories
        portion.name = name
        portion.density = density
        portion.fat = fat

        db.session.add(portion)
        db.session.commit()

        soup = Meal()
        mid = "olive-oil-soup"
        soup.id = mid
        soup.name = "Olive oil Soup"
        soup.servings = 2.5

        # db.session.add(soup)
        # db.session.commit()

        client = app.test_client()

        MEALPORTION = {
            'meal_id': mid,
            'portion_id': pid,
            'weight_per_serving': 10,
        }
        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/"
        print(endpoint)

        # Meal not in the DB yet
        r = client.post(endpoint, data=json.dumps(MEALPORTION), content_type=APPLICATION_JSON, method="POST")

        assert r.status_code == 409
        assert_content_type(r)
        assert_control_profile_error(r)

        # Add the Meal into the db and delete the Portion
        db.session.add(soup)
        db.session.commit()
        db.session.delete(portion)

        r = client.post(endpoint, data=json.dumps(MEALPORTION), content_type=APPLICATION_JSON, method="POST")

        assert r.status_code == 409
        assert_content_type(r)
        assert_control_profile_error(r)


def test_get_mealportion_200(app):
    with app.app_context():
        # create meal for testing and put it into the db

        pid = "olive-oil"
        name = "Olive oil"
        density = 0.89
        fat = 100
        calories = 720

        portion = Portion()
        portion.id = pid
        portion.calories = calories
        portion.name = name
        portion.density = density
        portion.fat = fat

        db.session.add(portion)
        db.session.commit()

        soup = Meal()
        mid = "olive-oil-soup"
        soup.id = mid
        soup.name = "Olive oil Soup"
        soup.servings = 2.5

        db.session.add(soup)
        db.session.commit()

        # Olive oil soup is total of 2.5 servings and has 10g of oil per serving
        mp = MealPortion(meal_id=mid, portion_id=pid, weight_per_serving=10)

        db.session.add(mp)
        db.session.commit()

        client = app.test_client()
        # create meal and person for testing and put it into the db

        r = client.get(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/" +
                       make_mealportion_handle(mid, pid) + '/', method="GET")
        # assert correct response code and data
        assert r.status_code == 200
        assert_content_type(r)
        assert_self_url(r, ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/" +
                        make_mealportion_handle(mid, pid) + '/')
        assert_control_collection(r, ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/")
        assert_control(r, 'profile', URL_PROFILE)
        body = json.loads(r.data, object_hook=date_hook)
        assert body['meal_id'] == mid
        assert body['portion_id'] == pid
        assert body['weight_per_serving'] == 10
        assert_namespace(r)
        assert_control_delete(r, ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/" +
                              make_mealportion_handle(mid, pid) + '/')
        # assert_control(r, NS + ":mealrecords-all", ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION)
        assert_edit_control_properties(r, NS + ":edit-mealportion")


def test_get_mealportion_404(app):
    with app.app_context():
        # create meal for testing and put it into the db

        mid = 'imaginary-meal-which-does-not-exist-in-the-db'
        pid = 'imaginary-portion-which-does-not-exist-in-the-db'
        client = app.test_client()
        # create meal and person for testing and put it into the db

        r = client.get(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/" +
                       make_mealportion_handle(mid, pid) + '/', method="GET")
        # assert correct response code and data
        # assert correct response code and data
        assert r.status_code == 404
        assert_content_type(r)
        assert_control_profile_error(r)


def test_delete_mealportion_204(app):
    with app.app_context():
        # create meal for testing and put it into the db

        pid = "olive-oil"
        name = "Olive oil"
        density = 0.89
        fat = 100
        calories = 720

        portion = Portion()
        portion.id = pid
        portion.calories = calories
        portion.name = name
        portion.density = density
        portion.fat = fat

        db.session.add(portion)
        db.session.commit()

        soup = Meal()
        mid = "olive-oil-soup"
        soup.id = mid
        soup.name = "Olive oil Soup"
        soup.servings = 2.5

        db.session.add(soup)
        db.session.commit()

        # Olive oil soup is total of 2.5 servings and has 10g of oil per serving
        mp = MealPortion(meal_id=mid, portion_id=pid, weight_per_serving=10)

        db.session.add(mp)
        db.session.commit()

        client = app.test_client()
        # create meal and person for testing and put it into the db

        r = client.delete(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/" +
                          make_mealportion_handle(mid, pid) + '/', method="DELETE")

        assert r.status_code == 204
        mp = MealPortion.query.filter(MealPortion.meal_id == mid, MealPortion.portion_id == pid).first()
        assert mp is None


def test_deleted_mealportion_404(app):
    with app.app_context():
        # create meal for testing and put it into the db

        pid = "olive-oil"
        name = "Olive oil"
        density = 0.89
        fat = 100
        calories = 720

        portion = Portion()
        portion.id = pid
        portion.calories = calories
        portion.name = name
        portion.density = density
        portion.fat = fat

        db.session.add(portion)
        db.session.commit()

        soup = Meal()
        mid = "olive-oil-soup"
        soup.id = mid
        soup.name = "Olive oil Soup"
        soup.servings = 2.5

        db.session.add(soup)
        db.session.commit()

        # Olive oil soup is total of 2.5 servings and has 10g of oil per serving
        mp = MealPortion(meal_id=mid, portion_id=pid, weight_per_serving=10)

        db.session.add(mp)
        db.session.commit()

        client = app.test_client()
        # create meal and person for testing and put it into the db

        r = client.delete(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/" +
                          make_mealportion_handle(mid, pid) + '/', method="DELETE")

        assert r.status_code == 204

        r = client.delete(ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/" +
                          make_mealportion_handle(mid, pid) + '/', method="DELETE")
        assert r.status_code == 404


def test_put_mealportion_415(app):
    with app.app_context():
        # create meal for testing and put it into the db

        pid = "olive-oil"
        name = "Olive oil"
        density = 0.89
        fat = 100
        calories = 720

        portion = Portion()
        portion.id = pid
        portion.calories = calories
        portion.name = name
        portion.density = density
        portion.fat = fat

        db.session.add(portion)
        db.session.commit()

        soup = Meal()
        mid = "olive-oil-soup"
        soup.id = mid
        soup.name = "Olive oil Soup"
        soup.servings = 2.5

        db.session.add(soup)
        db.session.commit()

        # Olive oil soup is total of 2.5 servings and has 10g of oil per serving
        mp = MealPortion(meal_id=mid, portion_id=pid, weight_per_serving=10)

        db.session.add(mp)
        db.session.commit()

        client = app.test_client()
        # create meal and person for testing and put it into the db
        MEALPORTION = {
            'meal_id': mid,
            'portion_id': pid,
            'weight_per_serving': 25,
        }
        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/" \
                   + make_mealportion_handle(mid, pid) + '/'

        r = client.put(endpoint, data=json.dumps(MEALPORTION), content_type=APPLICATION_JSON, method="PUT")
        # assert correct response code and data
        assert r.status_code == 204
        mp = MealPortion.query.filter(
            MealPortion.meal_id == mid,
            MealPortion.portion_id == pid
        ).first()
        assert mp is not None
        assert mp.weight_per_serving == 25


def test_put_mealportion_415_not_json(app):
    with app.app_context():
        client = app.test_client()
        mid = 'imaginary-meal-which-does-not-exist-in-the-db'
        pid = 'imaginary-portion-which-does-not-exist-in-the-db'

        # Let's send an empty data for as JSON content, (BadResponse)
        data = None
        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/" \
                   + make_mealportion_handle(mid, pid) + '/'

        r = client.put(endpoint, data=data, content_type=APPLICATION_JSON, method="PUT")

        assert r.status_code == 415
        assert_content_type(r)
        assert_control_profile_error(r)


def test_put_mealportion_415_wrong_content_type(app):
    with app.app_context():
        client = app.test_client()
        mid = 'imaginary-meal-which-does-not-exist-in-the-db'
        pid = 'imaginary-portion-which-does-not-exist-in-the-db'

        data = None
        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/" \
                   + make_mealportion_handle(mid, pid) + '/'

        # Let's send application/xml
        r = client.put(endpoint, data=None, content_type="application/xml", method="PUT")

        assert r.status_code == 415
        assert_content_type(r)
        assert_control_profile_error(r)


def test_put_mealportion_400(app):
    with app.app_context():
        client = app.test_client()
        mid = 'imaginary-meal-which-does-not-exist-in-the-db'
        pid = 'imaginary-portion-which-does-not-exist-in-the-db'

        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/" \
                   + make_mealportion_handle(mid, pid) + '/'

        for d in INVALID_MEALPORTION_DATA:
            r = client.put(endpoint, data=json.dumps(d), content_type=APPLICATION_JSON, method="PUT")
            assert r.status_code == 400
            assert_content_type(r)
            assert_control_profile_error(r)


def test_put_mealportion_204(app):
    with app.app_context():
        # create meal for testing and put it into the db

        pid = "olive-oil"
        name = "Olive oil"
        density = 0.89
        fat = 100
        calories = 720

        portion = Portion()
        portion.id = pid
        portion.calories = calories
        portion.name = name
        portion.density = density
        portion.fat = fat

        db.session.add(portion)
        db.session.commit()

        soup = Meal()
        mid = "olive-oil-soup"
        soup.id = mid
        soup.name = "Olive oil Soup"
        soup.servings = 2.5

        db.session.add(soup)
        db.session.commit()

        mp = MealPortion(
            meal_id=mid,
            portion_id=pid,
            weight_per_serving=40
        )
        db.session.add(mp)
        db.session.commit()

        client = app.test_client()

        MEALPORTION = {
            'meal_id': mid,
            'portion_id': pid,
            'weight_per_serving': 10,
        }
        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/" + make_mealportion_handle(mid,
                                                                                                               pid) + '/'
        print(endpoint)
        r = client.put(endpoint, data=json.dumps(MEALPORTION), content_type=APPLICATION_JSON, method="PUT")
        # Olive oil soup is total of 2.5 servings and has 10g of oil per serving

        assert r.status_code == 204


def test_put_mealportion_404(app):
    with app.app_context():
        # create meal for testing and put it into the db
        mid = 'imaginary-meal-which-does-not-exist-in-the-db'
        pid = 'imaginary-portion-which-does-not-exist-in-the-db'
        client = app.test_client()

        MEALPORTION = {
            'meal_id': mid,
            'portion_id': pid,
            'weight_per_serving': 10,
        }
        endpoint = ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mid + "/mealportions/" + make_mealportion_handle(mid,
                                                                                                               pid) + '/'
        r = client.put(endpoint, data=json.dumps(MEALPORTION), content_type=APPLICATION_JSON, method="PUT")
        # Olive oil soup is total of 2.5 servings and has 10g of oil per serving

        assert r.status_code == 404
        assert_content_type(r)
        assert_control_profile_error(r)
