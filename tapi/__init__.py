# BEGIN of the content taken from the exercise example
import os
from flask import Flask
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

    return app
