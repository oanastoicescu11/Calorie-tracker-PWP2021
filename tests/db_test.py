import datetime

import pytest
from sqlalchemy.exc import IntegrityError, StatementError

from tapi import db, create_app
from tapi.models import Person, Activity, Meal, MealRecord, ActivityRecord


# BEGIN Original fixture setup taken from the Exercise example and then modified further

import os
import tempfile
from sqlalchemy.engine import Engine
from sqlalchemy import event, and_

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


# 'Retrieve an existing instance of the model (recommended trying with different filter options)
# 'Update an existing model instance (if update operation is supported by this model)
# 'Remove an existing model from the database
def test_person_combo(app):
    with app.app_context():
        # create original person (id=677) and commit to db
        pid = "677"
        p_original = Person(id=pid)
        db.session.add(p_original)
        db.session.commit()
        # fetch the original person from the DB as 'fetched'
        fetched = Person.query.filter(Person.id == pid).first()
        assert(fetched.id == pid)
        # change the fetched ID and commit to the DB, primary key still unique
        new_id = "677-modified"
        fetched.id = new_id
        db.session.add(fetched)
        db.session.commit()
        # delete the entity
        db.session.delete(fetched)
        db.session.commit()
        deleted = Person.query.filter(Person.id == new_id).first()
        assert(deleted is None)


# TODO: check this part
# 'Test that onModify and onDelete work as expected

def test_person_unique(app):
    with app.app_context():
        same_id = "414"
        p1 = Person(id=same_id)
        p2 = Person(id=same_id)
        db.session.add(p1)
        db.session.add(p2)
        with pytest.raises(IntegrityError):
            db.session.commit()


# 'Create a new instance of the model
def test_person_creation(app):
    with app.app_context():
        person = Person()
        person.id = "123"
        db.session.add(person)
        db.session.commit()


# 'Test possible errors conditions (e.g. foreign keys violation or other situation
# where Integrity error might be raised)

# Suppress warnings: Person without ID throws IntegrityError,
# but even caught triggers warning in pytest.
@pytest.mark.filterwarnings("ignore")
def test_person_id_required(app):
    with app.app_context():
        person = Person()
        db.session.add(person)
        with pytest.raises(IntegrityError):
            db.session.commit()


# 'Create a new instance of the model
def test_activity_creation(app):
    with app.app_context():
        activity = Activity(id="123", name="Running", intensity=600)
        db.session.add(activity)
        db.session.commit()
        # And with optional fields
        a = Activity()
        a = Activity(id="345", name="Running-hard", intensity=800)
        a.description = "A harder exercise containing a continuous high heart beat running training"
        db.session.add(a)
        db.session.commit()

        db.session.delete(activity)
        db.session.delete(a)
        db.session.commit()


def test_activity_unique(app):
    with app.app_context():
        same_id = "123456"
        a1 = Activity(id=same_id, name="Running", intensity=600)
        a2 = Activity(id=same_id, name="Running-hard", intensity=800)

        db.session.add(a1)
        db.session.add(a2)
        with pytest.raises(IntegrityError):
            db.session.commit()


def test_activity_record_creation(app):
    with app.app_context():
        running = Activity()
        running.id = "1234"
        running.name = "Running"
        running.intensity = 600  # 600kcal per hour
        db.session.add(running)
        db.session.commit()

        runner = Person()
        runner.id = '4566'
        db.session.add(runner)
        db.session.commit()

        ac = ActivityRecord()
        ac.activity = running
        ac.person = runner
        ac.duration = 3600
        ac.timestamp = datetime.datetime.now()

        db.session.add(ac)
        db.session.commit()

        fetched = ActivityRecord.query.filter(ActivityRecord.person_id == runner.id).first()
        assert(fetched.activity == running)

        # extensive cleanup, will work even when cascade might be broken
        db.session.delete(ac)
        db.session.delete(running)
        db.session.delete(runner)


