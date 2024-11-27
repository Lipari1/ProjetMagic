import requests
import logging
from .models import Deck, Card, fetch_card_info, User
from .db import getDb
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from flask import flash, render_template, request, redirect, url_for, Blueprint

blueprint = Blueprint('my_blueprint', __name__, template_folder='templates')
# Liste temporaire pour stocker les decks
decks = []

db = getDb()

@blueprint.route('/')
def index():
    return render_template('index.html')

@blueprint.route('/deck/<deck_id>')
def view_deck(deck_id):
    # Placeholder pour récupérer un deck par son ID
    return render_template('deck.html', deck_id=deck_id)

@blueprint.route('/add_deck', methods=['GET', 'POST'])
def add_deck():
    if request.method == 'POST':
        deck_name = request.form['name']
        new_deck = Deck(name=deck_name)
        db.session.add(new_deck)
        db.session.commit()
        flash('Deck ajouté avec succès !', 'success')
        return redirect(url_for('index'))
    return render_template('add_deck.html')

'''
@blueprint.route('/add_card/<deck_id>', methods=['GET', 'POST'])
def add_card(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        mana_cost = request.form['mana_cost']
        new_card = Card(name=name, type=type, mana_cost=mana_cost, deck_id=deck.id)
        db.session.add(new_card)
        db.session.commit()
        flash('Carte ajoutée avec succès !', 'success')
        return redirect(url_for('view_deck', deck_id=deck_id))
    return render_template('add_card.html', deck=deck)
'''

@blueprint.route('/suggest_cards/<card_name>')
def suggest_cards(card_name):
    card_info = fetch_card_info(card_name)
    if card_info:
        # Par exemple, on peut suggérer des cartes du même type ou ayant des effets similaires
        suggested_cards = fetch_related_cards(card_info['type_line'])
        return render_template('suggestions.html', card=card_info, suggestions=suggested_cards)
    else:
        return "Carte introuvable", 404

def fetch_related_cards(card_type):
    response = requests.get(f'https://api.scryfall.com/cards/search?q=type:{card_type}')
    if response.status_code == 200:
        data = response.json()
        return data.get('data', [])
    else:
        return []

@blueprint.route('/update_deck/<deck_id>', methods=['GET', 'POST'])
def update_deck(deck_id):
    deck = decks[int(deck_id)]
    if request.method == 'POST':
        new_name = request.form['name']
        deck.name = new_name
        flash('Deck mis à jour avec succès !', 'success')
        return redirect(url_for('view_deck', deck_id=deck_id))
    return render_template('update_deck.html', deck=deck)

@blueprint.route('/delete_card/<deck_id>/<card_name>')
def delete_card(deck_id, card_name):
    deck = decks[int(deck_id)]
    deck.cards = [card for card in deck.cards if card.name != card_name]
    flash('Carte supprimée avec succès !', 'warning')
    return redirect(url_for('update_deck', deck_id=deck_id))

@blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Inscription réussie !', 'success')
        return redirect(url_for('login'))
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
            return redirect(url_for('index'))
        flash('Nom d\'utilisateur ou mot de passe incorrect', 'danger')
    return render_template('login.html')

@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Déconnexion réussie', 'info')
    return redirect(url_for('index'))

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
            logging.error(f"Erreur lors de l'ajout de la carte : {e}")
            flash('Erreur lors de l\'ajout de la carte', 'danger')
        return redirect(url_for('view_deck', deck_id=deck_id))
    return render_template('add_card.html', deck=deck)
