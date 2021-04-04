
# BEGIN of the content taken from the exercise example
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# END of the content taken from the exercise example

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