def test_activity_record_creation_many(app):
    with app.app_context():
        # make sure we can have many records for one person
        # and many records for one activity
        p1 = Person(id="333")
        p2 = Person(id="444")
        a1 = Activity(id="123", name="act1", intensity=200)
        a2 = Activity(id="456", name="act2", intensity=200)

        entities = [p1, p2, a1, a2]

        p1a1 = ActivityRecord()
        p1a1.person = p1
        p1a1.activity = a1
        p1a1.duration = 100
        p1a1.timestamp = datetime.datetime.now()
        entities.append(p1a1)

        p1a2 = ActivityRecord()
        p1a2.person = p1
        p1a2.activity = a2
        p1a2.duration = 100
        p1a2.timestamp = datetime.datetime.now()
        entities.append(p1a2)

        p2a1 = ActivityRecord()
        p2a1.person = p2
        p2a1.activity = a1
        p2a1.duration = 100
        p2a1.timestamp = datetime.datetime.now()
        entities.append(p2a1)

        p2a2 = ActivityRecord()
        p2a2.person = p2
        p2a2.activity = a2
        p2a2.duration = 100
        p2a2.timestamp = datetime.datetime.now()
        entities.append(p2a2)

        for i in entities:
            db.session.add(i)
        db.session.commit()

        fetched = ActivityRecord.query.filter(and_(Person.id == p1.id, Activity.id == a1.id)).first()
        assert (fetched is not None)
        db.session.delete(fetched)
        fetched = ActivityRecord.query.filter(and_(Person.id == p1.id, Activity.id == a2.id)).first()
        assert (fetched is not None)
        db.session.delete(fetched)
        fetched = ActivityRecord.query.filter(and_(Person.id == p2.id, Activity.id == a1.id)).first()
        assert (fetched is not None)
        db.session.delete(fetched)
        fetched = ActivityRecord.query.filter(and_(Person.id == p2.id, Activity.id == a2.id)).first()
        assert (fetched is not None)
        db.session.delete(fetched)

        db.session.delete(p1)
        db.session.delete(p1)
        db.session.delete(a1)
        db.session.delete(a2)


def test_activity_record_cascade_on_person(app):
    with app.app_context():
        running = Activity()
        running.id = "1234"
        running.name = "Running"
        running.intensity = 600  # 600kcal per hour
        db.session.add(running)
        db.session.commit()

        runner = Person()
        runner.id = '4566'
        db.session.add(runner)
        db.session.commit()

        ac = ActivityRecord()
        ac.activity = running
        ac.person = runner
        ac.duration = 3600
        ac.timestamp = datetime.datetime.now()

        db.session.add(ac)
        db.session.commit()

        db.session.delete(runner)
        db.session.commit()
        fetched = ActivityRecord.query.filter(ActivityRecord.person_id == runner.id).first()
        assert (fetched is None)


def test_activity_record_cascade_on_activity(app):
    with app.app_context():
        running = Activity()
        running.id = "1234"
        running.name = "Running"
        running.intensity = 600  # 600kcal per hour
        db.session.add(running)
        db.session.commit()

        runner = Person()
        runner.id = '4566'
        db.session.add(runner)
        db.session.commit()

        ac = ActivityRecord()
        ac.activity = running
        ac.person = runner
        ac.duration = 3600
        ac.timestamp = datetime.datetime.now()

        db.session.add(ac)
        db.session.commit()

        db.session.delete(running)
        db.session.commit()
        fetched = ActivityRecord.query.filter(ActivityRecord.activity_id == running.id).first()
        assert (fetched is None)


# delete on object previously deleted throws warning
# for simplicity reasons, all entities are purged at the end
@pytest.mark.filterwarnings("ignore")
def test_activity_record_cascade_many(app):
    with app.app_context():
        # make sure we can have many records for one person
        # and many records for one activity
        p1 = Person(id="333")
        p2 = Person(id="444")
        a1 = Activity(id="123", name="act1", intensity=200)
        a2 = Activity(id="456", name="act2", intensity=200)

        entities = [p1, p2, a1, a2]

        p1a1 = ActivityRecord()
        p1a1.person = p1
        p1a1.activity = a1
        p1a1.duration = 100
        p1a1.timestamp = datetime.datetime.now()
        entities.append(p1a1)

        p1a2 = ActivityRecord()
        p1a2.person = p1
        p1a2.activity = a2
        p1a2.duration = 100
        p1a2.timestamp = datetime.datetime.now()
        entities.append(p1a2)

        p2a1 = ActivityRecord()
        p2a1.person = p2
        p2a1.activity = a1
        p2a1.duration = 100
        p2a1.timestamp = datetime.datetime.now()
        entities.append(p2a1)

        p2a2 = ActivityRecord()
        p2a2.person = p2
        p2a2.activity = a2
        p2a2.duration = 100
        p2a2.timestamp = datetime.datetime.now()
        entities.append(p2a2)

        for i in entities:
            db.session.add(i)
        db.session.commit()
        db.session.delete(p1)
        db.session.delete(a1)
        db.session.commit()
        fetched = ActivityRecord.query.filter(Person.id == p1.id).first()
        assert (fetched is None)
        fetched = ActivityRecord.query.filter(Activity.id == a1.id).first()
        assert (fetched is None)
        fetched = ActivityRecord.query.filter(Person.id == p2.id).first()
        assert (fetched is not None)
        fetched = ActivityRecord.query.filter(Activity.id == a2.id).first()
        assert (fetched is not None)

        for i in entities:
            db.session.delete(i)
        db.session.commit()


