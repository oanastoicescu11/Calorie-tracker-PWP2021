import json

import pytest
from tapi import db, create_app
from tapi.constants import *
from tapi.models import Person
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


def test_post_person_400(app):
    with app.app_context():
        client = app.test_client()
        for d in INVALID_PERSON_DATA:
            r = client.post(
                ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION,
                data=json.dumps(d),
                content_type=APPLICATION_JSON,
                method='POST')
            if r.status_code == 201:
                print(d)
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
