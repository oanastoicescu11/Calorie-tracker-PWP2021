# Structure following the course example, no copy paste though
# Flask restful example uses the same structure as well:
# https://flask-restful.readthedocs.io/en/latest/intermediate-usage.html#use-with-blueprints

# This is used in the __init__ when creating the Flask instance
import json
from flask import Blueprint, Response, redirect
from flask_restful import Api
from tapi.constants import *

api_blueprint = Blueprint('tapi', __name__, url_prefix=ROUTE_ENTRYPOINT)
api = Api(api_blueprint)

from tapi.resources.person import PersonItem
from tapi.resources.meal import MealItem
from tapi.resources.mealrecord import MealRecordItem
from tapi.resources.mealportion import MealPortionItem
from tapi.resources.portion import PortionItem
from tapi.utils import CalorieBuilder, add_mason_response_header, add_calorie_namespace


api.add_resource(PersonItem, ROUTE_PERSON, ROUTE_PERSON_COLLECTION)
api.add_resource(MealItem, ROUTE_MEAL, ROUTE_MEAL_COLLECTION)
api.add_resource(MealRecordItem, ROUTE_MEALRECORD, ROUTE_MEALRECORD_COLLECTION)
api.add_resource(MealPortionItem, ROUTE_MEALPORTION)
api.add_resource(PortionItem, ROUTE_PORTION, ROUTE_PORTION_COLLECTION)


# Route for entry point
@api_blueprint.route('/')
def entrypoint():
    resp = CalorieBuilder()
    resp.add_control(NS + ':persons-all', api.url_for(PersonItem, handle=None))
    resp.add_control(NS + ':meals-all', api.url_for(MealItem, handle=None))
    resp.add_control(NS + ':portions-all', api.url_for(PortionItem, handle=None))
    add_calorie_namespace(resp)
    return Response(json.dumps(resp), 200, headers=add_mason_response_header())


# Route for MealRecords for person
@api_blueprint.route('/persons/<handle>/mealrecords/')
def meals_for_person(handle):
    return MealRecordItem.get_records_for_person(handle)


# Route for MealPortion POST
@api_blueprint.route('/meals/<handle>/mealportions/', methods=['POST'])
def mealportions_for_meal(handle):
    return MealPortionItem.post(handle)


APIARY_URL = "https://pwp2021calorie.docs.apiary.io/#reference/"

@api_blueprint.route('/link-relations/')
def redirect_to_apiary_link_rels():
    return redirect(APIARY_URL + "link-relations")