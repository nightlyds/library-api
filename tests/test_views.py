import pytest
import os
from io import BytesIO
import json
from library import app, db
from library.models import Genre, Author, Book, \
    Order, OrderItem, Review, ReviewImage
from library.models import User


@pytest.fixture(autouse=True)
def initialize(session):
    genre = Genre(id=101, name='comedy')

    author1 = Author(id=101, firstname="test firstname 1", lastname="test lastname 1",
                     biography="test biography 1")
    author2 = Author(id=102, firstname="test firstname 2", lastname="test lastname 2",
                     biography="test biography 2")

    user = User(id=101, username="test username 1", firstname="test firstname 1",
                lastname="test lastname 1")

    user.password = 'test password 1'

    db.session.add_all([genre, author1, author2, user])
    db.session.commit()

    book1 = Book(id=101, name="test name 1", isbn="test isbn 1", count=3,
                 publisher="test publisher 1", pages=101, genre_id=101)
    book2 = Book(id=102, name="test name 2", isbn="test isbn 2", count=3,
                 publisher="test publisher 2", pages=201, genre_id=101)
    book3 = Book(id=103, name="test name 3", isbn="test isbn 3", count=3,
                 publisher="test publisher 3", pages=301, genre_id=101)

    db.session.add_all([book1, book2, book3])
    db.session.commit()

    author1.books.append(book1)
    author2.books.append(book2)
    author1.books.append(book3)
    author2.books.append(book3)

    order1 = Order(id=101, user_id=101)
    order2 = Order(id=102, user_id=101)

    review1 = Review(id=101, user_id=101, book_id=101, message="test message 1")
    review2 = Review(id=102, user_id=101, book_id=102, message="test message 2")

    db.session.add_all([author1, author2, order1, order2, review1, review2])
    db.session.commit()

    order_item1 = OrderItem(id=101, order_id=101, book_id=101,
                            books_amount=3)
    order_item2 = OrderItem(id=102, order_id=101, book_id=102)
    order_item3 = OrderItem(id=103, order_id=102, book_id=102,
                            books_amount=2)

    review_image1 = ReviewImage(id=101, review_id=101, image="review_image1.jpg")
    review_image2 = ReviewImage(id=102, review_id=101, image="review_image2.jpg")
    review_image3 = ReviewImage(id=103, review_id=102, image="review_image3.jpg")

    db.session.add_all([order_item1, order_item2, order_item3,
                        review_image1, review_image2, review_image3])
    db.session.commit()

    yield

    models = [genre, author1, author2, user]

    for model in models:
        db.session.delete(model)
        db.session.commit()

@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def jwt_token(session, client):
    user = User(firstname="test", username="test",
                lastname="test")

    user.password = "test"

    db.session.add(user)
    db.session.commit()

    response = client.post('/auth', data=json.dumps({
        "username": "test",
        "password": "test"
    }), headers={
        "Content-Type": "application/json"
    })

    yield f"JWT {response.get_json(force=True).get('access_token')}"

    db.session.delete(user)
    db.session.commit()


