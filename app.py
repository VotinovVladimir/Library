from flask import Flask, render_template

# 1. Создание Flask-приложения
app = Flask(__name__)


# 2. Маршрут /
@app.route("/")
def index():
    # 3. Отображение главной страницы
    return render_template("index.html")


# 4. Запуск локального сервера
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)