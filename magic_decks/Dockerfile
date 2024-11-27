# Utiliser une image de base Python
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers du projet
COPY . /app

# Exposer le port sur lequel l'application s'exécute
EXPOSE 5000

# Commande pour exécuter l'application
CMD ["python", "run.py"]
