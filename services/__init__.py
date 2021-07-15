import os
import shutil
from library import app, db
from flask_restful import abort
from flask import request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


def allowed_file(filename):
    return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower()
            in app.config["ALLOWED_EXTENSIONS"]
    )


def check_whether_the_instance_exist(model, id, message):
    instance = model.query.filter_by(id=id).first()

    if not instance:
        abort(404, message=message)

    return instance


def check_whether_picture_exist(review_id, instance):
    if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'],
                                  'review_images',
                                  str(review_id),
                                  str(instance.id))):
        shutil.rmtree(os.path.join(app.config['UPLOAD_FOLDER'],
                               'review_images',
                               str(review_id),
                               str(instance.id)))
