from app.api import bp
import re
from app import db
from flask import url_for, request, jsonify
# from app.api.auth import token_auth
from app.api.error import bad_request
from app.models import User
from app.api.auth import token_auth


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return bad_request('You must post JSON data')
    message = {}
    if 'username' not in data or not data.get('username', None):
        message['username'] = 'Please provide a valid username.'
    pattern = '^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'
    if 'email' not in data or not re.match(pattern, data.get('email', None)):
        message['email'] = 'Please provide a valid email address.'
    if 'password' not in data or not data.get('password', None):
        message['password'] = 'Please provide a valid password.'
    if User.query.filter_by(username=data.get('username', None)).first():
        message['username'] = 'Please provide a different username'
    if User.query.filter_by(email=data.get('email', None)).first():
        message['email'] = 'Please provide a different email'
    if message:
        return bad_request(message)
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    # HTTP协议要求201响应包含一个值为新资源URL的Location头部
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_user_list():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(
        User.query, page, per_page, 'api.get_user_list')
    return jsonify(data)


@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/users', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    user = User.query.get_or_404(id) 
    data = request.get_json()
    if not data:
        return bad_request("you must post JSON data.")
    message = {}
    if 'username' in data and not data.get('username', None):
        message['username'] = 'Please provide a valid username.'

    pattern = '^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'
    if 'email' in data and not re.match(pattern, data.get('email', None)):
        message['email'] = 'Please provide a valid email address.'

    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        message['username'] = 'Please use a different username.'
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        message['email'] = 'Please use a different email address.'
    
    if message:
        return bad_request(message)
    
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())


@bp.route('/users', methods=['POST'])
def delete_user(id):
    pass