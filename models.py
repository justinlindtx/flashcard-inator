# all ORM models go here - User, FlashcardSet, Flashcard, CardData

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), unique=True, nullable=False)
	password = db.Column(db.String(255), nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.now)
	sets = db.relationship('FlashcardSet', back_populates='user', cascade='all, delete')

class FlashcardSet(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	title = db.Column(db.String, default="New Set")
	description = db.Column(db.String)
	created_at = db.Column(db.DateTime, default=datetime.now)
	last_updated = db.Column(db.DateTime, default=datetime.now)
	user = db.relationship('User', back_populates='sets')
	cards = db.relationship('Flashcard', back_populates='flashcard_set', cascade='all, delete')

class Flashcard(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	set_id = db.Column(db.Integer, db.ForeignKey('flashcard_set.id'), nullable=False)
	front_text = db.Column(db.String, nullable=False)
	back_text = db.Column(db.String, nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.now)
	flashcard_set = db.relationship('FlashcardSet', back_populates='cards')
	learning_data = db.relationship('CardData', back_populates='flashcard', cascade='all, delete')

class CardData(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	flashcard_id = db.Column(db.Integer, db.ForeignKey('flashcard.id'), nullable=False)
	repetitions = db.Column(db.Integer, default=0)
	times_correct = db.Column(db.Integer, default=0)
	flashcard = db.relationship('Flashcard', back_populates='learning_data')