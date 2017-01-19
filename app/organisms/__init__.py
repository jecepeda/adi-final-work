from flask import Blueprint

organisms = Blueprint('organisms', __name__)

from . import views
