import os
import shutil
from flask import request
from library import app, db
from library.routes import ResourseAuth
from services import allowed_file
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError
from library.models import User, ReviewImage, Review
from library.schemas import user_schema, user_schema_with_password, \
    review_image_schema, review_images_schema, password_schema
from services import check_whether_the_instance_exist, check_whether_picture_exist


class Pages(ResourseAuth):

    def __init__(self, model, scheme_many, scheme, message_name):
        self.model = model
        self.scheme_many = scheme_many
        self.scheme = scheme
        self.message_name = message_name

    def get(self):
        instances = self.model.query.all()

        return self.scheme_many.dump(instances)

    def post(self):
        json_data = request.get_json(force=True)

        try:
            instance = self.scheme.load(json_data)

            db.session.add(instance)
            db.session.commit()

            return self.scheme.dump(instance), 201

        except ValidationError as ve:
            return {'exception': ve.messages}, 400

        except IntegrityError:
            return {'exception': f'An exception occured while creating the {self.message_name}!'}, 400


class Page(ResourseAuth):

    def __init__(self, model, scheme, message_name, directory_name=None):
        self.model = model
        self.scheme = scheme
        self.message_name = message_name
        self.directory_name = directory_name

    def get(self, id):
        instance = check_whether_the_instance_exist(self.model, id, f"{self.message_name} {id} doesn`t exist.")

        return self.scheme.dump(instance)

    def put(self, id):
        check_whether_the_instance_exist(self.model, id, f"{self.message_name} {id} doesn`t exist.")
        json_data = request.get_json(force=True)

        try:
            instance = self.scheme.load(json_data)

            db.session.add(instance)
            db.session.commit()

            return self.scheme.dump(instance), 201

        except ValidationError as ve:
            return {'exception': ve.messages}, 400

        except IntegrityError:
            return {'exception': f'An exception occured while updating the {self.message_name.lower()}'}, 400

    def delete(self, id):
        instance = check_whether_the_instance_exist(self.model, id, f"{self.message_name} {id} doesn`t exist.")

        try:
            if self.directory_name:
                if instance.picture and os.path.isdir(
                        os.path.join(app.config['UPLOAD_FOLDER'], self.directory_name, str(instance.id))):
                    shutil.rmtree(os.path.join(app.config['UPLOAD_FOLDER'], self.directory_name, str(instance.id)))

            db.session.delete(instance)
            db.session.commit()

            return {'success': f'You successfully deleted the {self.message_name.lower()}!'}

        except:
            return {'exception': f'An exception throwed while deleting the {self.message_name.lower()}!'}, 400


class Picture(ResourseAuth):

    def __init__(self, model, message_name, directory_name, schema):
        self.model = model
        self.message_name = message_name
        self.directory_name = directory_name
        self.schema = schema

    def put(self, id):
        instance = check_whether_the_instance_exist(self.model, id, f"{self.message_name} {id} doesn`t exist.")

        if "file" not in request.files:
            return {"exception": "File didn`t found."}, 400

        uploaded_file = request.files["file"]

        if isinstance(uploaded_file, FileStorage) and allowed_file(
                uploaded_file.filename
        ):
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(uploaded_file.filename)

            # for further security checks
            mimetype = uploaded_file.content_type
            if mimetype and mimetype not in app.config["ALLOWED_MIMETYPES_EXTENSIONS"]:
                return {"exception": "File type not allowed, upload png, jpeg, svg files"}, 400

            target = os.path.join(app.config['UPLOAD_FOLDER'], self.directory_name, str(instance.id))

            if not os.path.exists(target):
                os.makedirs(target)

            target = os.path.join(self.directory_name, str(instance.id), filename)

            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], target))

            if instance.picture and os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], instance.picture)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], instance.picture))

            instance.picture = target

            db.session.add(instance)
            db.session.commit()

            return self.schema.dump(instance), 200

        return {'exception': 'An exception throwed while adding picture!'}, 400


class ChangePassword(ResourseAuth):

    def put(self, id):
        json_data = request.get_json(force=True)

        try:
            password_schema.load(json_data)

            user = User.query.filter_by(id=id).first()

            user.password = json_data['password']

            db.session.add(user)
            db.session.commit()

            return user_schema.dump(user), 201

        except ValidationError as ve:
            return {'exception': ve.messages}, 400

        except IntegrityError:
            return {'exception': f'An exception occured while updating password of the user!'}, 400


