import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging

app = Flask(__name__)

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

app.config.update(
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URI'),
    SECRET_KEY=os.environ.get('SECRET_KEY'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    ENV=os.environ.get('ENV'),
    DEBUG=os.environ.get('DEBUG'),
)

logging.basicConfig(filename='logs.log', level=logging.WARNING)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from library import routes