from flask_restful import Resource
from marshmallow import validate
from flask import request, jsonify, session
from werkzeug.security import check_password_hash
from models import User as dbUSer, Role as dbRole
from sqlalchemy.exc import NoResultFound
from flask_jwt_extended import create_access_token, jwt_required, decode_token
import datetime
from models import db


def is_admin(func):
    def wrapper(*args, **kwargs):
        public_id = session['public_id']
        if public_id is None:
            return {'success': False, 'msg': 'Необходимо авторизоваться'}
        query_user = dbUSer.query.filter_by(public_id=public_id).one()
        if query_user.role.name == dbRole.query.filter_by(name='Admin').one().name:
            return func(*args, **kwargs)

        return {'success': False, 'msg': 'Вы не являетесь администратором'}

    return wrapper


def validator_user_data(func):
    def wrapper(*args, **kwargs):
        params = request.json

        if params.get('email') is None or params.get('psw') is None or params.get('name') is None:
            return {'success': False, 'msg': 'Переданы не все поля'}
        email = params.get('email')
        psw = params.get('psw')
        name = params.get('name')
        if len(dbUSer.query.filter_by(email=email).all()) != 0:
            return {'success': False, 'msg': 'Email существует'}
        try:
            validate.Email()(email)
        except Exception as ex:
            return {'success': False, 'msg': 'Не валидный email'}
        if len(psw) < 6:
            return {'success': False, 'msg': 'Пароль должен быть более 6-ти символов'}
        if len(name) < 3:
            return {'success': False, 'msg': 'Имя должно содержать более 2-х символов'}

        return func(*args, **kwargs)

    return wrapper


class UserRegistration(Resource):
    @validator_user_data
    def post(self):
        params = request.json
        try:
            user = dbUSer(**params)
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'msg': 'Произошла внутрення ошибка'}, 400
        return {'success': True}


class UserLogin(Resource):
    def post(self):
        auth = request.authorization

        user = dbUSer.query.filter_by(email=auth.username).first()

        if not user or not check_password_hash(user.psw, auth.password):
            return jsonify({'success': False, 'msg': 'Неверно введенный логин и/или пароль'})

        exp_time = datetime.timedelta(minutes=300)
        return {'access_token': create_access_token(user.public_id, expires_delta=exp_time)}


class Users(Resource):

    # @is_admin
    @jwt_required()
    def get(self):
        users = dbUSer.query.all()
        result = {}
        for i in users:
            result[i.email] = {'name': i.name,
                               'role': i.role.name,
                               'departament': i.departament,
                               'public_id': i.public_id,
                               'foto_url': i.foto_url}
        return result


class User(Resource):
    def __init__(self):
        public_id = session['public_id']
        self.query_user = dbUSer.query.filter_by(public_id=public_id).one() if public_id is not None else None

    @is_admin
    def get(self):
        params = request.json
        email = params['email']
        find_user = dbUSer.query.filter_by(email=email).one()
        res = {find_user.email: {
            'name': find_user.name,
            'role': find_user.role.name,
            'departament': find_user.departament,
            'public_id': find_user.public_id,
            'foto_url': find_user.foto_url
        }}
        return res

    @jwt_required()
    def put(self):
        admin = dbRole.query.filter_by(name='Admin').one()
        email = request.json['email']
        name = request.json['name']
        if email != self.query_user.email:
            if admin != self.query_user.role:
                return {'success': False, 'msg': 'Нет прав для изменения другого пользователя'}

        self.query_user.name = name
        db.session.commit()

        return {'success': True}

    @jwt_required()
    @is_admin
    @validator_user_data
    def post(self):
        params = request.json
        try:
            user = dbUSer(**params)
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'msg': 'Произошла внутрення ошибка'}, 400
        return {'success': True}

    @jwt_required()
    # @is_admin
    # @validator_user_data
    def delete(self):
        print(request.json['email'])
        params = request.json
        try:
            del_user = dbUSer.query.filter_by(email=params['email']).one()
        except NoResultFound as e:
            return {'success': False, 'msg': 'Пользователь с таким email не найден'}
        db.session.delete(del_user)
        db.session.commit()
        return {'success': True}


class Index(Resource):
    def post(self):
        email = request.json['email']
        res = validate.Email(error='123123')(email)
        return {'index': res}
