
import os

from flask import Flask, render_template, request, redirect, url_for, flash

from database import db
from models import Author, Book, Reader, Loan


app = Flask(__name__, instance_relative_config=True)

os.makedirs(app.instance_path, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'library-development-key'

db.init_app(app)


# Главная страница
@app.route('/')
def index():
    return render_template('index.html')


# Список читателей
@app.route('/readers')
def readers():
    all_readers = Reader.query.order_by(Reader.full_name).all()
    return render_template('readers.html', readers=all_readers)


# Добавление читателя
@app.route('/readers/add', methods=['GET', 'POST'])
def add_reader():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()

        if not full_name:
            flash('Введите ФИО читателя.', 'error')
            return render_template('reader_form.html', reader=None)

        reader = Reader(
            full_name=full_name,
            phone=phone or None,
            email=email or None
        )

        db.session.add(reader)
        db.session.commit()

        flash('Читатель успешно добавлен.', 'success')
        return redirect(url_for('readers'))

    return render_template('reader_form.html', reader=None)


# Редактирование читателя
@app.route('/readers/edit/<int:reader_id>', methods=['GET', 'POST'])
def edit_reader(reader_id):
    reader = db.get_or_404(Reader, reader_id)

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()

        if not full_name:
            flash('Введите ФИО читателя.', 'error')
            return render_template('reader_form.html', reader=reader)

        reader.full_name = full_name
        reader.phone = request.form.get('phone', '').strip() or None
        reader.email = request.form.get('email', '').strip() or None

        db.session.commit()

        flash('Данные читателя обновлены.', 'success')
        return redirect(url_for('readers'))

    return render_template('reader_form.html', reader=reader)


# Удаление читателя
@app.route('/readers/delete/<int:reader_id>', methods=['POST'])
def delete_reader(reader_id):
    reader = db.get_or_404(Reader, reader_id)

    # Проверяем наличие истории выдач
    loan = Loan.query.filter_by(reader_id=reader.id).first()

    if loan:
        flash(
            'Нельзя удалить читателя: в системе есть история его выдач.',
            'error'
        )
        return redirect(url_for('readers'))

    db.session.delete(reader)
    db.session.commit()

    flash('Читатель удалён.', 'success')
    return redirect(url_for('readers'))


# Список книг
@app.route('/books')
def books():
    all_books = Book.query.order_by(Book.title).all()

    books_data = []

    for book in all_books:
        issued = sum(
            1 for loan in book.loans
            if loan.return_date is None
        )

        books_data.append({
            'book': book,
            'issued': issued,
            'available': book.quantity - issued
        })

    return render_template('books.html', books=books_data)


# Добавление книги
@app.route('/books/add', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.order_by(Author.full_name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        isbn = request.form.get('isbn', '').strip() or None

        try:
            author_id = int(request.form.get('author_id', ''))
            quantity = int(request.form.get('quantity', ''))
            year_text = request.form.get('year', '').strip()
            year = int(year_text) if year_text else None
        except ValueError:
            flash('Проверьте автора, год издания и количество экземпляров.', 'error')
            return render_template(
                'book_form.html',
                book=None,
                authors=authors,
                form_data=request.form
            )

        author = db.session.get(Author, author_id)

        if not title:
            flash('Введите название книги.', 'error')
        elif author is None:
            flash('Выберите существующего автора.', 'error')
        elif quantity < 1:
            flash('Количество экземпляров должно быть не меньше 1.', 'error')
        elif year is not None and year < 0:
            flash('Год издания указан некорректно.', 'error')
        elif isbn and Book.query.filter_by(isbn=isbn).first():
            flash('Книга с таким ISBN уже существует.', 'error')
        else:
            book = Book(
                title=title,
                author_id=author_id,
                isbn=isbn,
                year=year,
                quantity=quantity
            )

            db.session.add(book)
            db.session.commit()

            flash('Книга успешно добавлена.', 'success')
            return redirect(url_for('books'))

        return render_template(
            'book_form.html',
            book=None,
            authors=authors,
            form_data=request.form
        )

    return render_template(
        'book_form.html',
        book=None,
        authors=authors,
        form_data=None
    )


# Редактирование книги
@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = db.get_or_404(Book, book_id)
    authors = Author.query.order_by(Author.full_name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        isbn = request.form.get('isbn', '').strip() or None

        try:
            author_id = int(request.form.get('author_id', ''))
            quantity = int(request.form.get('quantity', ''))
            year_text = request.form.get('year', '').strip()
            year = int(year_text) if year_text else None
        except ValueError:
            flash('Проверьте автора, год издания и количество экземпляров.', 'error')
            return render_template(
                'book_form.html',
                book=book,
                authors=authors,
                form_data=request.form
            )

        author = db.session.get(Author, author_id)

        issued = sum(
            1 for loan in book.loans
            if loan.return_date is None
        )

        duplicate_isbn = Book.query.filter(
            Book.isbn == isbn,
            Book.id != book.id
        ).first() if isbn else None

        if not title:
            flash('Введите название книги.', 'error')
        elif author is None:
            flash('Выберите существующего автора.', 'error')
        elif quantity < 1:
            flash('Количество экземпляров должно быть не меньше 1.', 'error')
        elif quantity < issued:
            flash(
                f'Нельзя установить количество меньше {issued}: столько экземпляров сейчас на руках.',
                'error'
            )
        elif year is not None and year < 0:
            flash('Год издания указан некорректно.', 'error')
        elif duplicate_isbn:
            flash('Книга с таким ISBN уже существует.', 'error')
        else:
            book.title = title
            book.author_id = author_id
            book.isbn = isbn
            book.year = year
            book.quantity = quantity

            db.session.commit()

            flash('Данные книги обновлены.', 'success')
            return redirect(url_for('books'))

        return render_template(
            'book_form.html',
            book=book,
            authors=authors,
            form_data=request.form
        )

    return render_template(
        'book_form.html',
        book=book,
        authors=authors,
        form_data=None
    )


# Удаление книги
@app.route('/books/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = db.get_or_404(Book, book_id)

    # Проверяем наличие истории выдач
    loan = Loan.query.filter_by(book_id=book.id).first()

    if loan:
        flash(
            'Нельзя удалить книгу: в системе есть история её выдач.',
            'error'
        )
        return redirect(url_for('books'))

    db.session.delete(book)
    db.session.commit()

    flash('Книга удалена.', 'success')
    return redirect(url_for('books'))



# Создание таблиц
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
