from flask import Flask
from main.views import main as main_blueprint

app = Flask(__name__)

app.register_blueprint(main_blueprint)
