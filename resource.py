import json
import time

from flask_restful import Resource
from marshmallow import validate
from flask import request, jsonify, session, send_file
from werkzeug.security import check_password_hash, generate_password_hash
from models import User as dbUSer, Role as dbRole, Departament as dbDepartament, GroupArticle as dbGroupArticle
from flask_jwt_extended import create_access_token, jwt_required
import datetime
from models import db
import os
from flasgger import swag_from


def is_admin(func):
    def wrapper(*args, **kwargs):
        # public_id = session['public_id']
        # if public_id is None:
        #     return {'success': False, 'msg': 'Необходимо авторизоваться'}, 401
        # query_user = dbUSer.query.filter_by(public_id=public_id).one()
        # if query_user.role.name == dbRole.query.filter_by(name='Admin').one().name:
        if session['is_admin'] is None:
            return {'success': False, 'msg': 'Необходимо авторизоваться'}, 401
        elif session['is_admin']:
            return func(*args, **kwargs)
        return {'success': False, 'msg': 'Вы не являетесь администратором'}, 403

    return wrapper


def validator_user_data(func):
    def wrapper(*args, **kwargs):
        params = request.json

        if params.get('email') is None or params.get('psw') is None or params.get('name') is None:
            return {'success': False, 'msg': 'Переданы не все поля'}, 400
        email = params.get('email')
        psw = params.get('psw')
        name = params.get('name')
        if len(dbUSer.query.filter_by(email=email).all()) != 0:
            return {'success': False, 'msg': 'Email существует'}, 400
        try:
            validate.Email()(email)
        except Exception as ex:
            return {'success': False, 'msg': 'Не валидный email'}, 400
        if len(psw) < 6:
            return {'success': False, 'msg': 'Пароль должен быть более 6-ти символов'}, 400
        if len(name) < 3:
            return {'success': False, 'msg': 'Имя должно содержать более 2-х символов'}, 400

        return func(*args, **kwargs)

    return wrapper


class UserRegistration(Resource):
    @validator_user_data
    def post(self):
        params = request.json
        exp_time = datetime.timedelta(minutes=1440)
        try:
            user = dbUSer(**params)
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'msg': 'Произошла внутрення ошибка', 'text': str(e)}, 500
        return {'success': True,
                'access_token': create_access_token(user.public_id, expires_delta=exp_time),
                'name': user.name,
                'email': user.email,
                'foto_url': user.foto_url}


class UserLogin(Resource):
    def post(self):
        auth = request.authorization

        user = dbUSer.query.filter_by(email=auth.username).first()

        if not user or not check_password_hash(user.psw, auth.password):
            return {'success': False, 'msg': 'Неверно введенный логин и/или пароль'}, 401

        exp_time = datetime.timedelta(minutes=1440)
        admin = True if user.role_id == 1 else False
        return {'access_token': create_access_token(user.public_id, expires_delta=exp_time),
                'name': user.name,
                'email': user.email,
                'foto_url': user.foto_url,
                'is_admin': admin}


class Users(Resource):

    @jwt_required()
    def get(self):
        users = dbUSer.query.all()
        result = {}
        for i in users:
            print(i.departament)
            result[i.id] = {'name': i.name,
                            'email': i.email,
                            'role': i.role.name,
                            'departament': i.departament_id,
                            'foto_url': i.foto_url}
        return result

    @jwt_required()
    @is_admin
    @validator_user_data
    def post(self):
        UserRegistration.post()
        return {'success': True}


