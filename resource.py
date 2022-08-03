from flask_restful import Resource
from flask import request, jsonify
from werkzeug.security import check_password_hash
from models import User as dbUSer, Role as dbRole
from flask_jwt_extended import create_access_token, jwt_required, decode_token
import datetime
from models import db


def is_admin(func):
    def wrapper(*args, **kwargs):
        token = request.headers['Authorization'].split(' ')[1]
        public_id = decode_token(encoded_token=token)['sub']
        query_user = dbUSer.query.filter_by(public_id=public_id).one()

        if query_user.role.name == dbRole.query.filter_by(name='Admin').one().name:
            return func(*args, **kwargs)

        return {'msg': 'Вы не являетесь администратором'}

    return wrapper


class UserRegistration(Resource):
    def post(self):
        params = request.json
        email = params['email']

        if len(dbUSer.query.filter_by(email=email).all()) != 0:
            return {'msg': 'Email существует'}
        if len(params['psw']) < 6:
            return {'msg': 'Пароль должен быть более 6-ти символов'}
        if len(params['name']) < 3:
            return {'msg': 'Имя должно содержать более 2-х символов'}
        try:
            user = dbUSer(**params)
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'msg': 'Произошла внутрення ошибка'}, 400
        return {'success': True}


class UserLogin(Resource):
    def post(self):
        auth = request.authorization

        user = dbUSer.query.filter_by(email=auth.username).first()

        if not user or not check_password_hash(user.psw, auth.password):
            return jsonify({'msg': 'Неверно введенный логин и/или пароль'})

        exp_time = datetime.timedelta(minutes=300)
        return {'access_token': create_access_token(user.public_id, expires_delta=exp_time)}


class Users(Resource):
    # def __init__(self):
    #     self.token = request.headers['Authorization'].split(' ')[1]
    #     self.public_id = decode_token(encoded_token=self.token)['sub']
    #     self.query_user = dbUSer.query.filter_by(public_id=self.public_id).one()

    @jwt_required()
    @is_admin
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
        self.token = request.headers['Authorization'].split(' ')[1]
        self.public_id = decode_token(encoded_token=self.token)['sub']
        self.query_user = dbUSer.query.filter_by(public_id=self.public_id).one()

    @jwt_required()
    # @is_admin
    def get(self):
        params = request.json
        email = params['email']
        find_user = dbUSer.query.filter_by(email=email).one()
        res = {self.query_user.email: {
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
                return {'msg': 'Нет прав для изменения другого пользователя'}

        self.query_user.name = name
        db.session.commit()

        return {'success': True}

    @jwt_required()
    @is_admin
    def delete(self):
        return {}


class Index(Resource):
    # @jwt_required()
    def post(self):
        print(request.json)
        return {'index': 'index'}
