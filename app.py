from flask import Flask, jsonify
from flask_restful import Api
from flask_migrate import Migrate
from articles.app import api_db, articles_blueprint
from models import db
from resource import UserLogin, UserRegistration, Index, Users, User
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import database_uri, secret_key, debug


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key

api = Api(app)

app.register_blueprint(articles_blueprint, url_prefix='/api/v1/book')

jwt = JWTManager(app)

CORS(app)


db.init_app(app)
migrate = Migrate(app, db)

api.add_resource(Index, '/')
api.add_resource(UserLogin, '/login')
api.add_resource(UserRegistration, '/registration')
api.add_resource(Users, '/users')
api.add_resource(User, '/user')


# @app.route('/')
# def index():
#     return ''
#
#
# @app.route('/add_role')
# def add_role():
#     user = User(email='qwe2@r.ru', psw='12345')
#     db.session.add(user)
#     db.session.commit()
#     # data = User.query.filter_by(email='qwe@r.ru').first()
#     # print(data.role.name)
#     return jsonify({'':''})


if __name__ == '__main__':
    app.run(debug=debug, port=8787, host='0.0.0.0')
