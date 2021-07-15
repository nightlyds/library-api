from library import ma, db
from marshmallow_enum import EnumField
from marshmallow import fields
from library.models import Author, Book, BookCoverEnum, BookStatusEnum, \
    BookFormatEnum, RatingEnum, Genre, Order, User, OrderItem, \
    OrderItemStatusEnum, UserRoleEnum, Review, ReviewImage


class BookSchemaForAuthor(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Book
        load_instance = True
        sqla_session = db.session
        include_fk = True

    cover = EnumField(BookCoverEnum, by_value=True)
    status = EnumField(BookStatusEnum, by_value=True)
    rating = EnumField(RatingEnum, by_value=True)
    format = EnumField(BookFormatEnum, by_value=True)


class AuthorSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Author
        include_relationships = True
        load_instance = True
        sqla_session = db.session
        include_fk = True

    rating = EnumField(RatingEnum, by_value=True)
    books = fields.List(fields.Nested(BookSchemaForAuthor))

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("author", values=dict(id="<id>")),
            "collection": ma.URLFor("authors"),
        }
    )


author_schema = AuthorSchema()
authors_schema = AuthorSchema(many=True)


class AuthorSchemaForBook(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Author
        include_fk = True
        load_instance = True
        sqla_session = db.session

    rating = EnumField(RatingEnum, by_value=True)


class BookSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Book
        include_relationships = True
        load_instance = True
        sqla_session = db.session
        include_fk = True

    cover = EnumField(BookCoverEnum, by_value=True)
    status = EnumField(BookStatusEnum, by_value=True)
    rating = EnumField(RatingEnum, by_value=True)
    format = EnumField(BookFormatEnum, by_value=True)
    authors = fields.List(fields.Nested(AuthorSchemaForBook))

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("book", values=dict(id="<id>")),
            "collection": ma.URLFor("books"),
        }
    )


book_schema = BookSchema()
books_schema = BookSchema(many=True)


class GenreSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Genre
        load_instance = True
        sqla_session = db.session
        include_fk = True

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("genre", values=dict(id="<id>")),
            "collection": ma.URLFor("genres"),
        }
    )


genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


class OrderItemSchemaForOrder(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderItem
        include_fk = True
        load_instance = True
        sqla_session = db.session

    status = EnumField(OrderItemStatusEnum, by_value=True)


class OrderSchemaForUser(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True
        load_instance = True
        sqla_session = db.session

    items = fields.List(fields.Nested(OrderItemSchemaForOrder))


class ReviewImageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ReviewImage
        include_fk = True
        load_instance = True
        sqla_session = db.session


review_image_schema = ReviewImageSchema()
review_images_schema = ReviewImageSchema(many=True)


class ReviewSchemaForUser(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Review
        include_fk = True
        load_instance = True
        sqla_session = db.session

    images = fields.List(fields.Nested(ReviewImageSchema))


class UserSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        include_fk = True

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("user", values=dict(id="<id>")),
            "collection": ma.URLFor("users"),
        }
    )

    password = fields.String()
    role = EnumField(UserRoleEnum, by_value=True)
    orders = fields.List(fields.Nested(OrderSchemaForUser))
    reviews = fields.List(fields.Nested(ReviewSchemaForUser))


class PasswordSchema(ma.Schema):

    password = fields.String()


password_schema = PasswordSchema()


user_schema = UserSchema(exclude=['_User__password', 'password'])
user_schema_with_password = UserSchema(exclude=['_User__password'])
users_schema = UserSchema(many=True, exclude=['_User__password', 'password'])
users_schema_with_password = UserSchema(many=True, exclude=['_User__password'])


class OrderSchema(OrderSchemaForUser):

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("order", values=dict(id="<id>")),
            "collection": ma.URLFor("orders"),
        }
    )


order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


class OrderItemSchema(OrderItemSchemaForOrder):

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("order-item", values=dict(id="<id>")),
            "collection": ma.URLFor("order-items"),
        }
    )


order_item_schema = OrderItemSchema()
order_items_schema = OrderItemSchema(many=True)


class ReviewSchema(ReviewSchemaForUser):

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("review", values=dict(id="<id>")),
            "collection": ma.URLFor("reviews"),
        }
    )


review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)