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


def add_portion_to_db(portion_id):
    p = Portion()
    p.id = portion_id
    p.name = "oat"
    p.calories = 120
    p.density = 0.4
    p.alcohol = 0.5
    p.carbohydrate = 24
    p.protein = 10
    p.fat = 1.5
    db.session.add(p)
    db.session.commit()

def add_mealrecord_to_db(person_id, meal_id, timestamp):
    m = MealRecord()
    m.person_id = person_id
    m.meal_id = meal_id
    m.timestamp = timestamp
    m.amount = 4
    db.session.add(m)
    db.session.commit()


# from Juha's course exercise content, just a bit modified END


def date_hook(json_dict):
    # for json to load date object
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        except:
            pass
    return json_dict

#
# Just print the name of the unit test in the beginning of the test
@pytest.fixture(scope='function', autouse=True)
def print_test_progress(request):
    print ("\n\n{}\n".format(request.node.nodeid.split("::")[1]))

VALID_PERSON = {'id': '123'}

VALID_MEAL = {
    'id': 'myoatmeal',
    'name': 'My Oatmeal',
    'servings': 3
}

VALID_PORTION = {
    'id': 'myoat',
    'name': 'My Oat',
    'calories': 352,
}

def create_person(app):
    client = app.test_client()
    return client.post(
        ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION,
        data=json.dumps(VALID_PERSON),
        content_type=APPLICATION_JSON,
        method="POST")

def get_person(app, person_id):
    client = app.test_client()
    return client.get(
        ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION + person_id + '/',
        method="GET")

def delete_person(app, person_id):
    client = app.test_client()
    return client.delete(
        ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION + person_id + '/',
        method="DELETE")

def create_meal(app):
    client = app.test_client()
    return client.post(
        ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION,
        data=json.dumps(VALID_MEAL),
        content_type=APPLICATION_JSON,
        method="POST")

def get_meal(app, meal_id):
    client = app.test_client()
    return client.get(
        ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + '/',
        method="GET")

def delete_meal(app, meal_id):
    client = app.test_client()
    return client.delete(
        ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + '/',
        method="DELETE")

def test_create_get_and_delete_person_plain(app):
    with app.app_context():
        print("Use-case: CREATE, GET, DELETE (Person)")
        id = VALID_PERSON['id']
        r = create_person(app)
        assert r.status_code == 201
        print("CREATE PERSON - OK")

        r = get_person(app, id)
        assert r.status_code == 200
        body = json.loads(r.data)
        assert body['id'] == id
        print("GET PERSON - OK")

        r = delete_person(app, id)
        assert r.status_code == 204
        print("DELETE PERSON - OK")


def test_create_meal_portion_and_delete(app):
    with app.app_context():
        print("Use-case: CREATE, DELETE (Meal)")
        id = VALID_MEAL['id']
        r = create_meal(app)
        assert r.status_code == 201
        print("CREATE MEAL - OK")

        r = get_meal(app, id)
        assert r.status_code == 200
        body = json.loads(r.data)
        assert body['id'] == id
        print("GET MEAL - OK")

        r = delete_meal(app, id)
        assert r.status_code == 204
        print("DELETE MEAL - OK")
