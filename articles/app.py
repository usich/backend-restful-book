from flask import Blueprint
from flask_restful import Api
from articles.resource import RArticle, Index

articles_blueprint = Blueprint('api', __name__)
api_db = Api(articles_blueprint)

api_db.add_resource(RArticle, '/article')
api_db.add_resource(Index, '/')


# @articles_blueprint.route('/')
# def index():
#     return 'asdasdasdasd'
