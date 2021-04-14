# Structure following the course example, no copy paste though
# Flask restful example uses the same structure as well:
# https://flask-restful.readthedocs.io/en/latest/intermediate-usage.html#use-with-blueprints

# This is used in the __init__ when creating the Flask instance

from flask import Blueprint
from flask_restful import Api
from tapi.constants import *

api_blueprint = Blueprint('tapi', __name__, url_prefix=ROUTE_ENTRYPOINT)
api = Api(api_blueprint)

from tapi.resources.person import PersonItem
from tapi.resources.meal import MealItem
from tapi.resources.mealrecord import MealRecordItem

api.add_resource(PersonItem, ROUTE_PERSON, ROUTE_PERSON_COLLECTION)
api.add_resource(MealItem, ROUTE_MEAL, ROUTE_MEAL_COLLECTION)
api.add_resource(MealRecordItem, ROUTE_MEALRECORD, ROUTE_MEALRECORD_COLLECTION)

# Route for MealRecords for person
@api_blueprint.route('/persons/<handle>/mealrecords/')
def meals_for_person(handle):
    return MealRecordItem.get_records_for_person(handle)
