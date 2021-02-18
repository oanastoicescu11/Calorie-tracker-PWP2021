import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from tapi.app import app, ActivityRecord
from tapi.app import db
from tapi.app import Person, Activity

# BEGIN Original fixture setup taken from the Exercise example and then modified further

import os
import tempfile
from sqlalchemy.engine import Engine
from sqlalchemy import event, and_


@pytest.fixture
def dbh():
    db_fd, db_fname = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

    yield db

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
def test_person_combo(dbh):
    # create original person (id=677) and commit to db
    pid = "677"
    p_original = Person(id=pid)
    dbh.session.add(p_original)
    dbh.session.commit()
    # fetch the original person from the DB as 'fetched'
    fetched = Person.query.filter(Person.id == pid).first()
    assert(fetched.id == pid)
    # change the fetched ID and commit to the DB, primary key still unique
    new_id = "677-modified"
    fetched.id = new_id
    dbh.session.add(fetched)
    dbh.session.commit()
    # delete the entity
    dbh.session.delete(fetched)
    dbh.session.commit()
    deleted = Person.query.filter(Person.id == new_id).first()
    assert(deleted is None)


# TODO: check this part
# 'Test that onModify and onDelete work as expected


def test_person_unique(dbh):
    same_id = "414"
    print("hello")
    p1 = Person(id=same_id)
    p2 = Person(id=same_id)
    dbh.session.add(p1, p2)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


# 'Create a new instance of the model
def test_person_creation(dbh):
    person = Person()
    person.id = "123"
    dbh.session.add(person)
    dbh.session.commit()


# 'Test possible errors conditions (e.g. foreign keys violation or other situation
# where Integrity error might be raised)

# Suppress warnings: Person without ID throws IntegrityError,
# but even caught triggers warning in pytest.
@pytest.mark.filterwarnings("ignore")
def test_person_id_required(dbh):
    person = Person()
    dbh.session.add(person)
    try:
        dbh.session.commit()
    except IntegrityError:
        dbh.session.rollback()


# 'Create a new instance of the model
def test_activity_creation(dbh):
    activity = Activity()
    activity.id = "123"
    activity.name = "Running"
    activity.intensity = 600  # 600kcal per hour
    dbh.session.add(activity)
    dbh.session.commit()
    # And with optional fields
    a = Activity()
    a.id = "127"
    a.name = "Running-Hard"
    a.intensity = 800  # 600kcal per hour
    a.description = "A harder exercise containing a continuous high heart beat running training"
    dbh.session.add(a)
    dbh.session.commit()

    dbh.session.delete(activity)
    dbh.session.delete(a)
    dbh.session.commit()


def test_activity_record_creation(dbh):
    running = Activity()
    running.id = "1234"
    running.name = "Running"
    running.intensity = 600  # 600kcal per hour
    dbh.session.add(running)
    dbh.session.commit()

    runner = Person()
    runner.id = '4566'
    dbh.session.add(runner)
    dbh.session.commit()

    ac = ActivityRecord()
    ac.activity = running
    ac.person = runner
    ac.duration = 3600
    ac.timestamp = datetime.datetime.now()

    dbh.session.add(ac)
    dbh.session.commit()

    fetched = ActivityRecord.query.filter(ActivityRecord.person_id == Person.id).first()
    assert(fetched.activity == running)

    # extensive cleanup, will work even when cascade might be broken
    dbh.session.delete(ac)
    dbh.session.delete(running)
    dbh.session.delete(runner)


def test_activity_record_creation_many(dbh):
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
        dbh.session.add(i)
    dbh.session.commit()

    fetched = ActivityRecord.query.filter(and_(Person.id == p1.id, Activity.id == a1.id)).first()
    assert (fetched is not None)
    dbh.session.delete(fetched)
    fetched = ActivityRecord.query.filter(and_(Person.id == p1.id, Activity.id == a2.id)).first()
    assert (fetched is not None)
    dbh.session.delete(fetched)
    fetched = ActivityRecord.query.filter(and_(Person.id == p2.id, Activity.id == a1.id)).first()
    assert (fetched is not None)
    dbh.session.delete(fetched)
    fetched = ActivityRecord.query.filter(and_(Person.id == p2.id, Activity.id == a2.id)).first()
    assert (fetched is not None)
    dbh.session.delete(fetched)

    dbh.session.delete(p1)
    dbh.session.delete(p1)
    dbh.session.delete(a1)
    dbh.session.delete(a2)


def test_activity_record_cascade_on_person(dbh):
    running = Activity()
    running.id = "1234"
    running.name = "Running"
    running.intensity = 600  # 600kcal per hour
    dbh.session.add(running)
    dbh.session.commit()

    runner = Person()
    runner.id = '4566'
    dbh.session.add(runner)
    dbh.session.commit()

    ac = ActivityRecord()
    ac.activity = running
    ac.person = runner
    ac.duration = 3600
    ac.timestamp = datetime.datetime.now()

    dbh.session.add(ac)
    dbh.session.commit()

    dbh.session.delete(runner)
    dbh.session.commit()
    fetched = ActivityRecord.query.filter(ActivityRecord.person_id == Person.id).first()
    assert (fetched is None)


def test_activity_record_cascade_on_activity(dbh):
    running = Activity()
    running.id = "1234"
    running.name = "Running"
    running.intensity = 600  # 600kcal per hour
    dbh.session.add(running)
    dbh.session.commit()

    runner = Person()
    runner.id = '4566'
    dbh.session.add(runner)
    dbh.session.commit()

    ac = ActivityRecord()
    ac.activity = running
    ac.person = runner
    ac.duration = 3600
    ac.timestamp = datetime.datetime.now()

    dbh.session.add(ac)
    dbh.session.commit()

    dbh.session.delete(running)
    dbh.session.commit()
    fetched = ActivityRecord.query.filter(ActivityRecord.person_id == Person.id).first()
    assert (fetched is None)


# delete on object previously deleted throws warning
# for simplicity reasons, all entities are purged at the end
@pytest.mark.filterwarnings("ignore")
def test_activity_record_cascade_many(dbh):
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
        dbh.session.add(i)
    dbh.session.commit()
    dbh.session.delete(p1)
    dbh.session.delete(a1)
    dbh.session.commit()
    fetched = ActivityRecord.query.filter(Person.id == p1.id).first()
    assert (fetched is None)
    fetched = ActivityRecord.query.filter(Activity.id == a1.id).first()
    assert (fetched is None)
    fetched = ActivityRecord.query.filter(Person.id == p2.id).first()
    assert (fetched is not None)
    fetched = ActivityRecord.query.filter(Activity.id == a2.id).first()
    assert (fetched is not None)

    for i in entities:
        dbh.session.delete(i)
    dbh.session.commit()