# 'Create a new instance of the model
def test_meal_creation(app):
    with app.app_context():
        meal = Meal()
        meal.id = "123"
        meal.name = "Soup"
        meal.servings = 2  # 2 servings
        db.session.add(meal)
        db.session.commit()
        # And with optional fields
        a = Meal()
        a.id = "127"
        a.name = "Oatmeal"
        a.servings = 3  # 3 servings
        a.description = "Juha's morning oatmeal that he eats every morning"
        db.session.add(a)
        db.session.commit()

        db.session.delete(meal)
        db.session.delete(a)
        db.session.commit()


def test_meal_unique(app):
    with app.app_context():
        same_id = "414"
        print("hello")
        meal = Meal()
        meal.id = "123"
        meal.name = "Oatmeal"
        meal.servings = 1

        m1 = Meal(id=same_id)
        m2 = Meal(id=same_id)
        db.session.add(m1, m2)
        with pytest.raises(IntegrityError):
            db.session.commit()


def test_meal_record_creation(app):
    with app.app_context():
        soup = Meal()
        soup.id = "1234"
        soup.name = "Fish Soup"
        soup.servings = 2.5
        db.session.add(soup)
        db.session.commit()

        person = Person()
        person.id = '4566'
        db.session.add(person)
        db.session.commit()

        mc = MealRecord()
        mc.meal = soup
        mc.person = person
        mc.qty = 1
        mc.timestamp = datetime.datetime.now()

        db.session.add(mc)
        db.session.commit()

        fetched = MealRecord.query.filter(MealRecord.person_id == person.id).first()
        assert(fetched.meal == soup)

        # extensive cleanup, will work even when cascade might be broken
        db.session.delete(mc)
        db.session.delete(soup)
        db.session.delete(person)


def test_meal_record_creation_many(app):
    with app.app_context():
        # make sure we can have many records for one person
        # and many records for one meal
        p1 = Person(id="333")
        p2 = Person(id="444")
        m1 = Meal(id="123", name="meal1", servings=2)
        m2 = Meal(id="456", name="meal2", servings=2)

        entities = [p1, p2, m1, m2]

        p1m1 = MealRecord()
        p1m1.person = p1
        p1m1.meal = m1
        p1m1.qty = 1
        p1m1.timestamp = datetime.datetime.now()
        entities.append(p1m1)

        p1m2 = MealRecord()
        p1m2.person = p1
        p1m2.meal = m2
        p1m2.qty = 1
        p1m2.timestamp = datetime.datetime.now()
        entities.append(p1m2)

        p2m1 = MealRecord()
        p2m1.person = p2
        p2m1.meal = m1
        p2m1.qty = 1
        p2m1.timestamp = datetime.datetime.now()
        entities.append(p2m1)

        p2m2 = MealRecord()
        p2m2.person = p2
        p2m2.meal = m2
        p2m2.qty = 1.5
        p2m2.timestamp = datetime.datetime.now()
        entities.append(p2m2)

        for i in entities:
            db.session.add(i)
        db.session.commit()

        fetched = MealRecord.query.filter(and_(Person.id == p1.id, Meal.id == m1.id)).first()
        assert (fetched is not None)
        db.session.delete(fetched)
        fetched = MealRecord.query.filter(and_(Person.id == p1.id, Meal.id == m2.id)).first()
        assert (fetched is not None)
        db.session.delete(fetched)
        fetched = MealRecord.query.filter(and_(Person.id == p2.id, Meal.id == m1.id)).first()
        assert (fetched is not None)
        db.session.delete(fetched)
        fetched = MealRecord.query.filter(and_(Person.id == p2.id, Meal.id == m2.id)).first()
        assert (fetched is not None)
        db.session.delete(fetched)

        db.session.delete(p1)
        db.session.delete(p1)
        db.session.delete(m1)
        db.session.delete(m2)


