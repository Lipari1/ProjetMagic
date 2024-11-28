from app import db, create_app
from flask_login import LoginManager
from app.models import User

# Créez l'application Flask
app = create_app()

# Initialisez LoginManager et configurez-le
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "my_blueprint.login"  # Vue à laquelle rediriger les utilisateurs non authentifiés

# Fonction de chargement d'utilisateur
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Créez la base de données dans le contexte de l'application
with app.app_context():
    db.create_all()  # Crée les tables de la base de données automatiquement

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
