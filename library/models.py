from sqlalchemy.orm import validates
from sqlalchemy.dialects.postgresql import ENUM as pgEnum
from library import db, bcrypt
import datetime
import enum
import re


class TimestampMixin:
    created_at = db.Column(
        db.DateTime(), default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime(), onupdate=datetime.datetime.now)


class Genre(db.Model):
    __tablename__ = 'genre'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(), nullable=False)


class RatingEnum(enum.Enum):
    zero = 0
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5


author_book = db.Table('author_book',
                       db.Column('author_id', db.Integer, db.ForeignKey('author.id', ondelete='CASCADE'), primary_key=True),
                       db.Column('book_id', db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), primary_key=True))


class Author(TimestampMixin, db.Model):
    __tablename__ = 'author'

    id = db.Column(db.Integer(), primary_key=True)
    picture = db.Column(db.Unicode(), nullable=True)
    firstname = db.Column(db.Unicode(64), nullable=False)
    lastname = db.Column(db.Unicode(64), nullable=False)
    country = db.Column(db.Unicode(), nullable=True)
    city = db.Column(db.Unicode(), nullable=True)
    biography = db.Column(db.Unicode(), nullable=False)
    rating = db.Column(pgEnum(RatingEnum, name="author_rating"), default=RatingEnum.zero)
    birthday = db.Column(db.DateTime(), nullable=True)
    books = db.relationship('Book', secondary=author_book, cascade="all, delete", lazy='subquery', backref=db.backref('authors', lazy=True))


class BookCoverEnum(enum.Enum):
    paperbook = 'paperbook'
    hardcover = 'hardcover'


class BookFormatEnum(enum.Enum):
    ebook = 'e-book'
    paper = 'paper'
    audio = 'audio'


class BookStatusEnum(enum.Enum):
    available = 'available'
    unavailable = 'unavailable'


class Book(TimestampMixin, db.Model):
    __tablename__ = 'book'

    id = db.Column(db.Integer(), primary_key=True)
    picture = db.Column(db.Unicode(), nullable=True)
    name = db.Column(db.Unicode(255), nullable=False)
    isbn = db.Column(db.Unicode(17), nullable=False)
    description = db.Column(db.Unicode(), nullable=True)
    cover = db.Column(pgEnum(BookCoverEnum, name='book_cover'), default=BookCoverEnum.paperbook, nullable=True)
    count = db.Column(db.Integer(), default=0)
    status = db.Column(pgEnum(BookStatusEnum, name='book_status'), default=BookStatusEnum.available)
    publisher = db.Column(db.Unicode(), nullable=False)
    rating = db.Column(pgEnum(RatingEnum, name='book_rating'), default=RatingEnum.zero)
    format = db.Column(pgEnum(BookFormatEnum, name='book_format'), default=BookFormatEnum.ebook, nullable=False)
    pages = db.Column(db.Integer(), default=1, nullable=False)
    genre_id = db.Column(db.Integer(), db.ForeignKey('genre.id', ondelete='CASCADE'), nullable=False)

    @validates('count')
    def validate_count(self, key, count):
        assert count >= 0
        return count


class UserRoleEnum(enum.Enum):
    visitor = 0
    admin = 1


class User(TimestampMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.Unicode(64), nullable=False, unique=True)
    picture = db.Column(db.Unicode(), nullable=True)
    firstname = db.Column(db.Unicode(64), nullable=False)
    lastname = db.Column(db.Unicode(64), nullable=False)
    email = db.Column(db.Unicode(255), nullable=True)
    __password = db.Column(db.String(), nullable=False)
    country = db.Column(db.Unicode(), nullable=True)
    city = db.Column(db.Unicode(), nullable=True)
    birthday = db.Column(db.DateTime(), nullable=True)
    role = db.Column(pgEnum(UserRoleEnum, name='user_role'), default=UserRoleEnum.visitor)
    orders = db.relationship('Order', cascade="all, delete", lazy=True)
    reviews = db.relationship('Review', cascade="all, delete", lazy=True)

    @validates('email')
    def validate_email(self, key, email):
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise AssertionError('Provided email is not an email address')

        return email

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password_to_hash):
        self.__password = bcrypt.generate_password_hash(password_to_hash).decode('utf-8')

    def check_password(self, password_to_check):
        return bcrypt.check_password_hash(self.__password, str(password_to_check))


class Order(TimestampMixin, db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    items = db.relationship('OrderItem', cascade="all, delete", lazy=True)


class OrderItemStatusEnum(enum.Enum):
    in_progress = 'in progress'
    returned = 'returned'


class OrderItem(TimestampMixin, db.Model):
    __tablename__ = 'order_item'

    id = db.Column(db.Integer(), primary_key=True)
    order_id = db.Column(db.Integer(), db.ForeignKey('order.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer(), db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)
    books_amount = db.Column(db.Integer(), default=1)
    status = db.Column(pgEnum(OrderItemStatusEnum, name='order_item_status'),
                       default=OrderItemStatusEnum.in_progress)
    end_at = db.Column(
        db.DateTime(), default=(datetime.datetime.now() + datetime.timedelta(days=10)))


class Review(TimestampMixin, db.Model):
    __tablename__ = 'review'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer(), db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.Unicode(), nullable=False)
    images = db.relationship('ReviewImage', cascade="all, delete", lazy=True)


class ReviewImage(db.Model):
    __tablename__ = 'review_image'

    id = db.Column(db.Integer(), primary_key=True)
    review_id = db.Column(db.Integer(), db.ForeignKey('review.id', ondelete='CASCADE'), nullable=False)
    image = db.Column(db.Unicode(), nullable=True)