def test_meal_record_cascade_on_person(app):
    with app.app_context():
        soup = Meal()
        soup.id = "678"
        soup.name = "Fish Soup"
        soup.servings = 2.5
        db.session.add(soup)
        db.session.commit()

        person = Person()
        person.id = '4566'
        db.session.add(person)
        db.session.commit()

        mc = MealRecord()
        mc.meal = soup
        mc.person = person
        mc.qty = 1.5
        mc.timestamp = datetime.datetime.now()

        db.session.add(mc)
        db.session.commit()

        db.session.delete(person)
        db.session.commit()

        fetched = MealRecord.query.filter(MealRecord.person_id == person.id).first()
        assert (fetched is None)

def test_meal_record_cascade_on_meal(app):
    with app.app_context():
        soup = Meal()
        soup.id = "678"
        soup.name = "Fish Soup"
        soup.servings = 2.5
        db.session.add(soup)
        db.session.commit()

        person = Person()
        person.id = '4566'
        db.session.add(person)
        db.session.commit()

        mc = MealRecord()
        mc.meal = soup
        mc.person = person
        mc.qty = 1.5
        mc.timestamp = datetime.datetime.now()


        db.session.add(mc)
        db.session.commit()

        db.session.delete(soup)
        db.session.commit()

        fetched = MealRecord.query.filter(MealRecord.person_id == person.id).first()
        assert (fetched is None)


@pytest.mark.filterwarnings("ignore")
def test_meal_record_cascade_many(app):
    with app.app_context():
        # make sure we can have many records for one person
        # and many records for one meal
        p1 = Person(id="333")
        p2 = Person(id="444")
        m1 = Meal(id="123", name="meal1", servings=2)
        m2 = Meal(id="456", name="meal2", servings=2)

        entities = [p1, p2, m1, m2]

        p1m1 = MealRecord()
        p1m1.person = p1
        p1m1.meal = m1
        p1m1.qty = 1.5
        p1m1.timestamp = datetime.datetime.now()
        entities.append(p1m1)

        p1m2 = MealRecord()
        p1m2.person = p1
        p1m2.meal = m2
        p1m2.qty = 1
        p1m2.timestamp = datetime.datetime.now()
        entities.append(p1m2)

        p2m1 = MealRecord()
        p2m1.person = p2
        p2m1.meal = m1
        p2m1.qty = 1
        p2m1.timestamp = datetime.datetime.now()
        entities.append(p2m1)

        p2m2 = MealRecord()
        p2m2.person = p2
        p2m2.meal = m2
        p2m2.qty = 1
        p2m2.timestamp = datetime.datetime.now()
        entities.append(p2m2)

        for i in entities:
            db.session.add(i)
        db.session.commit()
        db.session.delete(p1)
        db.session.delete(m1)
        db.session.commit()
        fetched = MealRecord.query.filter(Person.id == p1.id).first()
        assert (fetched is None)
        fetched = MealRecord.query.filter(Meal.id == m1.id).first()
        assert (fetched is None)
        fetched = MealRecord.query.filter(Person.id == p2.id).first()
        assert (fetched is not None)
        fetched = MealRecord.query.filter(Meal.id == m2.id).first()
        assert (fetched is not None)

        for i in entities:
            db.session.delete(i)
        db.session.commit()

# ignore warning for SQLAlchemy missing primary key as missing the primary
# key is part of the test
@pytest.mark.filterwarnings("ignore")
def test_activity_columns(app):
    with app.app_context():
        """
        Tests for required columns activity
        """
        running = Activity()
        running.id = "1234"
        running.name = "running"
        running.intensity = "abs" # 600kcal per hour

        running.name = None
        db.session.add(running)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        running.id = None
        db.session.add(running)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        running.intensity = None
        db.session.add(running)
        with pytest.raises(IntegrityError):
            db.session.commit()


# ignore warning for SQLAlchemy missing primary key as missing the primary
# key is part of the test
@pytest.mark.filterwarnings("ignore")
def test_meal_columns(app):
    with app.app_context():
        """
        Tests for required columns meal
        """
        meal = Meal()
        meal.id = "123"
        meal.name = "Soup"
        meal.servings = 2  # 2 servings

        meal.name = None
        db.session.add(meal)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        meal.id = None
        db.session.add(meal)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        meal.servings = None
        db.session.add(meal)
        with pytest.raises(IntegrityError):
            db.session.commit()
