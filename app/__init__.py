from flask import Flask
from .db import init_db

def create_app():
    app = Flask(__name__)
    init_db()
    from . import routes
    app.register_blueprint(routes.bp)
    return app
