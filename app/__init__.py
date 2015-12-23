from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object('config')

db = MongoEngine(app)
mail = Mail()
mail.init_app(app)

from app import views, models
