from flask import Flask, make_response, jsonify
from users.views import users as users_blueprint
from authors.views import authors as authors_blueprint
from organisms.views import organisms as organisms_blueprint
from papers.views import papers as papers_blueprint
from .auth import auth

app = Flask(__name__)

app.register_blueprint(users_blueprint)
app.register_blueprint(authors_blueprint)
app.register_blueprint(organisms_blueprint)
app.register_blueprint(papers_blueprint)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)


@app.errorhandler(500)
def internal_server_error(error):
    return make_response(jsonify({'error': 'Internal Server Errror'}), 500)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(401)
def unauthorized(error):
    return make_response(jsonify({'error': 'Unauthorized'}), 401)
