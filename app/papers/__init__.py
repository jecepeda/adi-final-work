from flask import Blueprint

papers = Blueprint('papers', __name__)

from . import views
