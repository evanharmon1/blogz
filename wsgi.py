from flask import Flask
from app import app

@app.route('/')
def hello():
    return '<h1>Hello There!</h1>'

@app.route('/test')
def goodbye():
    return '<h1>Goodbye there!</h1>'

if __name__ == "__main__":
    app.run()
