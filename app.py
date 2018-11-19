from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://evan:Csodmf132$@localhost/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "\x179\x93$8y\xddJw\xd0\xfc*\xa97\xb5\x8eA\t\xeaKNr\xd4]"
db = SQLAlchemy(app)
