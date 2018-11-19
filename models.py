from app import db
from hashutils import make_pw_hash, make_salt, check_pw_hash
from datetime import datetime


# Class for blog post with automatic datetime added at creation
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.Text)
    date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, owner):
        self.title = title
        self.date = datetime.utcnow()
        self.owner = owner # user object

    def __repr__(self):
        return '<Blog %r>' % self.title


# Class for users - relation to Blog class
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    pw_hash = db.Column(db.String(100))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, pw_hash):
        self.username = username
        self.pw_hash = pw_hash

    def __repr__(self):
        return '<User %r>' % self.username
