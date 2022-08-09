import json
import uuid

from flask_restful import Resource
from flask import session, request, send_file
from flask_jwt_extended import jwt_required, decode_token
from models import Article as dbArticle, User as dbUser, GroupArticle as dbGroupArticle, db, Role as dbRole
import os
import shutil


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
    # @jwt_required()
    def __init__(self):
        public_id = session['public_id']
        self.current_user = dbUser.query.filter_by(public_id=public_id).one() if public_id is not None else None

    def get(self, article_id):
        find_article = dbArticle.query.filter_by(id=article_id).first()
        if find_article is None: return {'msg': 'Запись с таким id не найдена'}, 401
        data = {find_article.id: {
            'group': find_article.group.name,
            'user': find_article.user_id,
            'head': find_article.head,
            'description': find_article.descriptino,
            'content': json.loads(find_article.content)

        }}
        return data, 401

    def put(self, article_id):
        pass

    def delete(self, article_id):
        pass


class RArticles(Resource):
    """
    endpoint = '/article'
    """
    def __init__(self):
        public_id = session['public_id']
        self.current_user = dbUser.query.filter_by(public_id=public_id).one() if public_id is not None else None

    @jwt_required()
    def get(self):
        articles = dbArticle.query.all()
        data = {}
        for i in articles:
            data[i.id] = {
                'article_id': i.id,
                'user_id': i.user_id,
                'group_id': i.group_id,
                'head': i.head,
                'description': i.description,
                'content': json.loads(i.content)
            }
        return data

    @jwt_required()
    def post(self):
        params = request.json
        user_id = self.current_user.id
        try:
            group_id = params['group_id']
            head = params['head']
            description = params['description']
            content = params['content']
        except Exception as e:
            return {'msg': 'переданы не все поля в body'}, 401

        blocks = content['blogData']['blocks']
        for i in blocks:
            if i['type'] == 'image':
                img_temp = i['data']['file']['url'].split('/')[-1]
                shutil.move(f'upload/temp/{img_temp}', f'upload/image_article/{img_temp}')
                i['data']['file']['url'] = f'http://192.168.0.203:8787/upload/image-article/{img_temp}'

        add_articles = dbArticle(user_id=user_id, group_id=group_id, head=head, description=description,
                                 content=json.dumps(content))
        db.session.add(add_articles)
        db.session.commit()

        return {'success': True}


class UploadImageArticleTemp(Resource):
    """
    Endpoint этого ресурса находиться в основном приложении
    api.add_resource(UploadImageArticleTemp, '/upload')
    """

    def post(self):
        print(request.files)
        if request.files.get('image') is None: return {'msg': 'Не передано изображение'}, 401
        file = request.files['image']
        file_name = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
        if file:
            file_path = f"upload/temp/{file_name}"
            file.save(os.path.join('upload/temp/', f"{file_name}"))

        return {'success': True, 'file': {'url': f'{request.base_url}/temp/{file_name}'},
                'temp_image': True}


class GetImageArticle(Resource):
    """
        Endpoint этого ресурса находиться в основном приложении
        api.add_resource(GetImageArticle, '/upload/<string:path_dir>/<string:url_image>')
    """
    def get(self, url_image, path_dir):
        if path_dir == 'temp':
            if not os.path.exists(f'upload/temp/{url_image}'):
                return {'msg': 'Изображение не найдено'}, 400
            return send_file(f'upload/temp/{url_image}', mimetype='image/gif')
        elif path_dir == 'image-article':
            if not os.path.exists(f'upload/image_article/{url_image}'):
                return {'msg': 'Изображение не найдено'}, 400
            return send_file(f'upload/image_article/{url_image}', mimetype='image/gif')
        else:
            return {'msg': 'ошибка'}, 401


class Index(Resource):
    def get(self):
        return {'api': '12345123123'}
