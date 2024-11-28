import logging
import requests
from .models import Deck, Card, fetch_card_info, User
from .db import getDb
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask import flash, jsonify, render_template, request, redirect, url_for, Blueprint

blueprint = Blueprint('my_blueprint', __name__, template_folder='templates')

db = getDb()

@blueprint.route('/')
def index():
    decks = Deck.query.filter_by(user_id=current_user.id).all() if current_user.is_authenticated else []
    return render_template('index.html', decks=decks)

@blueprint.route('/deck/<deck_id>')
def view_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    return render_template('deck.html', deck=deck)

@blueprint.route('/add_deck', methods=['GET', 'POST'])
@login_required
def add_deck():
    if request.method == 'POST':
        deck_name = request.form['name']
        new_deck = Deck(name=deck_name, user_id=current_user.id)
        db.session.add(new_deck)
        try:
            db.session.commit()
            flash('Deck ajouté avec succès !', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout du deck : {e}', 'danger')
        return redirect(url_for('my_blueprint.index'))
    return render_template('add_deck.html')

@blueprint.route('/delete_deck/<int:deck_id>', methods=['GET'])
@login_required
def delete_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id == current_user.id:
        try:
            # Supprimer toutes les cartes associées à ce deck
            Card.query.filter_by(deck_id=deck.id).delete()
            db.session.delete(deck)
            db.session.commit()
            flash('Deck et ses cartes associées supprimés avec succès', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la suppression du deck : {e}', 'danger')
    else:
        flash('Vous n\'êtes pas autorisé à supprimer ce deck', 'danger')
    return redirect(url_for('my_blueprint.index'))

@blueprint.route('/add_card/<deck_id>', methods=['GET', 'POST'])
def add_card(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if request.method == 'POST':
        try:
            name = request.form['name']
            type = request.form['type']
            mana_cost = request.form['mana_cost']
            new_card = Card(name=name, type=type, mana_cost=mana_cost, deck_id=deck.id)
            db.session.add(new_card)
            db.session.commit()
            logging.info(f"Carte ajoutée : {name} dans le deck {deck.name}")
            flash('Carte ajoutée avec succès !', 'success')
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erreur lors de l'ajout de la carte : {e}")
            flash('Erreur lors de l\'ajout de la carte', 'danger')
        return redirect(url_for('my_blueprint.view_deck', deck_id=deck.id))
    return render_template('add_card.html', deck=deck)

@blueprint.route('/delete_card/<deck_id>/<card_name>')
def delete_card(deck_id, card_name):
    deck = Deck.query.get_or_404(deck_id)
    card_to_delete = Card.query.filter_by(deck_id=deck.id, name=card_name).first()
    if card_to_delete:
        db.session.delete(card_to_delete)
        db.session.commit()
        flash('Carte supprimée avec succès !', 'warning')
    else:
        flash('Carte non trouvée', 'danger')
    return redirect(url_for('my_blueprint.view_deck', deck_id=deck.id))

@blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Inscription réussie !', 'success')
        return redirect(url_for('my_blueprint.login'))
    return render_template('signup.html')

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Connexion réussie !', 'success')
            return redirect(url_for('my_blueprint.index'))
        flash('Nom d\'utilisateur ou mot de passe incorrect', 'danger')
    return render_template('login.html')

@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Déconnexion réussie', 'info')
    return redirect(url_for('my_blueprint.index'))

@blueprint.route('/search_cards', methods=['GET'])
def search_cards():
    query = request.args.get('q', '')
    if query:
        # Requête vers l'API Scryfall
        response = requests.get(f'https://api.scryfall.com/cards/search?q={query}')
        if response.status_code == 200:
            data = response.json()
            # Récupérer un nombre limité de résultats
            results = []
            for card in data.get('data', [])[:10]:
                if 'image_uris' in card:
                    results.append({
                        'id': card.get('id'),
                        'name': card.get('name'),
                        'type': card.get('type_line'),
                        'mana_cost': card.get('mana_cost'),
                        'image': card['image_uris'].get('small')
                    })
            return jsonify(results)
    return jsonify([])
