# from flask import Flask, session, request
# from flask_restful import Api, Resource
# from flask_migrate import Migrate
# from articles.app import articles_blueprint
# from models import db, User as dbUser
# from resource import UserLogin, UserRegistration, Index, Users, User, ProfileFoto
# from flask_jwt_extended import JWTManager, decode_token
# from flask_cors import CORS
# from config import database_uri, secret_key, debug
# from flasgger import Swagger

from flask import Flask, session, request
from flasgger import Swagger
from flask_cors import CORS
from flask_jwt_extended import JWTManager, decode_token
from flask_migrate import Migrate
from flask_restful import Api

from articles.app import articles_blueprint
from config import database_uri, secret_key, debug
from models import db, User as dbUser
from resource import UserLogin, UserRegistration, Index, Users, User, ProfileFoto


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key

api = Api(app)

app.register_blueprint(articles_blueprint, url_prefix='/api/v1/book')

swagger = Swagger(app)

jwt = JWTManager(app)

CORS(app)


db.init_app(app)
migrate = Migrate(app, db)

api.add_resource(Index, '/')
api.add_resource(UserLogin, '/login')
api.add_resource(UserRegistration, '/registration')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(Users, '/user')
# api.add_resource('', '/user/<int:user_id>/upload-foto')
api.add_resource(ProfileFoto, '/upload/img_profile/<string:url_image>')
# api.add_resource(Profile, '/profile')


@app.before_request
def before_request():
    try:
        token = request.headers['Authorization'].split(' ')[1]
        public_id = decode_token(encoded_token=token)['sub']
        query_user = dbUser.query.filter_by(public_id=public_id).one()
        session['public_id'] = query_user.public_id
    except Exception as e:
        session['public_id'] = None


if __name__ == '__main__':
    app.run(debug=debug, port=8787, host='0.0.0.0')
