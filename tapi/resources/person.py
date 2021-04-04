import json

from flask import Response
from flask_restful import Resource
from tapi.models import Person
from tapi.utils import add_mason_request_header
from tapi.utils import CalorieBuilder
from tapi.utils import person_to_api_person
from tapi.utils import error_404
from tapi.utils import add_calorie_namespace
from tapi.constants import ROUTE_PERSON_COLLECTION


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
