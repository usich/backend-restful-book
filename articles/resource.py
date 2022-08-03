from flask_restful import Resource, request
from flask import session
from flask_jwt_extended import jwt_required, decode_token
from models import Article, User as dbUser, GroupArticle


class RGroupArticle(Resource):
    @jwt_required()
    def post(self):
        if request.json.get('name') is None:
            return {'success': False, 'msg': 'Не передано имя группы'}
        name_group = request.json['name']
        group_article_add = GroupArticle('')


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

        add_article = Article()
        return {'s': '456'}


class RArticles(Resource):
    def get(self):
        return {}


class Index(Resource):
    def get(self):
        return {'api': '12345123123'}
