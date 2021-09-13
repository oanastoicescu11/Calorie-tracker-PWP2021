import json

from flask import Response, request
from flask_restful import Resource
from jsonschema import validate, SchemaError, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from tapi.models import Person
from tapi.utils import add_mason_response_header, add_calorie_namespace, person_to_api_person
from tapi.utils import CalorieBuilder
from tapi.utils import error_400, error_404, error_409, error_415
from tapi.constants import MASON, NS, ROUTE_ENTRYPOINT, ROUTE_PERSON_COLLECTION
from tapi import db
from tapi.api import api


# PersonItem type specific helper functions
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


def add_control_add_person(resp):
    resp.add_control(
        NS + ":add-person",
        href=api.url_for(PersonItem, handle=None),
        method="POST",
        encoding="json",
        title="Creates a new Person",
        schema=person_schema()
    )


def add_control_mealrecords(resp, handle):
    resp.add_control(NS + ':mealrecords-by', "{}{}{}/mealrecords/".format(
        ROUTE_ENTRYPOINT,
        ROUTE_PERSON_COLLECTION,
        handle))


class PersonItem(Resource):
    """ PersonItem servers both: Individual PersonItem and Person Collection
    If given handle is missing, the Person Collection is returned. If handle is
    given, the corresponding PersonItem is returned (if found from the DB) """
    @classmethod
    def get(cls, handle=None):
        if handle is None:
            # Person collection
            resp = CalorieBuilder(items=[])
            for person in Person.query.all():
                p = person_to_api_person(person)
                p.add_control_collection(api.url_for(PersonItem, handle=None))
                resp['items'].append(p)
            add_control_add_person(resp)
        else:
            # Person item
            person = Person.query.filter(Person.id == handle).first()
            if person is None:
                return error_404()
            resp = person_to_api_person(person)
            resp.add_control_collection(api.url_for(PersonItem, handle=None))
            resp.add_control_delete(api.url_for(PersonItem, handle=handle))
            add_control_mealrecords(resp, handle)

        # Common fields for person item and person collection
        resp.add_control_self(api.url_for(PersonItem, handle=handle))
        resp.add_control(NS+':persons-all', api.url_for(PersonItem, handle=None))
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

        h = add_mason_response_header()
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
