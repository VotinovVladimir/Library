
from app import app
from models import Author, Book, Reader, Loan


with app.app_context():

    print("\n=== ПРОВЕРКА БАЗЫ ДАННЫХ ===")

    print("Авторы:", Author.query.count())
    print("Книги:", Book.query.count())
    print("Читатели:", Reader.query.count())
    print("Выдачи:", Loan.query.count())

    print("\n=== СПИСОК КНИГ ===")

    for book in Book.query.all():
        issued = sum(
            1 for loan in book.loans
            if loan.return_date is None
        )

        available = book.quantity - issued

        print(
            f"{book.title} | "
            f"Автор: {book.author.full_name} | "
            f"Всего: {book.quantity} | "
            f"На руках: {issued} | "
            f"Свободно: {available}"
        )

    print("\n=== КНИГИ ЧИТАТЕЛЕЙ ===")

    for reader in Reader.query.all():
        active_loans = [
            loan for loan in reader.loans
            if loan.return_date is None
        ]

        print(
            f"{reader.full_name}: "
            f"{len(active_loans)} книг на руках"
        )
