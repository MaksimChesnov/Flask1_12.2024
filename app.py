from typing import Any
from flask import Flask, jsonify, request
from random import choice

app = Flask(__name__)

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

@app.route("/") # Это первый URL, который мы будем обрабатывать
def hello_world(): # Функция обработчик будет вызвана при запросе этого URL
    return "Hello, World!"

@app.route ("/about")
def about():
    return about_me

@app.route ("/quotes")
def get_all_quotes():
    return quotes

#Как подставлять динамические переменные
#Вариант 1.Попроще.Возвращает значение,которое было введено
@app.route ("/params/<value>")
def param_example (value):
    return jsonify(param=value)

#Вариант 2.Сложнее.Возвращает цитаты
@app.route ("/quotes/<int:quote_id>")
def get_quotes(quote_id):
    for quote in quotes:
        if quote["id"] == quote_id:
            return jsonify(quote), 200
    return {"error": f"Quote with id {quote_id} not found"}, 404

#Количество цитат
@app.get("/quotes/count")
def quotes_count():
    return jsonify(count=len(quotes))

#Случайная цитата
@app.route("/quotes/random", methods=["GET"])
def quote_random() -> dict:
    return jsonify(choice(quotes))


#Метод POST1
#@app.route("/quotes", methods=['POST'])
#def create_quote():
 #  data = request.json
 #  print("data = ", data)  
 #  print ("max=", (max(quotes["id"])))
 #  return {}, 201

#Метод POST2. Функция создает новую цитату в списке цитат.
@app.route("/quotes", methods=['POST'])
def create_quote():
    new_quote = request.json
    last_quote = quotes [-1]
    new_id = last_quote["id"] + 1
    new_quote["id"] = new_id
    quotes.append(new_quote)
    return {}, 201

#Метод DELETE
#Удаление цитаты по id
@app.route ("/quotes/<int:quote_id>", methods = ["DELETE"])
def delete_quote(quote_id:int):
    for quote in quotes:
        if quote["id"] == quote_id:
            quotes.remove(quote)
            return ({"message": f"Quote with id={quote_id} has deleted"}), 200
    return {"error": f"Quote with id {quote_id} not found"}, 404

if __name__ == "__main__":
    app.run(debug=True)