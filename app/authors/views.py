from . import authors
from ..models import User, Author
from flask import make_response, request, jsonify, abort
from urllib import unquote_plus
from google.appengine.ext import ndb

def search_author(author_id):
    key = ndb.Key('Author', author_id)
    return key.get()

def get_author(author_id):
    author = search_author(author_id)
    return make_response(jsonify(author.toJSON), 200)

@authors.route('author/<author_id>', methods=['GET'])
def handle_author(author_id):
    if request.method == 'GET':
        return get_author(author_id)
