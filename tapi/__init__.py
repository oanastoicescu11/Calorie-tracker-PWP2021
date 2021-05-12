# BEGIN of the content taken from the exercise example
import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
# END of the content taken from the exercise example
db = SQLAlchemy()


# create_app with test_config adopted from the course example
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    from tapi import api
    app.register_blueprint(api.api_blueprint)

    # Create all the tables if don't exist
    with app.app_context():
        db.create_all()
        from tapi.example_data import db_load_example_data
        db_load_example_data(db)



# @app.after_request taken from Blog post: https://modernweb.com/unlimited-access-with-cors/
    @app.after_request
    def add_cors(resp):
        """ Ensure all responses have the CORS headers. This ensures any failures are also accessible
            by the client. """
        resp.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET, DELETE, PUT'
        resp.headers['Access-Control-Expose-Headers'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = request.headers.get(
            'Access-Control-Request-Headers', 'Authorization')
        return resp

    return app
