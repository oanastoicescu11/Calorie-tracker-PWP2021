import json

from flask import Response, request
from flask_restful import Resource
from jsonschema import validate, SchemaError, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from tapi.models import Meal
from tapi.utils import add_mason_response_header, add_calorie_namespace, meal_to_api_meal
from tapi.utils import CalorieBuilder
from tapi.utils import error_400, error_404, error_409, error_415
from tapi.constants import MASON, NS
from tapi import db
from tapi.api import api


# MealItem type specific helper functions
def meal_schema():
    schema = {
        "type": "object",
        "required": ["id", "name", "servings"]
    }
    props = schema["properties"] = {}
    props['id'] = {
        "description": "usually meal name in small letters and white spaces replaced with dashes",
        "type": "string",
        "maxLength": 128,
        "pattern": "^[a-z,0-9]+(-[a-z,0-9]+)*$"
    }
    props['name'] = {
        "description": "meal name",
        "type": "string",
        "maxLength": 128
    }
    props['servings'] = {
        "description": "number of servings in this meal",
        "type": "integer"
    }
    props['description'] = {
        "description": "Description of the meal",
        "type": "string",
        "maxLength": 8192
    }
    return schema


def add_control_add_meal(resp):
    resp.add_control(
        NS + ":add-meal",
        href=api.url_for(MealItem, handle=None),
        method="POST",
        # TODO: json or should it be application/json?
        encoding="json",
        title="Creates a new Meal",
        schema=meal_schema()
    )


def add_control_edit_meal(resp, handle):
    resp.add_control(
        NS + ":edit-meal",
        href=api.url_for(MealItem) + handle + '/',
        method="PUT",
        # TODO: json or should it be application/json?
        encoding="json",
        title="Edits a Meal",
        schema=meal_schema()
    )


class MealItem(Resource):
    """ MealItem servers both: Individual MealItem and Meal Collection
    If given handle is missing, the Meal Collection is returned. If handle is
    given, the corresponding MealItem is returned (if found from the DB) """
    @classmethod
    def get(cls, handle=None):
        if handle is None:
            # Meal collection
            resp = CalorieBuilder(items=[])
            for meal in Meal.query.all():
                m = meal_to_api_meal(meal)
                m.add_control_collection(api.url_for(MealItem, handle=None))
                resp['items'].append(m)
            add_control_add_meal(resp)
        else:
            # Meal item
            meal = Meal.query.filter(Meal.id == handle).first()
            if meal is None:
                return error_404()
            resp = meal_to_api_meal(meal)
            resp.add_control_collection(api.url_for(MealItem, handle=None))
            resp.add_control_delete(api.url_for(MealItem, handle=handle))
            resp.add_control_profile()
            add_control_edit_meal(resp, handle)

        # Common fields for person item and person collection
        resp.add_control_self(api.url_for(MealItem, handle=handle))
        resp.add_control(NS+':meals-all', api.url_for(MealItem, handle=None))
        add_calorie_namespace(resp)
        return Response(json.dumps(resp), 200, headers=add_mason_response_header())

    @classmethod
    def post(cls):
        try:
            if request.json is None:
                return error_415()
        except BadRequest:
            return error_415()

        try:
            validate(request.json, schema=meal_schema())
        except (SchemaError, ValidationError):
            return error_400()

        meal_id = request.json['id']
        meal_name = request.json['name']
        meal_servings = request.json['servings']

        meal = Meal(
            id=meal_id,
            name=meal_name,
            servings=meal_servings
        )

        if 'description' in request.json.keys():
            meal.description = request.json['description']

        db.session.add(meal)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return error_409()

        h = add_mason_response_header()
        h.add('Location', api.url_for(MealItem, handle=meal.id))

        return Response(
            status=201,
            headers=h
        )

    @classmethod
    def put(cls, handle):
        try:
            if request.json is None:
                return error_415()
        except BadRequest:
            return error_415()

        try:
            validate(request.json, schema=meal_schema())
        except (SchemaError, ValidationError):
            return error_400()

        meal = Meal.query.filter(Meal.id == handle).first()
        if meal is None:
            return error_404()

        # We don't support a change of ID, so ID field from the request is ignored
        meal.name = request.json['name']
        meal.servings = request.json['servings']

        if 'description' in request.json.keys():
            meal.description = request.json['description']

        db.session.add(meal)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return error_409()

        return Response(
            response="",
            status=204,
            headers=add_mason_response_header()
        )

    @classmethod
    def delete(cls, handle=None):
        meal = Meal.query.filter(Meal.id == handle).first()
        if meal is None:
            return error_404()
        db.session.delete(meal)
        db.session.commit()
        return Response("DELETED", 204, mimetype=MASON)
