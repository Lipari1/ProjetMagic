from app import db, create_app
from flask import redirect, url_for
from flask_login import LoginManager, current_user, login_required
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

# Route principale qui redirige vers la connexion si l'utilisateur n'est pas authentifié
@app.route('/')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('my_blueprint.login'))
    else:
        return redirect(url_for('my_blueprint.index'))

# Protéger la vue des decks pour exiger une connexion
@app.route('/decks')
@login_required
def decks():
    return redirect(url_for('my_blueprint.index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
