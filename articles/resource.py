import json
import uuid

from flask_restful import Resource
from flask import session, request, send_file
from flask_jwt_extended import jwt_required
from models import Article as dbArticle, User as dbUser, GroupArticle as dbGroupArticle, db, Role as dbRole
import os
import shutil


def is_admin(func):
    def wrapper(*args, **kwargs):
        if session['is_admin'] is None:
            return {'success': False, 'msg': 'Необходимо авторизоваться'}, 401
        elif session['is_admin']:
            return func(*args, **kwargs)
        return {'success': False, 'msg': 'Вы не являетесь администратором'}, 403
    return wrapper


class RGroupArticle(Resource):
    def __init__(self):
        public_id = session['public_id']
        self.current_user = dbUser.query.filter_by(public_id=public_id).one() if public_id is not None else None

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
        if group_id is None or group_name is None:
            return {'success': False, 'msg': 'Не передан id изменяемой группы'}, 400
        try:
            edit_group = dbGroupArticle.query.filter_by(id=group_id).one()
            edit_group.name = group_name
            db.session.commit()
            return {'success': True}
        except Exception as e:
            return {'msg': 'Внутренняя ошибка', 'e': str(e)}, 500

    @jwt_required()
    def get(self):
        params = request.args
        departament_id = params.get('departament_id')
        if departament_id is None: return {'msg': 'Не переданы параметр департамента'}, 400
        group_list = dbGroupArticle.query.filter_by(departament_id=departament_id).all()
        data = [{'id': i.id, 'name': i.name} for i in group_list]
        return data


class RArticle(Resource):
    @jwt_required()
    def __init__(self):
        public_id = session['public_id']
        self.current_user = dbUser.query.filter_by(public_id=public_id).one() if public_id is not None else None

    def get(self, article_id):
        find_article = dbArticle.query.filter_by(id=article_id).first()
        if find_article is None:
            return {'msg': 'Запись с таким id не найдена'}, 400
        data = {
            'group': find_article.group if find_article.group is None else find_article.group.name,
            'user': find_article.user_id,
            'title': find_article.title,
            'description': find_article.description,
            'blogData': json.loads(find_article.blog_data)
        }
        return data

    def put(self, article_id):
        find_article = dbArticle.query.filter_by(id=article_id).first()
        if find_article is None:
            return {'msg': 'Запись с таким id не найдена'}, 400
        params = request.json
        try:
            if params.get('title') is not None: find_article.title = params['title']
            if params.get('description') is not None: find_article.title = params['description']
            if params.get('blogData') is not None:
                find_article.title = params['blogData']
            db.session.commit()
            return {'success': True}
        except Exception as e:
            return {'msg': 'Внутренняя ошибка', 'success': False}, 500

    def delete(self, article_id):
        find_article = dbArticle.query.filter_by(id=article_id).first()
        if find_article is None:
            return {'msg': 'Запись с таким id не найдена'}, 400

        try:
            if session['is_admin'] or self.current_user.id == find_article.user_id:
                db.session.delete(find_article)
                db.session.commit()
                return {'success': True}
            else:
                return {'msg': 'Нет прав для удаление этой записи', 'success': False}, 403
        except Exception as e:
            return {'msg': 'Внутренняя ошибка', 'success': False, 'txt': str(e)}, 500


class RArticles(Resource):
    """
        endpoint = '/article'
    """
    def __init__(self):
        public_id = session['public_id']
        self.current_user = dbUser.query.filter_by(public_id=public_id).one() if public_id is not None else None

    @jwt_required()
    def get(self):
        params = request.args

        if params.get('group_id') is None and params.get('departament_id'):
            articles = dbArticle.query.filter_by(departament_id=params['departament_id'], group_id=None).all()
        elif params.get('group_id') and params.get('departament_id') is None:
            articles = dbArticle.query.filter_by(group_id=params['group_id']).all()
        else:
            return {'success': False, 'msg': 'Не переданы параметры запроса'}, 400
        data = []
        for i in articles:
            data.append({
                'articleId': i.id,
                'userId': i.user_id,
                'groupId': i.group_id,
                'title': i.title,
                'description': i.description
            })
        return data

    @jwt_required()
    def post(self):
        params = request.json
        user_id = self.current_user.id
        group_id = params.get('group_id')
        try:
            title = params['title']
            description = params['description']
            blog_data = params['blogData']

            departament_id = params['departament_id']
        except Exception as e:
            return {'msg': 'переданы не все поля в body'}, 400
        try:
            for i in blog_data['blocks']:
                if i['type'] == 'image':
                    img_temp = i['data']['file']['url'].split('/')[-1]
                    shutil.move(f'upload/temp/{img_temp}', f'upload/image_article/{img_temp}')
                    i['data']['file']['url'] = f'http://192.168.0.203:8787/upload/image-article/{img_temp}'

            add_articles = dbArticle(user_id=user_id, group_id=group_id, title=title, description=description,
                                     blog_data=json.dumps(blog_data), departament_id=departament_id)
            db.session.add(add_articles)
            db.session.commit()

            return {'success': True}
        except Exception as e:
            return {'msg': str(e)}, 500


class UploadImageArticleTemp(Resource):
    """
        Endpoint этого ресурса находиться в основном приложении
        api.add_resource(UploadImageArticleTemp, '/upload')
    """

    def post(self):
        if request.files.get('image') is None: return {'msg': 'Не передано изображение'}, 400
        file = request.files['image']
        file_name = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
        if file:
            file_path = f"upload/temp/{file_name}"
            file.save(os.path.join('upload/temp/', f"{file_name}"))

        return {'success': True, 'file': {'url': f'{request.base_url}/temp/{file_name}'}}


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
