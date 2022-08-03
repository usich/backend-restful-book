from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, decode_token
from models import Article as dbArticle, User


class Article(Resource):
    def __init__(self):
        self.token = request.headers['Authorization'].split(' ')[1]
        self.public_id = decode_token(encoded_token=self.token)['sub']
        self.query_user = User.query.filter_by(public_id=self.public_id).one()

    @jwt_required()
    def get(self):
        # res = request.json
        # print(res)
        return {'345': '2345'}

    # @jwt_required()
    def post(self):
        data = request.json
        add_article = dbArticle()
        return {'s': '456'}


class Articles(Resource):
    def get(self):
        return {}


class Index(Resource):
    def get(self):
        return {'api': '12345123123'}
