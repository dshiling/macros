from macros.extensions import db
from datetime import datetime


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    username = db.Column(db.String(120))
    email = db.Column(db.String(120))
    macros = db.relationship('Macro', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.username


class Macro(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(120))
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Macro %r>' % self.title
