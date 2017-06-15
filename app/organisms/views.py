from . import organisms
from ..models import Organism
from flask import make_response, request, jsonify, abort
from urllib import unquote_plus
from google.appengine.ext import ndb
from ..auth import auth
import re

def check_all_elements(elements):
    return all(elem is not None for elem in elements)

@organisms.route('/organisms', methods=['POST','GET'])
def handle_base_organism_endpoint():
    if request.method == 'GET':
        return get_organisms()
    else:
        return put_organism()

@auth.login_required
def put_organism():
    if not request.json:
        abort(400)

    name = request.json.get('name')
    address = request.json.get('address')
    country = request.json.get('country')

    if check_all_elements([name, address, country]) is not True:
        abort(400)
    new_organism = Organism(name=name,
                            address=address,
                            country=country)

    organism_id = new_organism.put()

    return make_response(jsonify({'created':organism_id.urlsafe()}),200)

def get_organisms():
    return make_response(jsonify(Organism.getAll()), 200)

def get_organism(id_organism):
    organism = None
    try:
        organism = ndb.Key(urlsafe=id_organism).get()
    except:
        abort(404)
    if organism is None:
        abort(404)
    return make_response(jsonify(organism.toJSON), 200)

@auth.login_required
def delete_organism(id_organism):
    organism = None
    try:
        organism = ndb.Key(urlsafe=id_organism)
    except:
        abort(404)
    if organism.get() is None:
        abort(404)
    organism.delete()
    return make_response(jsonify({'removed': organism.urlsafe()}), 200)

@organisms.route('/organisms/<id_organism>', methods=['GET', 'DELETE'])
def handle_organism(id_organism):
    if request.method == 'GET':
        return get_organism(id_organism)
    elif request.method == 'DELETE':
        return delete_organism(id_organism)
