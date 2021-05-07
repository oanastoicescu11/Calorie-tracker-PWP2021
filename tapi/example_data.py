from tapi.models import Person, Meal, MealRecord, Portion, MealPortion
import datetime


def db_load_example_data(db):
    person = Person()
    person.id = "123"

    portion1 = Portion()
    portion1.id = "olive-oil"
    portion1.calories = 700
    portion1.name = "Olive oil"
    portion1.density = 0.89
    portion1.fat = 100
    
    portion2 = Portion()
    portion2.id = "salmon"
    portion2.calories = 200
    portion2.name = "salmon"
    portion2.density = 0.95
    portion2.fat = 20
    
    portion3 = Portion()
    portion3.id = "cream"
    portion3.calories = 250
    portion3.name = "cream"
    portion3.density = 0.65
    portion3.fat = 15

    portion4 = Portion()
    portion4.id = "oat"
    portion4.calories = 250
    portion4.name = "oat"
    portion4.density = 0.65
    portion4.fat = 15

    portion5 = Portion()
    portion5.id = "milk"
    portion5.calories = 32
    portion5.name = "milk"
    portion5.density = 0.89
    portion5.fat = 2

    meal1 = Meal()
    meal1.id = "salmon-soup"
    meal1.name = "Salmon Soup"
    meal1.servings = 2.5

    meal2 = Meal()
    meal2.id = "oatmeal"
    meal2.name = "Oatmeal"
    meal2.servings = 2

    mp1 = MealPortion(meal_id=meal1.id, portion_id=portion1.id, weight_per_serving=10)
    mp2 = MealPortion(meal_id=meal1.id, portion_id=portion2.id, weight_per_serving=200)
    mp3 = MealPortion(meal_id=meal1.id, portion_id=portion3.id, weight_per_serving=200)

    mp4 = MealPortion(meal_id=meal2.id, portion_id=portion4.id, weight_per_serving=150)
    mp5 = MealPortion(meal_id=meal2.id, portion_id=portion5.id, weight_per_serving=50)

    m1 = MealRecord()
    m1.person = person
    m1.meal = meal1
    m1.amount = 1.5
    m1.timestamp = datetime.datetime.now()

    m2 = MealRecord()
    m2.person = person
    m2.meal = meal2
    m2.amount = 1
    m2.timestamp = datetime.datetime.now()

    m3 = MealRecord()
    m3.person = person
    m3.meal = meal1
    m3.amount = 1
    m3.timestamp = datetime.datetime(2020, 1, 31, 13, 14, 31)

    db.session.add(person)
    db.session.add(portion1)
    db.session.add(portion2)
    db.session.add(portion3)
    db.session.add(portion4)
    db.session.add(portion5)
    db.session.add(meal1)
    db.session.add(meal2)
    db.session.add(mp1)
    db.session.add(mp2)
    db.session.add(mp3)
    db.session.add(mp4)
    db.session.add(mp5)
    db.session.add(m1)
    db.session.add(m2)
    db.session.add(m3)
    db.session.commit()
