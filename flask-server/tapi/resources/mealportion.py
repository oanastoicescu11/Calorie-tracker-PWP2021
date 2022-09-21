import json

from flask import Response, request
from flask_restful import Resource
from jsonschema import validate, SchemaError, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from tapi.models import Meal, MealPortion, Portion
from tapi.resources.meal import MealItem
from tapi.utils import add_mason_response_header, add_calorie_namespace, \
    mealportion_to_api_mealportion, make_mealportion_handle
from tapi.utils import error_400, error_404, error_409, error_415
from tapi.constants import MASON, NS
from tapi import db
from tapi.api import api


# MealItem type specific helper functions
def mealportion_schema():
    schema = {
        "type": "object",
        "required": ["weight_per_serving", "meal_id", "portion_id"]
    }
    props = schema["properties"] = {}
    props['meal_id'] = {
        "description": "usually meal name in small letters and white spaces replaced with dashes",
        "type": "string",
        "maxLength": 128,
        "pattern": "^[a-z,0-9]+(-[a-z,0-9]+)*$"
    }
    props['portion_id'] = {
        "description": "usually portion name in small letters and white spaces replaced with dashes",
        "type": "string",
        "maxLength": 128,
        "pattern": "^[a-z,0-9]+(-[a-z,0-9]+)*$"
    }
    props['weight_per_serving'] = {
        "description": "Weight of portion per serving of the Meal",
        "type": "number",
    }
    return schema


def add_control_edit_mealportion(resp, meal, handle):
    resp.add_control(
        NS + ":edit-mealportion",
        href=api.url_for(MealPortionItem, meal=meal, handle=handle),
        method="PUT",
        # TODO: json or should it be application/json?
        encoding="json",
        title="Edits a MealPortion",
        schema=mealportion_schema()
    )


def decode_handle(meal, handle):
    d = handle.split(meal + '-')
    return meal, d[1]


class MealPortionItem(Resource):
    @classmethod
    def get(cls, meal, handle):
        # MealPortion
        meal_id, portion_id = decode_handle(meal, handle)

        mealportion = MealPortion.query.filter(
            MealPortion.meal_id == meal_id,
            MealPortion.portion_id == portion_id).first()
        if mealportion is None:
            return error_404()
        resp = mealportion_to_api_mealportion(mealportion)

        resp.add_control_collection(api.url_for(MealItem, handle=meal_id) + "mealportions/")
        resp.add_control_delete(api.url_for(MealPortionItem, meal=meal, handle=handle))
        resp.add_control_profile()
        add_control_edit_mealportion(resp, meal, handle)

        resp.add_control_self(api.url_for(MealPortionItem, meal=meal, handle=handle))
        add_calorie_namespace(resp)
        return Response(json.dumps(resp), 200, headers=add_mason_response_header())

    @classmethod
    def post(cls, handle):
        try:
            if request.json is None:
                return error_415()
        except BadRequest:
            return error_415()

        try:
            validate(request.json, schema=mealportion_schema())
        except (SchemaError, ValidationError):
            return error_400()

        meal_id = handle
        portion_id = request.json['portion_id']
        mealportion = MealPortion(
            meal_id=meal_id,
            portion_id=portion_id,
            weight_per_serving=request.json['weight_per_serving']
        )

        db.session.add(mealportion)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return error_409()

        h = add_mason_response_header()
        h.add('Location', api.url_for(MealPortionItem,
                                      meal=meal_id,
                                      handle=make_mealportion_handle(meal_id, portion_id),
                                      _external=True))

        return Response(
            status=201,
            headers=h
        )

    @classmethod
    def put(cls, meal, handle):
        try:
            if request.json is None:
                return error_415()
        except BadRequest:
            return error_415()

        try:
            validate(request.json, schema=mealportion_schema())
        except (SchemaError, ValidationError):
            return error_400()

        meal_id, portion_id = decode_handle(meal, handle)
        mealportion = MealPortion.query.filter(
            MealPortion.meal_id == meal_id,
            MealPortion.portion_id == portion_id).first()
        if mealportion is None:
            return error_404()

        # Only weight per serving can be edited
        mealportion.weight_per_serving = request.json['weight_per_serving']

        db.session.add(mealportion)
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
    def delete(cls, meal, handle):
        meal_id, portion_id = decode_handle(meal, handle)
        mealportion = MealPortion.query.filter(
            MealPortion.meal_id == meal_id,
            MealPortion.portion_id == portion_id).first()
        if mealportion is None:
            return error_404()
        db.session.delete(mealportion)
        db.session.commit()
        return Response("DELETED", 204, mimetype=MASON)
