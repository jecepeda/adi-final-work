from . import authors
from ..models import User, Author
from flask import make_response, request, jsonify, abort
from urllib import unquote_plus
from google.appengine.ext import ndb
from ..auth import auth
import re


def verify_email(email):
    m = re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email)
    return True if m else False


def check_all_elements(elements):
    return all(elem is not None for elem in elements)


def search_author(author_id):
    key = ndb.Key('Author', author_id)
    return key.get()


def get_author(author_id):
    author = search_author(author_id)

    if author is None:
        abort(404)

    return make_response(jsonify(author.toJSON), 200)


@auth.login_required
def delete_author(author_id):
    key = ndb.Key('Author', author_id)

    if key.get() is None:
        abort(404)

    key.delete()
    return make_response(jsonify({'removed': author_id}), 200)


@authors.route('/author/<author_id>', methods=['GET', 'DELETE'])
def handle_author(author_id):
    author_id = unquote_plus(author_id).decode('utf-8')
    if request.method == 'GET':
        return get_author(author_id)
    elif request.method == 'DELETE':
        return delete_author(author_id)


@authors.route('/author', methods=['POST'])
@auth.login_required
def create_author():
    if not request.json or not request.json.get('id'):
        abort(400)

    author_id = request.json.get('id')
    if not verify_email(author_id):
        abort(400)

    author = search_author(author_id)
    if author is not None:
        abort(400)

    organism = request.json.get('organism')

    name = request.json.get('name')
    last_name = request.json.get('lastName')

    if not check_all_elements([organism, name, last_name]):
        abort(400)

    organism_key = None

    try:
        organism_key = ndb.Key(urlsafe=organism)
    except:
        abort(400)

    if organism_key.get() is None:
        abort(400)

    if verify_email(author_id) is False:
        abort(400)

    new_author = Author(id=author_id,
                        organism=organism_key,
                        name=name,
                        last_name=last_name)

    author_id = new_author.put()

    return make_response(jsonify({'created': author_id.id()}), 200)