class UserPages(Pages):

    def post(self):
        json_data = request.get_json(force=True)

        try:
            instance = user_schema_with_password.load(json_data)

            db.session.add(instance)
            db.session.commit()

            return user_schema.dump(instance), 201

        except ValidationError as ve:
            return {'exception': ve.messages}, 400

        except IntegrityError:
            return {'exception': f'An exception occured while creating the user!'}, 400


class ReviewImagesPage(ResourseAuth):

    def get(self, review_id):
        review_images = ReviewImage.query.filter_by(review_id=review_id)

        if review_images:
            return review_images_schema.dump(review_images)

        return {[]}, 200

    def post(self, review_id):
        check_whether_the_instance_exist(Review, review_id, f"Review {review_id} doesn`t exist.")

        if "file" not in request.files:
            return {"exception": "File didn`t found."}, 400

        uploaded_file = request.files["file"]

        if isinstance(uploaded_file, FileStorage) and allowed_file(
                uploaded_file.filename
        ):
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(uploaded_file.filename)

            # for further security checks
            mimetype = uploaded_file.content_type
            if mimetype and mimetype not in app.config["ALLOWED_MIMETYPES_EXTENSIONS"]:
                return {"exception": "File type not allowed, upload png, jpeg, svg files"}, 400

            review_image = ReviewImage(review_id=review_id)

            db.session.add(review_image)
            db.session.commit()

            check_whether_picture_exist(review_id=review_id, instance=review_image)

            target = os.path.join(app.config['UPLOAD_FOLDER'],
                                  'review_images',
                                  str(review_id),
                                  str(review_image.id))

            if not os.path.exists(target):
                os.makedirs(target)

            uploaded_file.save(os.path.join(target, filename))

            target = os.path.join('review_images',
                                  str(review_id),
                                  str(review_image.id),
                                  filename)

            review_image.image = target

            db.session.add(review_image)
            db.session.commit()

            return review_image_schema.dump(review_image), 200

        return {'exception': 'An exception throwed while adding picture!'}, 400


class ReviewImagePage(ResourseAuth):

    def put(self, review_id, review_image_id):
        check_whether_the_instance_exist(Review, review_id, f"Review {review_id} doesn`t exist.")
        review_image = check_whether_the_instance_exist(ReviewImage, review_image_id,
                                                        f"Review Image {review_image_id} doesn`t exist.")

        if "file" not in request.files:
            return {"exception": "File didn`t found."}, 400

        uploaded_file = request.files["file"]

        if isinstance(uploaded_file, FileStorage) and allowed_file(
                uploaded_file.filename
        ):
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(uploaded_file.filename)

            # for further security checks
            mimetype = uploaded_file.content_type
            if mimetype and mimetype not in app.config["ALLOWED_MIMETYPES_EXTENSIONS"]:
                return {"exception": "File type not allowed, upload png, jpeg, svg files"}, 400

            check_whether_picture_exist(review_id=review_id, instance=review_image)

            target = os.path.join(app.config['UPLOAD_FOLDER'],
                                  'review_images',
                                  str(review_id),
                                  str(review_image.id))

            if not os.path.exists(target):
                os.makedirs(target)

            uploaded_file.save(os.path.join(target, filename))

            target = os.path.join('review_images',
                                  str(review_id),
                                  str(review_image.id),
                                  filename)

            review_image.image = target

            db.session.add(review_image)
            db.session.commit()

            return review_image_schema.dump(review_image), 200

        return {'exception': 'An exception throwed while adding picture!'}, 400

    def delete(self, review_id, review_image_id):
        check_whether_the_instance_exist(Review, review_id, f"Review {review_id} doesn`t exist.")
        review_image = check_whether_the_instance_exist(ReviewImage, review_image_id, f"Review Image {review_image_id} doesn`t exist.")

        try:
            if review_image.image and os.path.isdir(
                    os.path.join(app.config['UPLOAD_FOLDER'], 'review_images',
                                  str(review_id),
                                  str(review_image.id))):
                shutil.rmtree(os.path.join(app.config['UPLOAD_FOLDER'], 'review_images',
                                  str(review_id)))
            db.session.delete(review_image)
            db.session.commit()

            return {'success': f'You successfully deleted the review image!'}

        except:
            return {'exception': f'An exception throwed while deleting the review image!'}, 400


