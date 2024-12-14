from typing import Any
from flask import Flask, jsonify, request, g, abort
from random import choice
from http import HTTPStatus
from pathlib import Path #аналог библиотеки OS. Но она ООП
import sqlite3

BASE_DIR = Path(__file__).parent
path_to_db = BASE_DIR / "quotes.db"  # <- тут путь к БД
#path_to_db = "/Projects/Flask1/quotes.db"


app = Flask(__name__)
#app.config ('JSON_AS_ASCII') = False

#Подключение к БД
def get_db():
    db = getattr(g,'_database', None)
    if db is None:
        db = g._database = sqlite3.connect(path_to_db)
    return db

@app.teardown_appcontext
def close_connection():
    db = getattr(g,'_database', None)
    if db is None:
        db.close()

def new_table (name_db: str):
    create_table = """
    CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT NOT NULL,
    text TEXT NOT NULL,
    rating INTEGER NOT NULL
    );
    """
    connection = sqlite3.connect(name_db)
    cursor = connection.cursor()
    cursor.execute(create_table)
    connection.commit()
    cursor.close()
    connection.close()

about_me = {
    "name": "Максим",
    "surname": "Чеснов",
    "email":"machesnov@gmail.com"
}

quotes = [
   {
       "id": 3,
       "author": "Rick Cook",
       "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает."
   },
   {
       "id": 5,
       "author": "Waldi Ravens",
       "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."
   },
   {
       "id": 6,
       "author": "Mosher’s Law of Software Engineering",
       "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."
   },
   {
       "id": 8,
       "author": "Yoggi Berra",
       "text": "В теории, теория и практика неразделимы. На практике это не так."
   }
]


#Метод GET
"""
@app.route("/") # Это первый URL, который мы будем обрабатывать
def hello_world(): # Функция обработчик будет вызвана при запросе этого URL
    return "Hello, World!"

@app.route ("/about")
def about():
    return about_me
"""
    
@app.route ("/quotes")
def get_all_quotes():
    select_quotes = "SELECT * FROM quotes"

    # Подключение в БД
    # Вариант1   
    connection = sqlite3.connect("quotes.db")
    cursor = connection.cursor()

    # Вариант 2
    #cursor = get_db().cursor()

    cursor.execute(select_quotes)

    quotes_db = cursor.fetchall()
    print(f"{quotes=}")
    cursor.close()

    # Закрыть соединение:
    connection.close()

    #Подготовка данных для отправки в правильном формате
    #Необходимо выполнить преобразование 
    # было list[tuple] стало list[dict]
    keys = ("id", "author", "text", "rating")
    quotes = []
    for quote_db in quotes_db:
        quote = dict(zip(keys, quote_db))
        quotes.append (quote)        
    return jsonify(quotes), 200


#Как подставлять динамические переменные
#Вариант 1.Попроще.Возвращает значение,которое было введено
@app.route ("/params/<value>")
def param_example (value):
    return jsonify(param=value)

#Вариант 2.Сложнее.Возвращает цитаты
@app.route ("/quotes/<int:quote_id>")
def get_quote(quote_id: int) -> dict:
    # Функция возвращает цитату по значению ключа quote_id
    select_quote = "SELECT * FROM quotes WHERE id = ?"
    cursor = get_db().cursor()
    cursor.execute(select_quote, (quote_id,))
    quote_db = cursor.fetchone() # Получаем одну запись из БД
    if quote_db:
        keys = ("id", "author", "text", "rating")
        quote = dict(zip(keys, quote_db))
        return jsonify(quote), 200
    return {"error": f"Quote with id {quote_id} not found"}, 404

#Количество цитат
@app.get("/quotes/count")
def quotes_count():
    select_count = "SELECT count(*) as count FROM quotes"
    cursor = get_db().cursor()
    cursor.execute(select_count)
    count = cursor.fetchone()
    if count:
        return jsonify(count=count[0]), 200
    abort(503) # Если что-то пошло не так, пишем ошибку Сервис не доступен

#Случайная цитата
# @app.route("/quotes/random", methods=["GET"])
# def quote_random() -> dict:
#     return jsonify(choice(quotes))

#Filter - не особо понял ТЗ. Разберусь потом.
"""@app.route("/quotes/filter")
def filter_quotes:
    filtered_quotes = quotes.copy()
    for key, value in request.args.items():
"""


#Метод POST1
#@app.route("/quotes", methods=['POST'])
#def create_quote():
 #  data = request.json
 #  print("data = ", data)  
 #  print ("max=", (max(quotes["id"])))
 #  return {}, 201

#Метод POST2. Функция создает новую цитату в списке цитат.
# @app.route("/quotes", methods=['POST'])
# def create_quote():
#     new_quote = request.json
#     last_quote = quotes [-1]
#     new_id = last_quote["id"] + 1
#     new_quote["id"] = new_id
#     #Мы проверяем наличие ключа рейтинг и его валидность (от 1 до 5)
#     rating = new_quote.get("rating")
#     if rating is None or rating not in range(1,6):
#         new_quote["rating"] = 1
#     quotes.append(new_quote)
#     return {}, 201

#Метод POST3. Новая цитата добавляется в БД
@app.route("/quotes", methods=['POST'])
def create_quote():
    new_quote = request.json
    insert_quote = "INSERT INTO quotes (author, text, rating) VALUES (?, ?, ?)"
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(insert_quote, (new_quote["author"], new_quote["text"], new_quote["rating"]))
    answer = cursor.lastrowid
    connection.commit()
    new_quote["id"] = answer
    return jsonify(new_quote), 201


#Метод DELETE
#Удаление цитаты по id
@app.route ("/quotes/<int:quote_id>", methods = ["DELETE"])
def delete_quote(quote_id:int):
    for quote in quotes:
        if quote["id"] == quote_id:
            quotes.remove(quote)
            return ({"message": f"Quote with id={quote_id} has deleted"}), 200
    return {"error": f"Quote with id {quote_id} not found"}, 404

#Метод PUT - Обновление данных
@app.route ("/quotes/<int:quote_id>", methods = ["PUT"])
def edit_quote(quote_id:int):
    new_data = request.json
    if set(new_data.keys()) - set (('author', 'rating', 'text')):
        for quote in quotes:
            if quote["id"] == quote_id:
                if "rating" in new_data and new_data["rating"] not in range(1,6):
                    #Валидируем новое значение рейтинга.В случае успеха, обновляем данные
                    new_data.pop("rating")
                quote.update(new_data)
                return jsonify(quote), HTTPStatus.OK
    else:
        return {"error": "Send bad data to update"}, HTTPStatus.BAD_REQUEST
    return {"error": f"Quote with id {quote_id} not found"}, 404


if __name__ == "__main__":
    new_table("quotes.db")
    app.run(debug=True)