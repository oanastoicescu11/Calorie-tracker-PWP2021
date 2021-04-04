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

api.add_resource(PersonItem, ROUTE_PERSON, ROUTE_PERSON_COLLECTION)
