import pytest
from library import bcrypt
from library.models import Genre, Author, Book, \
    User, Order, OrderItem, Review, ReviewImage
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def initialize(session):
    genre = Genre(id=101, name='comedy')

    author1 = Author(id=101, firstname="test firstname 1", lastname="test lastname 1",
                     biography="test biography 1")
    author2 = Author(id=102, firstname="test firstname 2", lastname="test lastname 2",
                     biography="test biography 2")

    user = User(id=101, username="test username 1", firstname="test firstname 1",
                lastname="test lastname 1")

    user.password = 'test password 1'

    session.add_all([genre, author1, author2, user])
    session.commit()

    book1 = Book(id=101, name="test name 1", isbn="test isbn 1", count=3,
                 publisher="test publisher 1", pages=101, genre_id=101)
    book2 = Book(id=102, name="test name 2", isbn="test isbn 2", count=3,
                 publisher="test publisher 2", pages=201, genre_id=101)
    book3 = Book(id=103, name="test name 3", isbn="test isbn 3", count=3,
                 publisher="test publisher 3", pages=301, genre_id=101)

    session.add_all([book1, book2, book3])
    session.commit()

    author1.books.append(book1)
    author2.books.append(book2)
    author1.books.append(book3)
    author2.books.append(book3)

    order1 = Order(id=101, user_id=101)
    order2 = Order(id=102, user_id=101)

    review1 = Review(id=101, user_id=101, book_id=101, message="test message 1")
    review2 = Review(id=102, user_id=101, book_id=102, message="test message 2")

    session.add_all([author1, author2, order1, order2, review1, review2])
    session.commit()

    order_item1 = OrderItem(id=101, order_id=101, book_id=101,
                            books_amount=3)
    order_item2 = OrderItem(id=102, order_id=101, book_id=102)
    order_item3 = OrderItem(id=103, order_id=102, book_id=102,
                            books_amount=2)

    review_image1 = ReviewImage(id=101, review_id=101, image="review_image1.jpg")
    review_image2 = ReviewImage(id=102, review_id=101, image="review_image2.jpg")
    review_image3 = ReviewImage(id=103, review_id=102, image="review_image3.jpg")

    session.add_all([order_item1, order_item2, order_item3,
                     review_image1, review_image2, review_image3])
    session.commit()


class TestAuthor:

    def test_get_info(self, session, initialize):
        expected_author = {
            'id': 101,
            'firstname': 'test firstname 1',
            'lastname': 'test lastname 1',
            'biography': 'test biography 1'
        }

        author = session.query(Author).filter_by(id=101).first()
        author_to_dict = {
            'id': author.id,
            'firstname': author.firstname,
            'lastname': author.lastname,
            'biography': author.biography
        }

        assert author_to_dict == expected_author

    def test_get_amount_of_authors(self, session, initialize):
        authors = session.query(Author).all()

        assert len(authors) == 2

    def test_get_books(self, session, initialize):
        expected_books = [session.query(Book).filter_by(id=102).first(),
                          session.query(Book).filter_by(id=103).first()]

        author_books = session.query(Author).filter_by(id=102).first().books

        assert author_books == expected_books

    def test_get_default_values(self, session, initialize):
        expected_values = {
            'picture': None,
            'country': None,
            'city': None,
            'rating': 0,
            'birthday': None
        }

        author = session.query(Author).filter_by(id=102).first()
        author_default_values_to_dict = {
            'picture': author.picture,
            'country': author.country,
            'city': author.city,
            'rating': author.rating.value,
            'birthday': author.birthday
        }

        assert author_default_values_to_dict == expected_values


class TestBook:

    def test_get_info(self, session, initialize):
        expected_book = {
            'id': 101,
            'name': 'test name 1',
            'isbn': 'test isbn 1',
            'count': 3,
            'publisher': 'test publisher 1',
            'pages': 101
        }

        book = session.query(Book).filter_by(id=101).first()
        book_to_dict = {
            'id': book.id,
            'name': book.name,
            'isbn': book.isbn,
            'count': book.count,
            'publisher': book.publisher,
            'pages': book.pages
        }

        assert book_to_dict == expected_book

    def test_get_genre_id(self, session, initialize):
        book = session.query(Book).filter_by(id=102).first()

        assert book.genre_id == 101

    def test_get_amount_of_books(self, session, initialize):
        books = session.query(Book).all()

        assert len(books) == 3

    def test_get_default_values(self, session, initialize):
        expected_values = {
            'picture': None,
            'description': None,
            'cover': 'paperbook',
            'status': 'available',
            'rating': 0,
            'format': 'e-book'
        }

        book = session.query(Book).filter_by(id=101).first()
        book_default_values_to_dict = {
            'picture': book.picture,
            'description': book.description,
            'cover': book.cover.value,
            'status': book.status.value,
            'rating': book.rating.value,
            'format': book.format.value
        }

        assert book_default_values_to_dict == expected_values

    def test_will_throw_error_on_create_count_negative(self, session, initialize):
        with pytest.raises(AssertionError):
            Book(id=104, name="test name 4", isbn="test isbn 4", count=-1,
                 publisher="test publisher 4", pages=401, genre_id=101)

    def test_will_throw_error_on_update_count_negative(self, session, initialize):
        with pytest.raises(AssertionError):
            book3 = session.query(Book).filter_by(id=103).first()
            book3.count = -3


