
import os

from datetime import date, timedelta

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
    search = request.args.get('search', '').strip().casefold().replace('ё', 'е')

    all_books = Book.query.order_by(Book.title).all()

    # Поиск без учёта регистра, включая кириллицу
    if search:
        all_books = [
            book for book in all_books
            if search in book.title.casefold().replace('ё', 'е')
               or search in book.author.full_name.casefold().replace('ё', 'е')
               or search in (book.isbn or '').casefold().replace('ё', 'е')
        ]

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

    return render_template(
        'books.html',
        books=books_data,
        search=request.args.get('search', '').strip()
    )




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


# Список выдач и история возвратов
@app.route('/loans')
def loans():
    all_loans = Loan.query.order_by(
        Loan.issue_date.desc(),
        Loan.id.desc()
    ).all()

    today = date.today()

    return render_template(
        'loans.html',
        loans=all_loans,
        today=today
    )


# Выдача книги
@app.route('/loans/add', methods=['GET', 'POST'])
def add_loan():
    readers_list = Reader.query.order_by(Reader.full_name).all()
    books_list = Book.query.order_by(Book.title).all()

    today = date.today()
    default_due_date = today + timedelta(days=14)

    if request.method == 'POST':
        try:
            reader_id = int(request.form.get('reader_id', ''))
            book_id = int(request.form.get('book_id', ''))
            due_date = date.fromisoformat(
                request.form.get('due_date', '')
            )
        except (ValueError, TypeError):
            flash('Проверьте выбранного читателя, книгу и дату возврата.', 'error')
            return render_template(
                'loan_form.html',
                readers=readers_list,
                books=books_list,
                default_due_date=default_due_date,
                today=today,
                form_data=request.form
            )

        reader = db.session.get(Reader, reader_id)
        book = db.session.get(Book, book_id)

        if reader is None:
            flash('Выбранный читатель не найден.', 'error')

        elif book is None:
            flash('Выбранная книга не найдена.', 'error')

        elif due_date < today:
            flash('Дата возврата не может быть в прошлом.', 'error')

        else:
            active_loans = Loan.query.filter_by(
                book_id=book.id,
                return_date=None
            ).count()

            available = book.quantity - active_loans

            if available <= 0:
                flash('Нет свободных экземпляров этой книги.', 'error')

            else:
                # Проверяем, есть ли у читателя эта книга на руках
                existing_loan = Loan.query.filter_by(
                    book_id=book.id,
                    reader_id=reader.id,
                    return_date=None
                ).first()

                if existing_loan:
                    flash(
                        'Этот читатель уже имеет данный экземпляр книги на руках.',
                        'error'
                    )
                else:
                    loan = Loan(
                        book_id=book.id,
                        reader_id=reader.id,
                        issue_date=today,
                        due_date=due_date
                    )

                    db.session.add(loan)
                    db.session.commit()

                    flash('Книга успешно выдана читателю.', 'success')
                    return redirect(url_for('loans'))

        return render_template(
            'loan_form.html',
            readers=readers_list,
            books=books_list,
            default_due_date=default_due_date,
            today=today,
            form_data=request.form
        )

    return render_template(
        'loan_form.html',
        readers=readers_list,
        books=books_list,
        default_due_date=default_due_date,
        today=today,
        form_data=None
    )


# Возврат книги
@app.route('/loans/return/<int:loan_id>', methods=['POST'])
def return_loan(loan_id):
    loan = db.get_or_404(Loan, loan_id)

    if loan.return_date is not None:
        flash('Эта книга уже была возвращена.', 'error')
    else:
        loan.return_date = date.today()
        db.session.commit()

        flash('Возврат книги успешно зарегистрирован.', 'success')

    return redirect(url_for('loans'))


# Создание таблиц
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
