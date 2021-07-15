from library import api
from flask_restful import Resource
from flask_jwt import jwt_required
from library.models import Author, Book, Genre, User, \
    Order, OrderItem, Review
from library.schemas import authors_schema, author_schema, \
    book_schema, books_schema, \
    genre_schema, genres_schema, \
    user_schema, users_schema, \
    order_schema, orders_schema, \
    order_item_schema, order_items_schema, \
    review_schema, reviews_schema


class ResourseAuth(Resource):
    method_decorators = [jwt_required()]


# routes
from library.views import Pages, Page, Picture, ChangePassword, \
                            UserPages, ReviewImagesPage, ReviewImagePage


api.add_resource(Pages, '/books', '/',
                 endpoint='books',
                 resource_class_args=[Book, books_schema, book_schema, 'book'])
api.add_resource(Page, '/books/<int:id>',
                 endpoint='book',
                 resource_class_args=[Book, book_schema, 'Book', 'books'])
api.add_resource(Picture, '/books/<int:id>/picture',
                 endpoint='book-picture',
                 resource_class_args=[Book, "Book",
                                      'books', book_schema])

api.add_resource(Pages, '/genres',
                 endpoint='genres',
                 resource_class_args=[Genre, genres_schema, genre_schema, 'genre'])
api.add_resource(Page, '/genres/<int:id>',
                 endpoint='genre',
                 resource_class_args=[Genre, genre_schema, 'Genre'])

api.add_resource(Pages, '/authors',
                 endpoint='authors',
                 resource_class_args=[Author, authors_schema, author_schema, 'author'])
api.add_resource(Page, '/authors/<int:id>',
                 endpoint='author',
                 resource_class_args=[Author, author_schema, 'Author', 'authors'])
api.add_resource(Picture, '/authors/<int:id>/picture',
                 endpoint='author-picture',
                 resource_class_args=[Author, "Author",
                                      'authors', author_schema])

api.add_resource(UserPages, '/users',
                 endpoint='users',
                 resource_class_args=[User, users_schema, user_schema, 'user'])
api.add_resource(Page, '/users/<int:id>',
                 endpoint='user',
                 resource_class_args=[User, user_schema, 'User', 'users'])
api.add_resource(ChangePassword, '/users/<int:id>/change-password',
                 endpoint='user-change-password')
api.add_resource(Picture, '/users/<int:id>/picture',
                 endpoint='user-picture',
                 resource_class_args=[User, "User",
                                      'users', user_schema])

api.add_resource(Pages, '/orders',
                 endpoint='orders',
                 resource_class_args=[Order, orders_schema, order_schema, 'order'])
api.add_resource(Page, '/orders/<int:id>',
                 endpoint='order',
                 resource_class_args=[Order, order_schema, 'Order'])

api.add_resource(Pages, '/order-items',
                 endpoint='order-items',
                 resource_class_args=[OrderItem, order_items_schema, order_item_schema, 'order item'])
api.add_resource(Page, '/order-items/<int:id>',
                 endpoint='order-item',
                 resource_class_args=[OrderItem, order_item_schema, 'Order Item'])

api.add_resource(Pages, '/reviews',
                 endpoint='reviews',
                 resource_class_args=[Review, reviews_schema, review_schema, 'review'])
api.add_resource(Page, '/reviews/<int:id>',
                 endpoint='review',
                 resource_class_args=[Review, review_schema, 'Review'])

api.add_resource(ReviewImagesPage, '/reviews/<int:review_id>/review-images',
                 endpoint='review-images')
api.add_resource(ReviewImagePage, '/reviews/<int:review_id>/review-images/<int:review_image_id>',
                 endpoint='review-image')