class TestUser:

    def test_get_info(self, session, initialize):
        expected_user = {
            'id': 101,
            'username': 'test username 1',
            'firstname': 'test firstname 1',
            'lastname': 'test lastname 1'
        }

        user = session.query(User).filter_by(id=101).first()
        user_to_dict = {
            'id': user.id,
            'username': user.username,
            'firstname': user.firstname,
            'lastname': user.lastname
        }

        assert user_to_dict == expected_user

    def test_password_get(self, session, initialize):
        user = session.query(User).filter_by(id=101).first()

        assert user.password == user._User__password

    def test_check_password_hash(self, session, initialize):
        expected_password = 'test password 1'
        user = session.query(User).filter_by(id=101).first()

        assert bcrypt.check_password_hash(user._User__password, expected_password)

    def test_check_password_hash_method(self, session, initialize):
        expected_password = 'test password 1'
        user = session.query(User).filter_by(id=101).first()

        assert user.check_password(expected_password)

    def test_get_amount_of_users(self, session, initialize):
        users = session.query(User).all()

        assert len(users) == 1

    def test_get_orders(self, session, initialize):
        expected_orders = session.query(Order).all()

        user_orders = session.query(User).filter_by(id=101).first().orders

        assert user_orders == expected_orders

    def test_get_reviews(self, session, initialize):
        expected_reviews = session.query(Review).all()

        user_reviews = session.query(User).filter_by(id=101).first().reviews

        assert user_reviews == expected_reviews

    def test_get_default_values(self, session, initialize):
        expected_values = {
            'picture': None,
            'email': None,
            'country': None,
            'city': None,
            'birthday': None,
            'role': 0
        }

        user = session.query(User).filter_by(id=101).first()
        user_default_values_to_dict = {
            'picture': user.picture,
            'email': user.email,
            'country': user.country,
            'city': user.city,
            'birthday': user.birthday,
            'role': user.role.value
        }

        assert user_default_values_to_dict == expected_values

    def test_will_throw_error_on_create_email_negative(self, session, initialize):
        with pytest.raises(AssertionError):
            User(id=102, username="test username 2", email="incorrect email", firstname="test firstname 2",
                 lastname="test lastname 2")

    def test_will_throw_error_on_update_email_negative(self, session, initialize):
        with pytest.raises(AssertionError):
            user = session.query(User).filter_by(id=101).first()
            user.email = "incorrect email"

    def test_will_throw_error_on_create_username_already_exist(self, session, initialize):
        with pytest.raises(IntegrityError):
            user3 = User(id=103, username="test username 2", firstname="test firstname 3",
                 lastname="test lastname 3")

            session.add(user3)
            session.commit()


class TestOrder:

    def test_get_info(self, session, initialize):
        expected_order = {
            'id': 101,
            'user_id': 101
        }

        order = session.query(Order).filter_by(id=101).first()
        order_to_dict = {
            'id': order.id,
            'user_id': order.user_id
        }

        assert order_to_dict == expected_order

    def test_get_amount_of_orders(self, session, initialize):
        orders = session.query(Order).all()

        assert len(orders) == 2

    def test_get_order_items(self, session, initialize):
        expected_order_items = [session.query(OrderItem).filter_by(id=103).first()]

        order_items = session.query(Order).filter_by(id=102).first().items

        assert order_items == expected_order_items

    def test_get_amount_of_order_items(self, session, initialize):
        order_items = session.query(Order).filter_by(id=101).first().items

        assert len(order_items) == 2

    def test_get_amount_of_books_in_order_item(self, session, initialize):
        order1 = session.query(Order).filter_by(id=101).first()

        order_item1 = order1.items[0]
        order_item2 = order1.items[1]

        assert order_item1.books_amount == 3
        assert order_item2.books_amount == 1


class TestOrderItem:

    def test_get_info(self, session, initialize):
        expected_order_item = {
            'id': 101,
            'order_id': 101,
            'book_id': 101,
            'books_amount': 3
        }

        order_item = session.query(OrderItem).filter_by(id=101).first()
        order_item_to_dict = {
            'id': order_item.id,
            'order_id': order_item.order_id,
            'book_id': order_item.book_id,
            'books_amount': order_item.books_amount
        }

        assert order_item_to_dict == expected_order_item

    def test_get_amount_of_orders(self, session, initialize):
        order_items = session.query(OrderItem).all()

        assert len(order_items) == 3

    def test_get_default_values(self, session, initialize):
        expected_values = {
            'books_amount': 1,
            'status': 'in progress'
        }

        order_item = session.query(OrderItem).filter_by(id=102).first()
        order_item_default_values_to_dict = {
            'books_amount': order_item.books_amount,
            'status': order_item.status.value
        }

        assert order_item_default_values_to_dict == expected_values


class TestReview:

    def test_get_info(self, session, initialize):
        expected_review = {
            'id': 102,
            'user_id': 101,
            'book_id': 102,
            'message': 'test message 2'
        }

        review = session.query(Review).filter_by(id=102).first()
        review_to_dict = {
            'id': review.id,
            'user_id': review.user_id,
            'book_id': review.book_id,
            'message': review.message
        }

        assert review_to_dict == expected_review

    def test_get_amount_of_reviews(self, session, initialize):
        reviews = session.query(Review).all()

        assert len(reviews) == 2

    def test_get_review_images(self, session, initialize):
        expected_review_images = [session.query(ReviewImage).filter_by(id=101).first(),
                                  session.query(ReviewImage).filter_by(id=102).first()]

        review = session.query(Review).filter_by(id=101).first().images

        assert review == expected_review_images


class TestReviewImage:

    def test_get_info(self, session, initialize):
        expected_review_image = {
            'id': 101,
            'review_id': 101,
            'image': 'review_image1.jpg'
        }

        review_image = session.query(ReviewImage).filter_by(id=101).first()
        review_image_to_dict = {
            'id': review_image.id,
            'review_id': review_image.review_id,
            'image': review_image.image
        }

        assert review_image_to_dict == expected_review_image

    def test_get_amount_of_reviews_images(self, session, initialize):
        reviews = session.query(ReviewImage).all()

        assert len(reviews) == 3
