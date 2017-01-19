from .models import User
from google.appengine.ext import ndb
from flask_httpauth import HTTPBasicAuth
from flask import g

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    try:
        user = ndb.Key('User', username).get()
    except:
        return False

    if not user or not user.verify_password(password):
        return False

    g.user = user
    return True
