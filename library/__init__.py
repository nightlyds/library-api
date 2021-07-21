import os
import datetime
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, got_request_exception
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_marshmallow import Marshmallow
from flask_jwt import JWT
import logging

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

basedir = os.path.abspath(os.path.dirname(__file__))

database_user = os.environ.get('POSTGRES_USER')
database_password = os.environ.get('POSTGRES_PASSWORD')
database_host = os.environ.get('POSTGRES_HOSTNAME')
database_db = os.environ.get('POSTGRES_DB')

app.config.update(
    SQLALCHEMY_DATABASE_URI=f'postgresql://{database_user}:{database_password}@{database_host}/{database_db}',
    SECRET_KEY=os.environ.get('SECRET_KEY'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    ENV=os.environ.get('ENV'),
    DEBUG=os.environ.get('DEBUG'),
    JWT_EXPIRATION_DELTA=datetime.timedelta(days=30),
    UPLOAD_FOLDER=os.path.join(basedir, 'upload'),
    ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'gif', 'svg', 'bmp'},
    ALLOWED_MIMETYPES_EXTENSIONS={'image/apng', 'image/bmp', 'image/jpeg',
                                  'image/png', 'image/svg+xml'},
    MAX_CONTENT_LENGTH=4 * 1024 * 1024
)

logging.basicConfig(filename='logs.log', level=logging.WARNING)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app, catch_all_404s=True)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)


def log_exception(sender, exception, **extra):
    """ Log an exception to our logging framework """
    sender.logger.warning('Got exception during processing: %s', exception)


got_request_exception.connect(log_exception, app)


from library.models import User


def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    print(user)

    if user and user.check_password(password):
        return user


def identity(payload):
    user_id = payload['identity']

    return User.query.filter_by(id=user_id).first()


jwt = JWT(app, authenticate, identity)

from library import routes