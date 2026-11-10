
from database import db
from datetime import date


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    birth_year = db.Column(db.Integer)

    # Связь с книгами
    books = db.relationship('Book', back_populates='author')

    def __repr__(self):
        return f'<Author {self.full_name}>'

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)

    author_id = db.Column(
        db.Integer,
        db.ForeignKey('authors.id'),
        nullable=False
    )

    title = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    year = db.Column(db.Integer)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Связь с автором
    author = db.relationship('Author', back_populates='books')

    # Связь с выдачами
    loans = db.relationship('Loan', back_populates='book')

    def __repr__(self):
        return f'<Book {self.title}>'


class Reader(db.Model):
    __tablename__ = 'readers'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    registration_date = db.Column(
        db.Date,
        nullable=False,
        default=date.today
    )

    # Связь с выдачами
    loans = db.relationship('Loan', back_populates='reader')

    def __repr__(self):
        return f'<Reader {self.full_name}>'



class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True)

    book_id = db.Column(
        db.Integer,
        db.ForeignKey('books.id'),
        nullable=False
    )

    reader_id = db.Column(
        db.Integer,
        db.ForeignKey('readers.id'),
        nullable=False
    )

    issue_date = db.Column(
        db.Date,
        nullable=False,
        default=date.today
    )

    due_date = db.Column(db.Date, nullable=False)

    return_date = db.Column(db.Date)

    # Связь с книгой
    book = db.relationship('Book', back_populates='loans')

    # Связь с читателем
    reader = db.relationship('Reader', back_populates='loans')

    def __repr__(self):
        return f'<Loan {self.id}>'

