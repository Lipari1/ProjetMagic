import logging
import requests
from .models import Deck, Card, fetch_card_info, User
from .db import getDb
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask import flash, jsonify, render_template, request, redirect, url_for, Blueprint

blueprint = Blueprint('my_blueprint', __name__, template_folder='templates')

db = getDb()

# Route principale : redirige l'utilisateur non authentifié vers la page de connexion
@blueprint.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('my_blueprint.login'))
    first_deck = Deck.query.filter_by(user_id=current_user.id).first()
    if first_deck:
        return redirect(url_for('my_blueprint.view_deck', deck_id=first_deck.id))
    return render_template('deck.html', deck=None)

# Vue d'un deck spécifique (nécessite une authentification)
@blueprint.route('/deck/<deck_id>')
@login_required
def view_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    return render_template('deck.html', deck=deck)

# Ajout d'un deck (nécessite une authentification)

# Suppression d'un deck (nécessite une authentification)

# Ajout d'une carte à un deck (nécessite une authentification)
@blueprint.route('/add_card/<deck_id>', methods=['POST'])
@login_required
def add_card(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    try:
        # Récupérer les données JSON de la requête
        data = request.get_json()
        name = data.get('name')
        type = data.get('type')
        mana_cost = data.get('mana_cost', '')  # Mana cost peut être optionnel
        image_url = data.get('image_url', '')

        # Ajouter des journaux de debug
        logging.info(f"Requête d'ajout de carte reçue : Nom={name}, Type={type}, Mana Cost={mana_cost}, Deck ID={deck.id}, Image URL={image_url}")

        # Vérifier que le nom est présent
        if not name:
            raise ValueError("Le nom de la carte est requis.")

        # Récupérer l'URL de l'image via l'API Scryfall si elle n'est pas fournie
        if not image_url:
            card_info = fetch_card_info(name)
            image_url = card_info['image_uris'].get('normal', '') if card_info and 'image_uris' in card_info else ''

        # Créer une nouvelle carte
        new_card = Card(name=name, type=type, mana_cost=mana_cost, deck_id=deck.id, image_url=image_url)
        db.session.add(new_card)
        db.session.commit()

        logging.info(f"Carte ajoutée : {name} dans le deck {deck.name}")
        return jsonify({'message': 'Carte ajoutée avec succès!'}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Erreur lors de l'ajout de la carte : {e}")
        return jsonify({'error': str(e)}), 400


# Suppression d'une carte spécifique (nécessite une authentification)
@blueprint.route('/delete_card/<deck_id>/<card_name>')
@login_required
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

# Inscription d'un nouvel utilisateur
@blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('Inscription réussie !', 'success')
            return redirect(url_for('my_blueprint.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'inscription : {e}', 'danger')
    return render_template('signup.html')

# Connexion de l'utilisateur
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

# Déconnexion de l'utilisateur (nécessite une authentification)
@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Déconnexion réussie', 'info')
    return redirect(url_for('my_blueprint.login'))

# Recherche de cartes via l'API Scryfall
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
        else:
            return jsonify({'error': 'Scryfall API error', 'status_code': response.status_code, 'message': response.text}), response.status_code
    return jsonify([])


# Mise à jour du deck (nécessite une authentification)
@blueprint.route('/update_deck/<int:deck_id>', methods=['GET', 'POST'])
@login_required
def update_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if request.method == 'POST':
        new_name = request.form['name']
        deck.name = new_name
        try:
            db.session.commit()
            flash('Deck mis à jour avec succès', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la mise à jour du deck : {e}', 'danger')
        return redirect(url_for('my_blueprint.view_deck', deck_id=deck.id))
    return render_template('update_deck.html', deck=deck)

@blueprint.route('/api/decks', methods=['GET'])
@login_required
def get_decks():
    decks = Deck.query.filter_by(user_id=current_user.id).all()
    deck_list = [{'id': deck.id, 'name': deck.name} for deck in decks]
    return jsonify(deck_list)

@blueprint.route('/api/deck/<int:deck_id>/cards', methods=['GET'])
@login_required
def get_deck_cards(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    cards = Card.query.filter_by(deck_id=deck_id).all()
    card_list = [{'id': card.id, 'name': card.name, 'type': card.type, 'mana_cost': card.mana_cost, 'image_url': card.image_url} for card in cards]
    return jsonify(card_list)

@blueprint.route('/api/cards/search', methods=['GET'])
def search_cards_api():
    query = request.args.get('q', '')
    if query:
        cards = Card.query.filter(Card.name.ilike(f'%{query}%')).all()
        results = [{'id': card.id, 'name': card.name, 'type': card.type, 'image_url': card.image_url} for card in cards]
        return jsonify(results)
    return jsonify([])

# Ajouter une carte à un deck (API)
@blueprint.route('/api/deck/<int:deck_id>/add_card', methods=['POST'])
@login_required
def add_card_to_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    card_name = request.json.get('name')
    card_type = request.json.get('type')
    card_image_url = request.json.get('image_url')

    new_card = Card(name=card_name, type=card_type, deck_id=deck.id, image_url=card_image_url)
    db.session.add(new_card)
    db.session.commit()

    return jsonify({'success': True})

# Supprimer une carte d'un deck (API)
@blueprint.route('/api/deck/<int:deck_id>/remove_card/<int:card_id>', methods=['DELETE'])
@login_required
def remove_card_from_deck(deck_id, card_id):
    card = Card.query.get_or_404(card_id)
    if card.deck_id != deck_id or card.deck.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(card)
    db.session.commit()

    return jsonify({'success': True})

# Créer un nouveau deck (API)
@blueprint.route('/api/deck/create', methods=['POST'])
@login_required
def create_deck():
    deck_name = request.json.get('name')
    new_deck = Deck(name=deck_name, user_id=current_user.id)
    db.session.add(new_deck)
    db.session.commit()

    return jsonify({'success': True, 'deck': {'id': new_deck.id, 'name': new_deck.name}})