class User(Resource):
    def __init__(self):
        public_id = session['public_id']
        self.current_user = dbUSer.query.filter_by(public_id=public_id).one() if public_id is not None else None

    def get(self, user_id):
        find_user = dbUSer.query.filter_by(id=user_id).first()
        if find_user is None: return {'success': False}
        res = {find_user.id: {
            'name': find_user.name,
            'email': find_user.email,
            'role': find_user.role.name,
            # 'departament': find_user.departament,
            'public_id': find_user.public_id,
            'foto_url': find_user.foto_url
        }}
        return res

    @jwt_required()
    def put(self, user_id):
        find_user = dbUSer.query.filter_by(id=user_id).first()
        if find_user is None: return {'success': False}
        admin = dbRole.query.filter_by(name='Admin').one()
        if find_user.email != self.current_user.email:
            if admin != self.current_user.role:
                return {'success': False, 'msg': 'Нет прав для изменения другого пользователя'}, 403

        if request.json.get('name') is not None: find_user.name = request.json.get('name')
        if request.json.get('foto_url') is not None: find_user.name = request.json.get('foto_url')
        if request.json.get('old_psw') is not None:
            if check_password_hash(find_user.psw, request.json['old_psw']):
                find_user.psw = generate_password_hash(request.json.get('psw'), method="pbkdf2:sha256")
            else:
                return {'success': False, 'msg': 'Введен неверный старый пароль'}, 400
        db.session.commit()

        return {'success': True}

    @jwt_required()
    @is_admin
    def delete(self, user_id):
        del_user = dbUSer.query.filter_by(id=user_id).first()
        if del_user is None:
            return {'success': False, 'msg': 'Пользователь с таким id не найден'}, 404
        db.session.delete(del_user)
        db.session.commit()
        return {'success': True}


class ProfileFoto(Resource):
    def __init__(self):
        public_id = session['public_id']
        self.current_user = dbUSer.query.filter_by(public_id=public_id).one() if public_id is not None else None

    # @jwt_required()
    # def put(self, url_image):
    #     if request.files.get('profile_img') is None: return {'msg': 'В запросе не передано изображение профиля'}, 400
    #     file = request.files['profile_img']
    #     if file:
    #         file_path = f"upload/img_profile/{session['public_id']}.{file.filename.split('.')[-1]}"
    #         file.save(os.path.join('upload/img_profile', f"{session['public_id']}.{file.filename.split('.')[-1]}"))
    #
    #         self.current_user.foto_url = file_path

    def get(self, url_image):
        if not os.path.exists(f'upload/img_profile/{url_image}'):
            return {'msg': 'Изображение не найдено'}, 400
        return send_file(f'upload/img_profile/{url_image}', mimetype='image/gif')


class EditProfileFoto(Resource):
    def __init__(self):
        public_id = session['public_id']
        self.current_user = dbUSer.query.filter_by(public_id=public_id).one() if public_id is not None else None

    @jwt_required()
    def put(self, user_id):
        if user_id != self.current_user.id: return {'msg': 'Нет прав для изменения фото этого юзера'}
        if request.files.get('profile_img') is None: return {'msg': 'В запросе не передано изображение профиля'}, 400
        file = request.files['profile_img']
        if file:
            file_path = f"upload/img_profile/{session['public_id']}.{file.filename.split('.')[-1]}"
            file.save(os.path.join('upload/img_profile', f"{session['public_id']}.{file.filename.split('.')[-1]}"))

            self.current_user.foto_url = file_path
        return {'success': True}, 201


class Departament(Resource):
    def __init__(self):
        public_id = session['public_id']
        self.current_user = dbUSer.query.filter_by(public_id=public_id).one() if public_id is not None else None

    @jwt_required()
    def get(self):

        groups = {}
        for i in dbGroupArticle.query.all():
            if groups.get(i.departament_id) is None:
                groups[i.departament_id] = [{'name': i.name, 'id': i.id}]
            else:
                groups[i.departament_id].append({'name': i.name, 'id': i.id})

        if self.current_user.role_id == 1:
            data = [{'id': i.id, 'name': i.name, 'groups': groups.get(i.id)} for i in dbDepartament.query.all()]
            return data

        data = [{'id': self.current_user.departament.id, 'name': self.current_user.departament.name,
                 'groups': groups.get(self.current_user.departament.id)},
                {'id': dbDepartament.query.filter_by(id=0).one().id,
                 'name': dbDepartament.query.filter_by(id=0).one().name,
                 'groups': groups.get(dbDepartament.query.filter_by(id=0).one().id)}]
        return data


class Index(Resource):
    def __init__(self):
        public_id = session['public_id']
        self.current_user = dbUSer.query.filter_by(public_id=public_id).one() if public_id is not None else None

    # @jwt_required()
    @swag_from('yaml/schema.yml')
    def post(self):
        print(request.json)
        with open('res.json', 'w') as f:
            json.dump(request.json, f, indent=4)
        return request.json

    # @swag_from('yaml/schema.yml')
    def get(self):
        return {'2': 'n'}
