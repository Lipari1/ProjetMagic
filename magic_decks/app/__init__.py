from flask import Flask
from flask_login import LoginManager
import logging

from .views import blueprint
from .db import getDb

db = getDb()

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///magic_decks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key_here'

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.user_loader(lambda : 'Jessie')

    app.register_blueprint(blueprint)

    # Configuration du logging
    logging.basicConfig(filename='app.log', level=logging.DEBUG, 
                        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    
    print(app)
    print(app.url_map)

    return app

