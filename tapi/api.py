
# Structure following the course example, no copy paste though
# Flask restful example uses the same structure as well:
# https://flask-restful.readthedocs.io/en/latest/intermediate-usage.html#use-with-blueprints

# This is used in the __init__ when creating the Flask instance

from flask import Blueprint
from flask_restful import Api
from flask_restful import Resource

api_blueprint = Blueprint('tapi', __name__, url_prefix='/api')
api = Api(api_blueprint)


class Hello(Resource):
    def get(self):
        return "OK"


api.add_resource(Hello, "/hello/")
