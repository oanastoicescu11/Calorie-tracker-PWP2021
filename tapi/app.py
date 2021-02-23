""" Simple SQLAlchemy model Programmable Web Course
Copyright: jjuutine20@student.oulu.fi, oanastoicescu11@gmail.com

An example from the exercise taken as a base and then modified (Measurement example)
"""

# BEGIN of the content taken from the exercise example
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref, validates

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# END of the content taken from the exercise example
# now group's own content from here on.


class Person(db.Model):
    """ Person- All columns required """
    id = db.Column(db.String(128), primary_key=True)


class Activity(db.Model):
    """ Activity- id, name and intensity required """
    id = db.Column(db.String(128), primary_key=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    intensity = db.Column(db.Integer, nullable=False, default=0)
    # Description max size 8K for simplicity reasons
    description = db.Column(db.String(8*1024), nullable=True)
    persons = relationship("ActivityRecord", cascade="all, delete-orphan")

    # intensity is positive integer
    @validates('intensity')
    def validate_intensity(self, key, intensity):
        value = int(intensity)
        if value < 0:
            raise ValueError("'intensity' not positive integer!")
        return intensity


class ActivityRecord(db.Model):
    """ ActivityRecord- All columns required """
    person_id = db.Column(db.String(128), ForeignKey('person.id'), primary_key=True)
    activity_id = db.Column(db.String(128), ForeignKey('activity.id'), primary_key=True)
    person = relationship(Person, backref=backref("activities", cascade="all, delete-orphan"))
    activity = relationship(Activity, backref=backref("activityrecords"))
    duration = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, primary_key=True)


class Meal(db.Model):
    """  id, name and servings required """
    id = db.Column(db.String(128), primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    servings = db.Column(db.Float, nullable=False)
    # Description max size 8K for simplicity reasons
    description = db.Column(db.String(8*1024), nullable=True)
    persons = relationship("MealRecord", cascade="all, delete-orphan")
    #portions = relationship("MealPortion", cascade="all, delete-orphan")


class MealRecord(db.Model):
    """ MealRecord- All columns required """
    person_id = db.Column(db.String(128), ForeignKey('person.id'), primary_key=True)
    meal_id = db.Column(db.String(128), ForeignKey('meal.id'), primary_key=True)
    person = relationship(Person, backref=backref("meals", cascade="all, delete-orphan"))
    meal = relationship(Meal, backref=backref("mealrecords"))
    qty = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, primary_key=True)

# Simple sanity check for Person (ipython)
# In [1]: from app import db
# In [2]: db.create_all()
# In [3]: from app import Person
# In [4]: person = Person()
# In [5]: person.id = "123"
# In [9]: db.session.add(oatmeal)
# In [10]: db.session.commit()
# In [11]: print(person)
# <Person 123>
