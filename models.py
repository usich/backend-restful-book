from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash
import uuid

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    psw = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    name = db.Column(db.String(200), nullable=False)
    foto_url = db.Column(db.String(500))

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    departament_id = db.Column(db.Integer, db.ForeignKey('departament.id'))

    departament = db.relationship('Departament', backref='user')
    role = db.relationship('Role', backref='user')

    def __init__(self, **kwargs):
        self.email = kwargs.get('email')
        self.public_id = uuid.uuid4()
        self.psw = generate_password_hash(kwargs.get('psw'), method="pbkdf2:sha256")
        self.role_id = Role.query.filter_by(name='User').first().id
        self.name = kwargs.get('name')
        self.departament_id = Departament.query.filter_by(name='default').one().id,
        self.foto_url = 'upload/img_profile/default.jpg'

    def __repr__(self):
        return self.name


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return self.name


class Departament(db.Model):
    __tablename__ = 'departament'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return self.name


'''Articles BEGIN'''


class GroupArticle(db.Model):
    __tablename__ = 'grouparticles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    departament_id = db.Column(db.Integer, db.ForeignKey('departament.id'))

    departament = db.relationship('Departament', backref='grouparticles')


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('grouparticles.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    group = db.relationship('GroupArticle', backref='article')
    user = db.relationship('User', backref='article')

    head = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)


'''Articles END'''
