import json

from flask import Response, request
from flask_restful import Resource
from jsonschema import validate, SchemaError, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from tapi.models import Portion
from tapi.utils import add_mason_response_header, add_calorie_namespace, portion_to_api_portion
from tapi.utils import CalorieBuilder
from tapi.utils import error_400, error_404, error_409, error_415
from tapi.constants import MASON, NS
from tapi import db
from tapi.api import api


# PortionItem type specific helper functions
def portion_schema():
    schema = {
        "type": "object",
        "required": ["id", "name", "calories"]
    }
    props = schema["properties"] = {}
    props['id'] = {
        "description": "usually portion name in small letters and white spaces replaced with dashes",
        "type": "string",
        "maxLength": 128,
        "pattern": "^[a-z,0-9]+(-[a-z,0-9]+)*$"
    }
    props['name'] = {
        "description": "portion name",
        "type": "string",
        "maxLength": 128
    }
    props['calories'] = {
        "description": "number of calories/100g in this portion",
        "type": "number"
    }
    props['density'] = {
        "description": "Density of the portion",
        "type": "number",
        "maxLength": 8192
    }
    props['alcohol'] = {
        "description": "alcohol/100g of the portion",
        "type": "number",
        "maxLength": 8192
    }
    props['carbohydrate'] = {
        "description": "Carbs/100g of the portion",
        "type": "number",
        "maxLength": 8192
    }
    props['protein'] = {
        "description": "Protein/100g of the portion",
        "type": "number",
        "maxLength": 8192
    }
    props['fat'] = {
        "description": "Fat/100g of the portion",
        "type": "number",
        "maxLength": 8192
    }
    return schema


def add_control_add_portion(resp):
    resp.add_control(
        NS + ":add-portion",
        href=api.url_for(PortionItem, handle=None),
        method="POST",
        # TODO: json or should it be application/json?
        encoding="json",
        title="Creates a new Portion",
        schema=portion_schema()
    )


def add_control_edit_portion(resp, handle):
    resp.add_control(
        NS + ":edit-portion",
        href=api.url_for(PortionItem) + handle + '/',
        method="PUT",
        # TODO: json or should it be application/json?
        encoding="json",
        title="Edits a Portion",
        schema=portion_schema()
    )


class PortionItem(Resource):
    """ PortionItem servers both: Individual PortionItem and Portion Collection
    If given handle is missing, the Portion Collection is returned. If handle is
    given, the corresponding PortionItem is returned (if found from the DB) """
    @classmethod
    def get(cls, handle=None):
        if handle is None:
            # Portion collection
            resp = CalorieBuilder(items=[])
            for portion in Portion.query.all():
                m = portion_to_api_portion(portion)
                m.add_control_collection(api.url_for(PortionItem, handle=None))
                resp['items'].append(m)
            add_control_add_portion(resp)
        else:
            # Portion item
            portion = Portion.query.filter(Portion.id == handle).first()
            if portion is None:
                return error_404()

            resp = portion_to_api_portion(portion)
            resp.add_control_collection(api.url_for(PortionItem, handle=None))
            resp.add_control_delete(api.url_for(PortionItem, handle=handle))
            resp.add_control_profile()
            add_control_edit_portion(resp, handle)

        # Common fields for portion item and portion collection
        resp.add_control_self(api.url_for(PortionItem, handle=handle))
        resp.add_control(NS+':portions-all', api.url_for(PortionItem, handle=None))
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
            validate(request.json, schema=portion_schema())
        except (SchemaError, ValidationError):
            return error_400()

        portion_id = request.json['id']
        portion_name = request.json['name']
        portion_calories = request.json['calories']
        portion_density = request.json['density']
        portion_alcohol = request.json['alcohol']
        portion_carbohydrate = request.json['carbohydrate']
        portion_protein = request.json['protein']
        portion_fat = request.json['fat']

        portion = Portion(
            id=portion_id,
            name=portion_name,
            calories=portion_calories,
            density=portion_density,
            alcohol=portion_alcohol,
            carbohydrate=portion_carbohydrate,
            protein=portion_protein,
            fat=portion_fat
        )

        db.session.add(portion)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return error_409()

        h = add_mason_response_header()
        h.add('Location', api.url_for(PortionItem, handle=portion.id))

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
            validate(request.json, schema=portion_schema())
        except (SchemaError, ValidationError):
            return error_400()

        portion = Portion.query.filter(Portion.id == handle).first()
        if portion is None:
            return error_404()

        # We don't support a change of ID, so ID field from the request is ignored
        portion.name = request.json['name']
        portion.calories = request.json['calories']
        portion.density = request.json['density']
        portion.alcohol = request.json['alcohol']
        portion.carbohydrate = request.json['carbohydrate']
        portion.protein = request.json['protein']
        portion.fat = request.json['fat']

        db.session.add(portion)
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
        portion = Portion.query.filter(Portion.id == handle).first()
        if portion is None:
            return error_404()
        db.session.delete(portion)
        db.session.commit()
        return Response("DELETED", 204, mimetype=MASON)
