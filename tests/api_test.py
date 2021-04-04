import json

import pytest
from tapi import db, create_app
from tapi.models import Person
# BEGIN Original fixture setup taken from the Exercise example and then modified further

import os
import tempfile
from sqlalchemy.engine import Engine
from sqlalchemy import event


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
def add_person_to_db(app, id):
    p = Person()
    p.id = id
    db.session.add(p)
    db.session.commit()

def test_person_collection(app):
    with app.app_context():
        add_person_to_db(app, "123")
        client = app.test_client()
        r = client.get("/api/persons/", method="GET")
        persons = json.loads(r.data)
        print(persons)
        assert r.status_code == 200
        assert persons[0]['id'] == "123"

def test_hello(app):
    with app.app_context():
        client = app.test_client()
        r = client.get("/api/hello/", method="GET")
        assert r.status_code == 200
