from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
import logging
import os
from .views import blueprint
from .db import getDb
from .models import User, db

db = getDb()

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/magic_decks.db'  # Le fichier DB est dans instance
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key_here'

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(blueprint)

    # Initialiser Migrate
    migrate = Migrate(app, db)

    # Utiliser un fichier log dans le dossier instance
    instance_log_path = os.path.join(app.instance_path, 'app.log')
    logging.basicConfig(filename=instance_log_path, level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

    print(app)
    print(app.url_map)

    return app

