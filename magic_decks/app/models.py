import requests
from flask_login import UserMixin
from .db import getDb

db = getDb()

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cards = db.relationship('Card', backref='deck', lazy=True)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100))
    mana_cost = db.Column(db.String(50))
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False)

    def __init__(self, name, type, mana_cost, deck_id):
        self.name = name
        self.type = type
        self.mana_cost = mana_cost
        self.deck_id = deck_id


    def add_card(self, card):
        self.cards.append(card)

def fetch_card_info(card_name):
    response = requests.get(f'https://api.scryfall.com/cards/named?fuzzy={card_name}')
    if response.status_code == 200:
        return response.json()
    else:
        return None

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    decks = db.relationship('Deck', backref='owner', lazy=True)