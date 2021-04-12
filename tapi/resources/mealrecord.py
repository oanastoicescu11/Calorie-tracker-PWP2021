import json

from flask import Response, request
from flask_restful import Resource
from jsonschema import validate, SchemaError, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from tapi.models import MealRecord
from tapi.utils import add_mason_response_header, add_calorie_namespace, mealrecord_to_api_mealrecord
from tapi.utils import CalorieBuilder
from tapi.utils import error_400, error_404, error_409, error_415
from tapi.constants import MASON, NS
from tapi import db
from tapi.api import api


# MealRecord type specific helper functions
def mealrecord_schema():
    schema = {
        "type": "object",
        "required": ["person_id", "meal_id", "amount", "timestamp"]
    }
    props = schema["properties"] = {}
    props['person_id'] = {
        "description": "Person id",
        "type": "string",
        "maxLength": 128,
        "pattern": "^[a-z,0-9]+(-[a-z,0-9]+)*$"
    }
    props['meal_id'] = {
        "description": "usually meal name in small letters and white spaces replaced with dashes",
        "type": "string",
        "maxLength": 128,
        "pattern": "^[a-z,0-9]+(-[a-z,0-9]+)*$"
    }
    props['amount'] = {
        "description": "number of servings of meal OR quantity of portion",
        "type": "float"
    }
    props['timestamp'] = {
        "description": "time of recording",
        "type": "datetime"
    }
    return schema


def make_mealrecord_handle(person, meal, timestamp):
    handle = person + '-' + meal + '-' + timestamp
    return handle


def add_control_add_mealrecord(resp):
    resp.add_control(
        NS + ":add-mealrecord",
        href=api.url_for(MealRecordItem, handle=None),
        method="POST",
        # TODO: json or should it be application/json?
        encoding="json",
        title="Creates a new MealRecord",
        schema=mealrecord_schema()
    )


def add_control_edit_mealrecord(resp, handle):
    resp.add_control(
        NS + ":edit-mealrecord",
        href=api.url_for(MealRecordItem) + handle + '/',
        method="PUT",
        # TODO: json or should it be application/json?
        encoding="json",
        title="Edits a MealRecord",
        schema=mealrecord_schema()
    )


class MealRecordItem(Resource):
    """ MealRecordItem serves: Individual MealRecordItem,MealRecord Collection ans MealRecord by person.
    If handle is missing, the MealRecord Collection is returned. If handle is missing but person is given,
     MealRecords by person are returned. If handle is
    given, the corresponding MealRecord is returned (if found from the DB) """
    @classmethod
    def get(cls, person=None, meal=None, timestamp=None):

        if person is not None and meal is not None and timestamp is not None:
            handle = make_mealrecord_handle(person, meal, timestamp)
        else:
            handle = None

        if handle is None and person is None:
            # MealRecord collection
            resp = CalorieBuilder(items=[])
            for mealrecord in MealRecord.query.all():
                m = mealrecord_to_api_mealrecord(mealrecord)
                m.add_control_collection(api.url_for(MealRecordItem, handle=None))
                resp['items'].append(m)
            add_control_add_mealrecord(resp)
        elif handle is None and person is not None:
            # MealRecords by person
            resp = CalorieBuilder(items=[])
            for mealrecord in MealRecord.query.filter(MealRecord.person_id == person).all():
                m = mealrecord_to_api_mealrecord(mealrecord)
                m.add_control_collection(api.url_for(MealRecordItem, handle=None))
                resp['items'].append(m)
            add_control_add_mealrecord(resp)
        else:
            # MealRecord item
            mealrecord = MealRecord.query.filter(MealRecord.person_id == person,
                                                 MealRecord.meal_id == meal,
                                                 MealRecord.timestamp == timestamp).first()
            if mealrecord is None:
                return error_404()
            resp = mealrecord_to_api_mealrecord(mealrecord)
            resp.add_control_collection(api.url_for(MealRecordItem, handle=None))
            resp.add_control_delete(api.url_for(MealRecordItem, handle=handle))
            resp.add_control_profile()
            add_control_edit_mealrecord(resp, handle)

        # Common fields for mealrecord item and mealrecord collection
        resp.add_control_self(api.url_for(MealRecordItem, handle=handle))
        resp.add_control(NS+':mealrecords-all', api.url_for(MealRecordItem, handle=None))
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
            validate(request.json, schema=mealrecord_schema())
        except (SchemaError, ValidationError):
            return error_400()

        mealrecord_person = request.json['person_id']
        mealrecord_meal = request.json['meal_id']
        mealrecord_amount = request.json['amount']
        mealrecord_timestamp = request.json['timestamp']

        mealrecord = MealRecord(
            person_id=mealrecord_person,
            meal_id=mealrecord_meal,
            amount=mealrecord_amount,
            timestamp=mealrecord_timestamp
        )

        db.session.add(mealrecord)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return error_409()

        h = add_mason_response_header()
        h.add('Location', api.url_for(MealRecordItem,
                                      handle=make_mealrecord_handle(mealrecord.person_id,
                                                                    mealrecord.meal_id,
                                                                    mealrecord.timestamp)))

        return Response(
            status=201,
            headers=h
        )

    @classmethod
    def put(cls, person, meal, timestamp):
        try:
            if request.json is None:
                return error_415()
        except BadRequest:
            return error_415()

        try:
            validate(request.json, schema=mealrecord_schema())
        except (SchemaError, ValidationError):
            return error_400()

        mealrecord = MealRecord.query.filter(MealRecord.person_id == person,
                                             MealRecord.meal_id == meal,
                                             MealRecord.timestamp == timestamp).first()
        if meal is None:
            return error_404()

        mealrecord.person_id = request.json['person_id']
        mealrecord.meal_id = request.json['meal_id']
        mealrecord.amount = request.json['amount']
        mealrecord.timestamp = request.json['timestamp']

        db.session.add(mealrecord)
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
    def delete(cls, person=None, meal=None, timestamp=None):
        mealrecord = MealRecord.query.filter(MealRecord.person_id == person,
                                 MealRecord.meal_id == meal,
                                 MealRecord.timestamp == timestamp).first()
        if mealrecord is None:
            return error_404()
        db.session.delete(mealrecord)
        db.session.commit()
        return Response("DELETED", 204, mimetype=MASON)