class TestGenre:

    def test_get_all(self, initialize, client, jwt_token):
        expected_data_genres = [
            {
                "_links": {
                    "self": "/genres/101",
                    "collection": "/genres"
                },
                "id": 101,
                "name": "comedy"
            }
        ]
        request = client.get('/genres', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert request_data == expected_data_genres
        assert request.status_code == 200

    def test_amount_of_genres(self, initialize, client, jwt_token):
        request = client.get('/genres', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert len(request_data) == 1
        assert request.status_code == 200

    def test_get_name_of_the_genre(self, initialize, client, jwt_token):
        expected_genre_name = 'comedy'
        request = client.get('/genres', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)
        genre_name = request_data[0].get('name')

        assert genre_name == expected_genre_name
        assert request.status_code == 200

    def test_add_new_genre(self, initialize, client, jwt_token):
        new_genre = {
            "id": 102,
            "name": "action"
        }
        request = client.post('/genres', headers={
            "Authorization": jwt_token
        }, data=json.dumps(new_genre))

        assert request.status_code == 201

    def test_add_new_genre_fail_with_validation_error(self, initialize, client, jwt_token):
        new_genre = {
                "id": 103
        }
        request = client.post('/genres', headers={
            "Authorization": jwt_token
        }, data=json.dumps(new_genre))

        request_data = request.get_json(force=True)

        assert request_data.get('exception') is not None
        assert request.status_code == 400

    def test_get_genre(self, initialize, client, jwt_token):
        expected_data_genre = {
            "_links": {
                "self": "/genres/102",
                "collection": "/genres"
            },
            "id": 102,
            "name": "action"
        }
        request = client.get('/genres/102', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert request_data == expected_data_genre
        assert request.status_code == 200

    def test_update_genre(self, initialize, client, jwt_token):
        update_genre_data = {
            "id": 102,
            "name": "adventures"
        }

        request = client.put('/genres/102', headers={
            "Authorization": jwt_token
        }, data=json.dumps(update_genre_data))

        request_data = request.get_json(force=True)
        genre = Genre.query.filter_by(id=102).first()

        assert request_data.get('name') == genre.name
        assert request.status_code == 201

    def test_delete_genre(self, initialize, client, jwt_token):
        expected_message = 'You successfully deleted the genre!'
        request = client.delete('/genres/102', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert request_data.get('success') == expected_message
        assert request.status_code == 200


class TestBook:

    def test_amount_of_books(self, initialize, client, jwt_token):
        request = client.get('/books', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert len(request_data) == 3
        assert request.status_code == 200

    def test_get_books_names(self, initialize, client, jwt_token):
        expected_books_names = ['test name 1', 'test name 2', 'test name 3']
        request = client.get('/books', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)
        books_names = []

        for book in request_data:
            for key, value in book.items():
                if key == 'name':
                    books_names.append(value)

        assert books_names == expected_books_names
        assert request.status_code == 200


    def test_add_new_book(self, initialize, client, jwt_token):

        genre = Genre(id=104, name='genre for test book')
        db.session.add(genre)
        db.session.commit()

        new_book = {
            "id": 104,
            "name": "test book 4",
            "isbn": "test isbn 4",
            "count": 3,
            "publisher": "test publisher 4",
            "pages": 401,
            "genre_id": 104
        }
        request = client.post('/books', headers={
            "Authorization": jwt_token
        }, data=json.dumps(new_book))

        assert request.status_code == 201

    def test_add_new_book_fail_with_validation_error(self, initialize, client, jwt_token):
        new_book = {
                "id": 105
        }
        request = client.post('/books', headers={
            "Authorization": jwt_token
        }, data=json.dumps(new_book))

        request_data = request.get_json(force=True)

        assert request_data.get('exception') is not None
        assert request.status_code == 400

    def test_update_book(self, initialize, client, jwt_token):
        update_book_data = {
            "id": 104,
            "name": "test name 4",
            "isbn": "test isbn 4",
            "count": 2,
            "publisher": "test publisher 4",
            "pages": 401,
            "genre_id": 104
        }

        request = client.put('/books/104', headers={
            "Authorization": jwt_token
        }, data=json.dumps(update_book_data))

        request_data = request.get_json(force=True)
        book = Book.query.filter_by(id=104).first()

        assert request_data.get('count') == book.count
        assert request.status_code == 201

    def test_book_picture_add(self, initialize, client, jwt_token):
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'image.jpg'), 'rb') as image:
            file_data = BytesIO(image.read())

        request = client.put('/books/104/picture',
                              content_type='multipart/form-data',
                              headers={"Authorization": jwt_token},
                              data={"file": (file_data, 'image.jpg')})

        request_data = request.get_json(force=True)

        assert request_data.get('picture') == 'books\\104\\image.jpg'
        assert request.status_code == 200

    def test_delete_book(self, initialize, client, jwt_token):
        expected_message = 'You successfully deleted the book!'
        request = client.delete('/books/104', headers={
            "Authorization": jwt_token
        })

        genre = Genre.query.filter_by(id=104).first()
        db.session.delete(genre)
        db.session.commit()

        request_data = request.get_json(force=True)

        assert request_data.get('success') == expected_message
        assert request.status_code == 200


class TestAuthor:

    def test_amount_of_authors(self, initialize, client, jwt_token):
        request = client.get('/authors', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert len(request_data) == 2
        assert request.status_code == 200

    def test_get_authors_firstnames(self, initialize, client, jwt_token):
        expected_authors_names = ['test firstname 1', 'test firstname 2']
        request = client.get('/authors', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)
        authors_firstnames = []

        for author in request_data:
            for key, value in author.items():
                if key == 'firstname':
                    authors_firstnames.append(value)

        assert authors_firstnames == expected_authors_names
        assert request.status_code == 200

    def test_add_new_author(self, initialize, client, jwt_token):
        new_author = {
            "id": 103,
            "firstname": "test firstname 3",
            "lastname": "test lastname 3",
            "biography": "test biography 3"
        }
        request = client.post('/authors', headers={
            "Authorization": jwt_token
        }, data=json.dumps(new_author))

        assert request.status_code == 201

    def test_get_author(self, initialize, client, jwt_token):
        expected_author_firstname = 'test firstname 3'
        request = client.get('/authors/103', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert request_data.get('firstname') == expected_author_firstname
        assert request.status_code == 200

    def test_add_new_author_fail_with_validation_error(self, initialize, client, jwt_token):
        new_author = {
            "id": 104
        }
        request = client.post('/authors', headers={
            "Authorization": jwt_token
        }, data=json.dumps(new_author))

        request_data = request.get_json(force=True)

        assert request_data.get('exception') is not None
        assert request.status_code == 400

    def test_update_author(self, initialize, client, jwt_token):
        update_author_data = {
            "id": 103,
            "firstname": "test firstname 3",
            "lastname": "test lastname 3",
            "biography": "test biography 3 updated"
        }

        request = client.put('/authors/103', headers={
            "Authorization": jwt_token
        }, data=json.dumps(update_author_data))

        request_data = request.get_json(force=True)
        author = Author.query.filter_by(id=103).first()

        assert request_data.get('biography') == author.biography
        assert request.status_code == 201

    def test_author_picture_add(self, initialize, client, jwt_token):
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'image2.jpg'), 'rb') as image:
            file_data = BytesIO(image.read())

        request = client.put('/authors/103/picture',
                              content_type='multipart/form-data',
                              headers={"Authorization": jwt_token},
                              data={"file": (file_data, 'image2.jpg')})

        request_data = request.get_json(force=True)

        assert request_data.get('picture') == 'authors\\103\\image2.jpg'
        assert request.status_code == 200

    def test_delete_author(self, initialize, client, jwt_token):
        expected_message = 'You successfully deleted the author!'
        request = client.delete('/authors/103', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert request_data.get('success') == expected_message
        assert request.status_code == 200


class TestUser:

    def test_amount_of_users(self, initialize, client, jwt_token):
        request = client.get('/users', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert len(request_data) == 2
        assert request.status_code == 200

    def test_get_users_usernames(self, initialize, client, jwt_token):
        expected_users_usernames = ['test username 1', 'test']
        request = client.get('/users', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)
        users_usernames = []

        for user in request_data:
            for key, value in user.items():
                if key == 'username':
                    users_usernames.append(value)

        assert users_usernames == expected_users_usernames
        assert request.status_code == 200

    def test_add_new_user(self, initialize, client, jwt_token):
        new_author = {
            "id": 103,
            "firstname": "test firstname 3",
            "username": "test username 3",
            "password": "test password 3",
            "lastname": "test lastname 3"
        }
        request = client.post('/users', headers={
            "Authorization": jwt_token
        }, data=json.dumps(new_author))

        assert request.status_code == 201

    def test_get_user_username(self, initialize, client, jwt_token):
        expected_user_username = 'test username 3'
        request = client.get('/users/103', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert request_data.get('username') == expected_user_username
        assert request.status_code == 200

    def test_add_new_user_fail_with_validation_error(self, initialize, client, jwt_token):
        new_user = {
            "id": 104
        }
        request = client.post('/users', headers={
            "Authorization": jwt_token
        }, data=json.dumps(new_user))

        request_data = request.get_json(force=True)

        assert request_data.get('exception') is not None
        assert request.status_code == 400

    def test_update_user(self, initialize, client, jwt_token):
        update_user_data = {
            "id": 103,
            "firstname": "test firstname 3",
            "lastname": "test lastname 3",
            "username": "test username 3 updated"
        }

        request = client.put('/users/103', headers={
            "Authorization": jwt_token
        }, data=json.dumps(update_user_data))

        request_data = request.get_json(force=True)
        user = User.query.filter_by(id=103).first()

        assert request_data.get('username') == user.username
        assert request.status_code == 201

    def test_user_picture_add(self, initialize, client, jwt_token):
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'image2.jpg'), 'rb') as image:
            file_data = BytesIO(image.read())

        request = client.put('/users/103/picture',
                              content_type='multipart/form-data',
                              headers={"Authorization": jwt_token},
                              data={"file": (file_data, 'image2.jpg')})

        request_data = request.get_json(force=True)

        assert request_data.get('picture') == 'users\\103\\image2.jpg'
        assert request.status_code == 200

    def test_user_change_password(self, initialize, client, jwt_token):
        update_user_data = {
            "password": "test password 3 updated"
        }

        request = client.put('/users/103/change-password', headers={
            "Authorization": jwt_token
        }, data=json.dumps(update_user_data))

        user = User.query.filter_by(id=103).first()

        assert user.check_password('test password 3 updated')
        assert request.status_code == 201

    def test_user_change_password_fail_with_validation_error(self, initialize, client, jwt_token):
        user_data = {
            "password_": 123
        }
        request = client.put('/users/103/change-password', headers={
            "Authorization": jwt_token
        }, data=json.dumps(user_data))

        request_data = request.get_json(force=True)

        assert request_data.get('exception') is not None
        assert request.status_code == 400

    def test_delete_user(self, initialize, client, jwt_token):
        expected_message = 'You successfully deleted the user!'
        request = client.delete('/users/103', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert request_data.get('success') == expected_message
        assert request.status_code == 200


class TestOrder:

    def test_amount_of_orders(self, initialize, client, jwt_token):
        request = client.get('/orders', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert len(request_data) == 2
        assert request.status_code == 200

    def test_get_orders_user_ids(self, initialize, client, jwt_token):
        expected_orders_user_ids = [101, 101]
        request = client.get('/orders', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)
        orders_user_ids = []

        for order in request_data:
            for key, value in order.items():
                if key == 'user_id':
                    orders_user_ids.append(value)

        assert orders_user_ids == expected_orders_user_ids
        assert request.status_code == 200

    def test_add_new_order(self, initialize, client, jwt_token):
        user = User(id=105, firstname="test firstname 7", username="test username 7", lastname="test lastname 7")
        user.password = 'test password 7'

        db.session.add(user)
        db.session.commit()

        new_order = {
            "id": 103,
            "user_id": 105
        }
        request = client.post('/orders', headers={
            "Authorization": jwt_token
        }, data=json.dumps(new_order))

        assert request.status_code == 201

    def test_get_order_user_id(self, initialize, client, jwt_token):
        expected_order_user_id = 105
        request = client.get('/orders/103', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert request_data.get('user_id') == expected_order_user_id
        assert request.status_code == 200

    def test_add_new_order_fail_with_validation_error(self, initialize, client, jwt_token):
        new_order = {
            "id": 104
        }
        request = client.post('/orders', headers={
            "Authorization": jwt_token
        }, data=json.dumps(new_order))

        request_data = request.get_json(force=True)

        assert request_data.get('exception') is not None
        assert request.status_code == 400

    def test_delete_order(self, initialize, client, jwt_token):
        expected_message = 'You successfully deleted the order!'
        request = client.delete('/orders/103', headers={
            "Authorization": jwt_token
        })

        user = User.query.filter_by(id=105).first()
        db.session.delete(user)
        db.session.commit()

        request_data = request.get_json(force=True)

        assert request_data.get('success') == expected_message
        assert request.status_code == 200


class TestOrderItem:

    def test_amount_of_order_items(self, initialize, client, jwt_token):
        request = client.get('/order-items', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert len(request_data) == 3
        assert request.status_code == 200

    def test_get_order_items_books_amounts(self, initialize, client, jwt_token):
        expected_order_items_books_amounts = [3, 1, 2]
        request = client.get('/order-items', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)
        order_items_books_amounts = []

        for order_item in request_data:
            for key, value in order_item.items():
                if key == 'books_amount':
                    order_items_books_amounts.append(value)

        assert order_items_books_amounts == expected_order_items_books_amounts
        assert request.status_code == 200

    def test_add_new_order_item(self, initialize, client, jwt_token):
        genre = Genre(id=104, name="test")
        user = User(id=106, firstname="test firstname 6", username="test username 6", lastname="test lastname 6")
        user.password = 'test password 6'

        db.session.add_all([genre, user])
        db.session.commit()

        book = Book(id=105, name="test name 5", isbn="test isbn 5", count=3,
                     publisher="test publisher 5", pages=501, genre_id=104)
        order = Order(id=105, user_id=106)
        db.session.add_all([order, book])
        db.session.commit()

        new_order_item = {
            "id": 104,
            "order_id": 105,
            "book_id": 105,
            "books_amount": 5
        }
        request = client.post('/order-items', headers={
            "Authorization": jwt_token
        }, data=json.dumps(new_order_item))

        assert request.status_code == 201

    def test_add_new_order_item_fail_with_validation_error(self, initialize, client, jwt_token):
        new_order_item = {
            "id": 105,
            "book_id": 105
        }
        request = client.post('/order-items', headers={
            "Authorization": jwt_token
        }, data=json.dumps(new_order_item))

        request_data = request.get_json(force=True)

        assert request_data.get('exception') is not None
        assert request.status_code == 400

    def test_update_order_item(self, initialize, client, jwt_token):
        update_order_item_data = {
            "id": 104,
            "order_id": 105,
            "book_id": 105,
            "books_amount": 7
        }

        request = client.put('/order-items/104', headers={
            "Authorization": jwt_token
        }, data=json.dumps(update_order_item_data))

        request_data = request.get_json(force=True)
        order_item = OrderItem.query.filter_by(id=104).first()

        assert request_data.get('books_amount') == order_item.books_amount
        assert request.status_code == 201

    def test_delete_order_item(self, initialize, client, jwt_token):
        expected_message = 'You successfully deleted the order item!'
        request = client.delete('/order-items/104', headers={
            "Authorization": jwt_token
        })

        genre = Genre.query.filter_by(id=104).first()
        user = User.query.filter_by(id=106).first()
        book = Book.query.filter_by(id=105).first()
        order = Order.query.filter_by(id=105).first()

        db.session.delete(genre)
        db.session.delete(user)
        db.session.delete(book)
        db.session.delete(order)
        db.session.commit()

        request_data = request.get_json(force=True)

        assert request_data.get('success') == expected_message
        assert request.status_code == 200


class TestReview:

    def test_amount_of_reviews(self, initialize, client, jwt_token):
        request = client.get('/reviews', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert len(request_data) == 2
        assert request.status_code == 200

    def test_get_review_messages(self, initialize, client, jwt_token):
        expected_review_messages = ['test message 1', 'test message 2']
        request = client.get('/reviews', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)
        review_messages = []

        for review in request_data:
            for key, value in review.items():
                if key == 'message':
                    review_messages.append(value)

        assert review_messages == expected_review_messages
        assert request.status_code == 200

    def test_add_new_review(self, initialize, client, jwt_token):
        genre = Genre(id=105, name="test")
        user = User(id=107, firstname="test firstname 7", username="test username 7", lastname="test lastname 7")
        user.password = 'test password 7'

        db.session.add_all([genre, user])
        db.session.commit()

        book = Book(id=106, name="test name 6", isbn="test isbn 6", count=3,
                     publisher="test publisher 6", pages=601, genre_id=105)
        db.session.add(book)
        db.session.commit()

        new_review = {
            "id": 103,
            "user_id": 107,
            "book_id": 106,
            "message": "test message 3"
        }
        request = client.post('/reviews', headers={
            "Authorization": jwt_token
        }, data=json.dumps(new_review))

        assert request.status_code == 201

    def test_add_new_review_fail_with_validation_error(self, initialize, client, jwt_token):
        new_review = {
            "id": 104,
            "user_id": 107,
            "book_id": 106
        }
        request = client.post('/reviews', headers={
            "Authorization": jwt_token
        }, data=json.dumps(new_review))

        request_data = request.get_json(force=True)

        assert request_data.get('exception') is not None
        assert request.status_code == 400

    def test_update_review(self, initialize, client, jwt_token):
        update_review_data = {
            "id": 103,
            "user_id": 107,
            "book_id": 106,
            "message": "test message 3 update"
        }

        request = client.put('/reviews/103', headers={
            "Authorization": jwt_token
        }, data=json.dumps(update_review_data))

        request_data = request.get_json(force=True)
        review = Review.query.filter_by(id=103).first()

        assert request_data.get('message') == review.message
        assert request.status_code == 201

    def test_delete_review(self, initialize, client, jwt_token):
        expected_message = 'You successfully deleted the review!'
        request = client.delete('/reviews/103', headers={
            "Authorization": jwt_token
        })

        genre = Genre.query.filter_by(id=105).first()
        user = User.query.filter_by(id=107).first()
        book = Book.query.filter_by(id=106).first()

        db.session.delete(genre)
        db.session.delete(user)
        db.session.delete(book)
        db.session.commit()

        request_data = request.get_json(force=True)

        assert request_data.get('success') == expected_message
        assert request.status_code == 200


class TestReviewImage:

    def test_get_review_images_for_review(self, initialize, client, jwt_token):
        request = client.get('/reviews/101/review-images', headers={
            "Authorization": jwt_token
        })

        request_data = request.get_json(force=True)

        assert len(request_data) == 2
        assert request.status_code == 200

    def test_add_new_review_image(self, initialize, client, jwt_token):
        genre = Genre(id=106, name="test")
        user = User(id=108, firstname="test firstname 8", username="test username 8", lastname="test lastname 8")
        user.password = 'test password 8'

        db.session.add_all([genre, user])
        db.session.commit()

        book = Book(id=107, name="test name 7", isbn="test isbn 7", count=3,
                     publisher="test publisher 7", pages=701, genre_id=106)
        db.session.add(book)
        db.session.commit()

        review = Review(id=105, user_id=108, book_id=107, message="test message 5")
        db.session.add(review)
        db.session.commit()

        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'image.jpg'), 'rb') as image:
            file_data = BytesIO(image.read())

        request = client.post('/reviews/105/review-images',
                              content_type='multipart/form-data',
                              headers={"Authorization": jwt_token},
                              data={"file": (file_data, 'image.jpg')})

        request_data = request.get_json(force=True)
        review_image = ReviewImage.query.filter_by(review_id=105).first()

        assert request_data.get('image') == f'review_images\\105\\{review_image.id}\\image.jpg'
        assert request.status_code == 200

    def test_add_new_review_image_fail_without_image(self, initialize, client, jwt_token):
        expected_exception_message = 'File didn`t found.'
        request = client.post('/reviews/105/review-images',
                              content_type='multipart/form-data',
                              headers={
                                  "Authorization": jwt_token
                              },
                              data={'': ''})

        request_data = request.get_json(force=True)

        assert request_data.get('exception') == expected_exception_message
        assert request.status_code == 400

    def test_update_review_image(self, initialize, client, jwt_token):
        review_image = ReviewImage.query.filter_by(review_id=105).first()
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'image2.jpg'), 'rb') as image:
            file_data = BytesIO(image.read())

        request = client.put(f'/reviews/105/review-images/{review_image.id}',
                             content_type='multipart/form-data',
                             headers={"Authorization": jwt_token},
                             data={"file": (file_data, 'image2.jpg')})

        request_data = request.get_json(force=True)

        assert request_data.get('image') == f'review_images\\105\\{review_image.id}\\image2.jpg'
        assert request.status_code == 200

    def test_update_review_image_fail_without_image(self, initialize, client, jwt_token):
        review_image = ReviewImage.query.filter_by(review_id=105).first()
        expected_exception_message = 'File didn`t found.'
        request = client.put(f'/reviews/105/review-images/{review_image.id}',
                             headers={
                                 "Authorization": jwt_token
                             })

        request_data = request.get_json(force=True)

        assert request_data.get('exception') == expected_exception_message
        assert request.status_code == 400

    def test_delete_review_image(self, initialize, client, jwt_token):
        expected_message = 'You successfully deleted the review image!'
        review_image = ReviewImage.query.filter_by(review_id=105).first()
        request = client.delete(f'/reviews/105/review-images/{review_image.id}',
                                headers={
                                    "Authorization": jwt_token
                                })

        genre = Genre.query.filter_by(id=106).first()
        user = User.query.filter_by(id=108).first()

        db.session.delete(genre)
        db.session.delete(user)
        db.session.commit()

        request_data = request.get_json(force=True)

        assert request_data.get('success') == expected_message
        assert request.status_code == 200