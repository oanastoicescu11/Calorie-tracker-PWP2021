from flask import jsonify
from flask_restful import Resource
from tapi.models import Person


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
        return jsonify(collection)
