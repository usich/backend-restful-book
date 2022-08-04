from flask import Blueprint
from flask_restful import Api
from articles.resource import RArticle, Index, RGroupArticle, RArticles

articles_blueprint = Blueprint('api', __name__)
api_db = Api(articles_blueprint)

api_db.add_resource(RArticles, '/article')
api_db.add_resource(RArticle, '/article/<int:article_id>')
api_db.add_resource(RGroupArticle, '/group-article')
api_db.add_resource(Index, '/')


# @articles_blueprint.route('/')
# def index():
#     return 'asdasdasdasd'
