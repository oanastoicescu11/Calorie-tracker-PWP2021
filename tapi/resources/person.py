import json

from flask import Response, request
from flask_restful import Resource
from jsonschema import validate, SchemaError, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from tapi.models import Person
from tapi.utils import add_mason_request_header, add_calorie_namespace, person_to_api_person
from tapi.utils import CalorieBuilder
from tapi.utils import error_400, error_404, error_409, error_415
from tapi.constants import ROUTE_PERSON_COLLECTION, MASON
from tapi import db
from tapi.api import api


def person_schema():
    schema = {
        "type": "object",
        "required": ["id"]
    }
    props = schema["properties"] = {}
    props['id'] = {
        "description": "Person id",
        "type": "string",
        "maxLength": 128,
        "pattern": "^[a-z,0-9]+(-[a-z,0-9]+)*$"
    }
    return schema


class PersonItem(Resource):
    @classmethod
    def get(cls, handle=None):
        if handle is None:
            resp = CalorieBuilder(items=[])
            for person in Person.query.all():
                p = person_to_api_person(person)
                p.add_control_collection(ROUTE_PERSON_COLLECTION)
                resp['items'].append(p)
        else:
            person = Person.query.filter(Person.id == handle).first()
            if person is None:
                return error_404()
            resp = person_to_api_person(person)
            resp.add_control_collection(ROUTE_PERSON_COLLECTION)

        add_calorie_namespace(resp)
        return Response(json.dumps(resp), 200, headers=add_mason_request_header())

    @classmethod
    def post(cls):
        try:
            if request.json is None:
                return error_415()
        except BadRequest:
            return error_415()

        try:
            validate(request.json, schema=person_schema())
        except (SchemaError, ValidationError):
            return error_400()

        person_id = request.json['id']
        person = Person(id=person_id)
        db.session.add(person)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return error_409()

        h = add_mason_request_header()
        h.add('Location', api.url_for(PersonItem, handle=person.id))

        return Response(
            status=201,
            headers=h
        )

    @classmethod
    def delete(cls, handle=None):
        person = Person.query.filter(Person.id == handle).first()
        if person is None:
            return error_404()
        db.session.delete(person)
        db.session.commit()
        return Response("DELETED", 204, mimetype=MASON)

