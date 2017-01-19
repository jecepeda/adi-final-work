from flask import Blueprint

authors = Blueprint('authors', __name__)

from . import views
