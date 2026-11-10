
from datetime import date, timedelta

from app import app
from database import db
from models import Author, Book, Reader, Loan


with app.app_context():

    # Не добавляем данные повторно
    if Author.query.first():
        print("Тестовые данные уже существуют.")
    else:

        # 1. Авторы
        authors = [
            Author(full_name="Фёдор Достоевский", birth_year=1821),
            Author(full_name="Лев Толстой", birth_year=1828),
            Author(full_name="Александр Пушкин", birth_year=1799),
            Author(full_name="Михаил Булгаков", birth_year=1891),
            Author(full_name="Антон Чехов", birth_year=1860)
        ]

        db.session.add_all(authors)
        db.session.flush()

        # 2. Книги
        books = [
            Book(author=authors[0], title="Преступление и наказание",
                 isbn="978-5-17-090123-4", year=1866, quantity=5),

            Book(author=authors[0], title="Идиот",
                 isbn="978-5-17-090124-1", year=1869, quantity=4),

            Book(author=authors[1], title="Война и мир",
                 isbn="978-5-17-090125-8", year=1869, quantity=6),

            Book(author=authors[1], title="Анна Каренина",
                 isbn="978-5-17-090126-5", year=1877, quantity=4),

            Book(author=authors[2], title="Евгений Онегин",
                 isbn="978-5-17-090127-2", year=1833, quantity=3),

            Book(author=authors[2], title="Капитанская дочка",
                 isbn="978-5-17-090128-9", year=1836, quantity=3),

            Book(author=authors[3], title="Мастер и Маргарита",
                 isbn="978-5-17-090129-6", year=1967, quantity=5),

            Book(author=authors[3], title="Собачье сердце",
                 isbn="978-5-17-090130-2", year=1925, quantity=4),

            Book(author=authors[4], title="Вишнёвый сад",
                 isbn="978-5-17-090131-9", year=1904, quantity=3),

            Book(author=authors[4], title="Палата № 6",
                 isbn="978-5-17-090132-6", year=1892, quantity=3)
        ]

        db.session.add_all(books)

        # 3. Читатели
        readers = [
            Reader(full_name="Иванов Иван Иванович",
                   phone="+79991112233", email="ivanov@mail.ru"),

            Reader(full_name="Петров Пётр Петрович",
                   phone="+79992223344", email="petrov@mail.ru"),

            Reader(full_name="Сидоров Сергей Сергеевич",
                   phone="+79993334455", email="sidorov@mail.ru"),

            Reader(full_name="Смирнова Анна Викторовна",
                   phone="+79994445566", email="smirnova@mail.ru"),

            Reader(full_name="Кузнецов Алексей Андреевич",
                   phone="+79995556677", email="kuznetsov@mail.ru")
        ]

        db.session.add_all(readers)
        db.session.flush()

        # 4. Выдачи
        today = date.today()

        loans = [
            Loan(
                book=books[0],
                reader=readers[0],
                issue_date=today,
                due_date=today + timedelta(days=14)
            ),
            Loan(
                book=books[2],
                reader=readers[0],
                issue_date=today,
                due_date=today + timedelta(days=14)
            ),
            Loan(
                book=books[6],
                reader=readers[1],
                issue_date=today - timedelta(days=20),
                due_date=today - timedelta(days=6)
            ),
            Loan(
                book=books[4],
                reader=readers[2],
                issue_date=today - timedelta(days=5),
                due_date=today + timedelta(days=9),
                return_date=today
            )
        ]

        db.session.add_all(loans)

        # Сохраняем все изменения
        db.session.commit()

        print("Тестовые данные успешно добавлены!")
