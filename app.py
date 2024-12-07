from flask import Flask, jsonify

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

@app.route("/") # Это первый URL, который мы будем обрабатывать
def hello_world(): # Функция обработчик будет вызвана при запросе этого URL
    return "Hello, World!"

@app.route ("/about")
def about():
    return about_me

@app.route ("/quotes")
def get_quotes():
    return quotes

#@app.route ("/quotes/<int:quotes_id>")
#def quotes(quotes_id):
    #return 'Quote %d' % quotes_id

if __name__ == "__main__":
    app.run(debug=True)