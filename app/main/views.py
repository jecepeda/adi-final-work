from . import main

@main.route('/')
def hello():
    return 'Hello world'
