from . import users
from ..models import User
from ..auth import auth
from flask import g, make_response, request, jsonify, abort
from urllib import unquote_plus
from google.appengine.ext import ndb
import re

def check_all_elements(elements):
    return all(elem is not None for elem in elements)

def verify_email(email):
    m = re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email)
    return True if m else False

def search_user(user_id):
    key = ndb.Key('User', user_id)
    return key.get()

@auth.login_required
def update_user(user_id):
    user = search_user(user_id)

    if user is None:
        abort(404)
    elif user != g.user:
        abort(401)
    nick = request.json.get('nick')
    name = request.json.get('name')
    last_name = request.json.get('lastName')

    if check_all_elements([name, last_name]) is False:
        abort(400)

    user.name = name
    user.last_name = name
    user.nick = nick

    user.put()

    return make_response(jsonify(user.toJSON), 200)

def get_user(user_id):
    user = search_user(user_id)

    if user is None:
        abort(400)

    return make_response(jsonify(user.toJSON), 200)

@auth.login_required
def delete_user(user_id):
    key = ndb.Key('User', user_id)
    user = key.get()

    if user is None:
        abort(404)
    elif user != g.user:
        abort(401)

    key.delete()
    return make_response(jsonify({'deleted': user_id}), 200)


@users.route('/user/<user_id>', methods=['POST', 'GET', 'PUT', 'DELETE'])
def user_treatment(user_id):
    user_id = unquote_plus(user_id).decode('utf-8')
    if request.method == 'POST':
        return update_user(user_id)
    elif request.method == 'PUT':
        return update_user(user_id)
    elif request.method == 'GET':
        return get_user(user_id)
    elif request.method == 'DELETE':
        return delete_user(user_id)

@users.route('/user', methods=['GET', 'POST'])
def get_users():
    if request.method == 'POST':
        return post_user()
    elif request.method == 'GET':
        return make_response(jsonify(User.getAll()), 200)


def post_user():
    if not request.json or not request.json.get('id'):
        abort(400)

    user_id = request.json.get('id')
    user = search_user(user_id)

    if user is not None:
        abort(400)

    nick = request.json.get('nick')
    name = request.json.get('name')
    last_name = request.json.get('lastName')
    password = request.json.get('password')

    if check_all_elements([name, last_name, password]) is False:
        abort(400)

    mail = user_id

    if verify_email(mail) is False:
        abort(400)

    new_user = User(id=mail,
                    name=name,
                    last_name=last_name,
                    nick=nick)

    new_user.hash_password(password)
    user_id = new_user.put()

    return make_response(jsonify({'created':user_id.id()}), 200)
