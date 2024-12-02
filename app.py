from flask import Flask

app = Flask(__name__)

about_me = {
    "name": "Максим",
    "surname": "Чеснов",
    "email":"machesnov@gmail.com"
}

@app.route("/") # Это первый URL, который мы будем обрабатывать
def hello_world(): # Функция обработчик будет вызвана при запросе этого URL
    return "Hello, World!"

@app.route ("/about")
def about():
    return about_me

if __name__ == "__main__":
    app.run(debug=True)