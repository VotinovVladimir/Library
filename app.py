
import os

from flask import Flask, render_template

from database import db
from models import Author, Book, Reader, Loan


app = Flask(__name__, instance_relative_config=True)

# Создаём папку instance, если её нет
os.makedirs(app.instance_path, exist_ok=True)

# Настройки базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Подключаем базу данных к Flask
db.init_app(app)


# Главная страница
@app.route('/')
def index():
    return render_template('index.html')


# Создание таблиц
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
