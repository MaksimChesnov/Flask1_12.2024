from typing import Any
from flask import Flask, jsonify, request, g, abort
from random import choice
from http import HTTPStatus
from pathlib import Path #аналог библиотеки OS. Но она ООП
import sqlite3

#Work with ORM
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class Base(DeclarativeBase):
    pass

## Настройки конфигурации 

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config ['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class QuoteModel(db.Model):
    __tablename__ = 'quotes'

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(49))
    text: Mapped[str] = mapped_column(String(358))
    rating: Mapped[int] = mapped_column(default=1)

    def __init__(self, author, text, rating):
        self.author = author
        self.text  = text
        self.rating = rating

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "text": self.text,
            "rating": self.rating
        }

#Какая-то приблуда. Пусть тоже будет
# @app.errorhandler(HTTPException)
# def handle_exception(e):
#     return jsonify({"message": e.description}), e.code


## Логика что будет делать программа при разных URL
    
# Метод GET
@app.route ("/quotes")
def get_all_quotes():  
    quotes_db = db.session.scalars(db.select(QuoteModel)).all()
    quotes = []
    for quote in quotes_db:
        quotes.append(quote.to_dict())
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


#Метод POST. Новая цитата добавляется в БД
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
    app.run(debug=True)