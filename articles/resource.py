from flask_restful import Resource
from flask import session, request
from flask_jwt_extended import jwt_required, decode_token
from models import Article as dbArticle, User as dbUser, GroupArticle as dbGroupArticle, db, Role as dbRole


def is_admin(func):
    def wrapper(*args, **kwargs):
        public_id = session['public_id']
        if public_id is None:
            return {'success': False, 'msg': 'Необходимо авторизоваться'}
        query_user = dbUser.query.filter_by(public_id=public_id).one()
        if query_user.role.name == dbRole.query.filter_by(name='Admin').one().name:
            return func(*args, **kwargs)

        return {'success': False, 'msg': 'Вы не являетесь администратором'}

    return wrapper


class RGroupArticle(Resource):
    @jwt_required()
    def post(self):
        if request.json.get('name') is None:
            return {'success': False, 'msg': 'Не передано имя группы'}
        name_group = request.json['name']
        user_departament = dbUser.query.filter_by(public_id=session['public_id']).one().departament_id
        try:
            group_article_add = dbGroupArticle(name=name_group, departament_id=user_departament)
            db.session.add(group_article_add)
            db.session.commit()
        except Exception as e:
            return {'success': False, 'msg': 'Группа не добавлена, внутренняя ошибка'}
        return {'seccess': True}

    @jwt_required()
    @is_admin
    def put(self):
        params = request.json
        group_id = params.get('group_id')
        group_name = params.get('group_name')
        if group_id is None or group_name is None: return {'success': False, 'msg': 'Не передан id изменяемой группы'}
        try:
            edit_group = dbGroupArticle.query.filter_by(id=group_id).one()
            edit_group.name = group_name
            db.session.commit()
            return {'success': True}
        except Exception as e:
            return {'msg': 'Внутренняя ошибка', 'e': str(e)}


class RArticle(Resource):
    @jwt_required()
    def __init__(self):
        public_id = session['public_id']
        self.query_user = dbUser.query.filter_by(public_id=public_id).one() if public_id is not None else None

    def get(self):
        # res = request.json
        # print(res)
        return {'345': '2345'}

    def post(self):
        data = request.json

        add_article = 'Article()'
        return {'s': '456'}


class RArticles(Resource):
    @jwt_required()
    def get(self):
        articles = dbArticle.query.all()
        data = {}
        for i in articles:
            data[i.head] = {
                'article_id': i.id,
                'user_id': i.user_id,
                'group_id': i.group_id,
                'description': i.description,
                'content': i.content
            }
        return data


class Index(Resource):
    def get(self):
        return {'api': '12345123123'}
