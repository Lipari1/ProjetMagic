import logging
from app import create_app, db

app = create_app()

with app.app_context():
    try:
        db.create_all()
        print("Base de données créée avec succès.")
    except Exception as e:
        print(f"Erreur lors de la création de la base de données : {e}")
        logging.error(f"Erreur lors de la création de la base de données : {e}")
