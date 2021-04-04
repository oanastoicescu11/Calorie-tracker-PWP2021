import json

from flask import Response
from flask_restful import Resource
from tapi.models import Person
from tapi.utils import add_mason_request_header


class PersonItem(Resource):
    def get(self):
        pass


class PersonCollection(Resource):
    def get(self):
        collection = []
        for person in Person.query.all():
            collection.append({
                'id': person.id
            })
        return Response(
            response=json.dumps(collection),
            status=200,
            headers=add_mason_request_header()
        )
