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


def add_portion_to_db(portion_id, cal, c=0, p=0, f=0, a=0, density=1):
    portion = Portion()
    portion.id = portion_id
    portion.name = portion_id
    portion.calories = cal
    portion.density = density
    portion.alcohol = a
    portion.carbohydrate = c
    portion.protein = p
    portion.fat = f
    db.session.add(portion)
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

def get_portion(app, portion_id):
    client = app.test_client()
    r = client.get(
        ROUTE_ENTRYPOINT + ROUTE_PORTION_COLLECTION + portion_id + '/',
        method="GET")
    assert r.status_code == 200
    return json.loads(r.data)

def delete_meal(app, meal_id):
    client = app.test_client()
    return client.delete(
        ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + meal_id + '/',
        method="DELETE")

def create_portions(app):
    add_portion_to_db("oat", cal=130, p=4, c=33, f=1)
    add_portion_to_db("bread", cal=200, c=40, p=8, f=2)
    add_portion_to_db("milk", cal=40, c=4, p=4, f=2)
    add_portion_to_db("ham", cal=330, p=30, c=0, f=15)
    add_portion_to_db("beer", cal=100, c=4, a=4.7)

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

def create_basic_meal(app, meal_id):
    m = {'id': meal_id, 'name': meal_id, 'servings': 1}
    client = app.test_client()
    r = client.post(
        ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION,
        data=json.dumps(m),
        content_type=APPLICATION_JSON,
        method="POST")
    assert r.status_code == 201
    r = client.get(r.headers['Location'])
    assert r.status_code == 200
    return json.loads(r.data)

def get_mealjson(app, meal_id):
    r = get_meal(app, meal_id)
    assert r.status_code == 200
    return json.loads(r.data)

def create_meal_portion(app, mp):
    client = app.test_client()
    r = client.post(
        ROUTE_ENTRYPOINT + ROUTE_MEAL_COLLECTION + mp['meal_id'] + '/mealportions/',
        data=json.dumps(mp),
        content_type=APPLICATION_JSON,
        method="POST")
    assert r.status_code == 201
    r = client.get(r.headers['Location'])
    assert r.status_code == 200
    return json.loads(r.data)

def add_portion_to_meal(app, meal, portion, amount):
    mp = {'meal_id': meal['id'], 'portion_id': portion['id'], 'weight_per_serving': amount}
    create_meal_portion(app, mp)

def create_mealrecord(app, meal, time, servings, date='2021-04-21'):
    client = app.test_client()
    h = time.split(':')[0]
    m = time.split(':')[1]

    d = {'meal_id': meal['id'], 'timestamp': date + " " + time + ':0.0', 'person_id': VALID_PERSON['id'], 'amount': servings}
    r = client.post(
        ROUTE_ENTRYPOINT + ROUTE_MEALRECORD_COLLECTION,
        data=json.dumps(d),
        content_type=APPLICATION_JSON,
        method="POST"
    )
    assert r.status_code == 201

def get_meals_for_day(app, day='2021-04-21'):
    client = app.test_client()
    r = client.get(
        ROUTE_ENTRYPOINT + ROUTE_PERSON_COLLECTION + VALID_PERSON['id'] + '/mealrecords/'
    )
    assert r.status_code == 200
    return json.loads(r.data)

def test_track_meals_of_the_day_and_count_calories(app):
    """ As a working from home -person, I want to record my meals to know my calorie intake
    and meal times to get the best energy possible for my day """
    with app.app_context():
        create_person(app)
        create_portions(app)

        print()
        breakfast = create_basic_meal(app, "breakfast")
        add_portion_to_meal(app, breakfast, get_portion(app, "oat"), 80)
        add_portion_to_meal(app, breakfast, get_portion(app, "milk"), 200)

        lunch = create_basic_meal(app, "soap")
        add_portion_to_meal(app, lunch, get_portion(app, "bread"), 90)
        add_portion_to_meal(app, lunch, get_portion(app, "ham"), 100)
        add_portion_to_meal(app, lunch, get_portion(app, "milk"), 200)

        dinner = create_basic_meal(app, "dinner")
        add_portion_to_meal(app, dinner, get_portion(app, "bread"), 90)
        add_portion_to_meal(app, dinner, get_portion(app, "ham"), 100)
        add_portion_to_meal(app, dinner, get_portion(app, "beer"), 660)

        create_mealrecord(app, breakfast, "10:00", servings=2)
        create_mealrecord(app, lunch, "14:00", servings=1)
        create_mealrecord(app, dinner, "20:00", servings=2)

        meals_data = get_meals_for_day(app)

        meals = []
        for m in meals_data['items']:
            meals.append([m['timestamp'], m['meal_id'], m['amount'], 0])
        assert len(meals) == 3
        for m in meals:
            for p in get_mealjson(app, m[1]):
                print (p)
                # TODO: HOW do we get the MealPortions for calculating totals?
                #['items']:
                pass


def test_track_breakfast_and_count_carbohydrates(app):
    """ As a hobbyist runner, I want to record my breakfast and track the amount of carbohydrates consumed. """
    pass

def test_track_alcohol_for_a_month(app):
    """ As a semi professional athlete, I have my daily diet in shape already, but I want to track the amount
    of my alcohol consumption in daily basis to detect if it has any effect to my performance."""
    pass