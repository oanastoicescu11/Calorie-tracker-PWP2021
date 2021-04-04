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

def assert_control_collection(resp, expected_href):
    body = json.loads(resp.data)
    print(body)
    assert CONTROL_COLLECTION in body['@controls']
    assert body['@controls'][CONTROL_COLLECTION]['href'] == expected_href

def assert_namespace(resp):
    body = json.loads(resp.data)
    assert 'cameta' in body['@namespaces']

# from Juha's course exercise content, just a bit modified END

def test_person_collection(app):
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


def test_get_person(app):
    with app.app_context():
        # create person for testing and put it into the db
        person_id = "123"
        add_person_to_db(person_id)
        # obtain test client and make request
        client = app.test_client()
        print(ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION + person_id + '/')
        r = client.get(ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION + person_id + '/', method="GET")
        # assert correct response code and data
        assert r.status_code == 200
        assert_content_type(r)
        assert_control_collection(r, ROUTE_PERSON_COLLECTION)
        body = json.loads(r.data)
        print(body)
        assert body['id'] == person_id
        assert_namespace(r)
