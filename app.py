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
# Показать все цитаты из БД
@app.route ("/quotes")
def get_all_quotes():  
    quotes_db = db.session.scalars(db.select(QuoteModel)).all()
    quotes = []
    for quote in quotes_db:
        quotes.append(quote.to_dict())
    return jsonify(quotes), 200

# Возвращает цитату по id
@app.route ("/quotes/<int:quote_id>")
def get_quote(quote_id: int) -> dict:
    quote = db.session.get(QuoteModel, quote_id)
    if quote:
        return jsonify(quote.to_dict()), 200
    return {"error": f"Quote with id {quote_id} not found"}, 404

# Фильтр
#@app.route ("/quotes/filter"):


# Метод POST
# Добавление новой цитаты в БД
@app.route("/quotes", methods=['POST'])
def create_quote():
    data = request.json
    new_quote = QuoteModel(data["author"], data["text"], data["rating"])
    db.session.add(new_quote)
    db.session.commit()
    return jsonify(new_quote.to_dict()), 201

# Метод PUT
# Обновление цитаты по id
@app.route ("/quotes/<int:quote_id>", methods = ["PUT"])
def edit_quote(quote_id:int):
    data = request.json
    quote = db.session.get(QuoteModel, quote_id)
    quote.text = data["text"]
    db.session.commit()
    return jsonify(quote.to_dict(), data), HTTPStatus.OK
    
    #return {"error": "Send bad data to update"}, HTTPStatus.BAD_REQUEST
    #return {"error": f"Quote with id {quote_id} not found"}, 404

#Метод DELETE
#Удаление цитаты по id
@app.route ("/quotes/<int:quote_id>", methods = ["DELETE"])
def delete_quote(quote_id:int):
    answer = db.get_or_404(QuoteModel, quote_id)
    if answer:
        db.session.delete(answer);
        db.session.commit()
        return ({"message": f"Quote with id={quote_id} has deleted"}), 200
    return {"error": f"Quote with id {quote_id} not found"}, 404

if __name__ == "__main__":
    app.run(debug=True)