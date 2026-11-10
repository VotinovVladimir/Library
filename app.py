
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


# Создание таблиц
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
