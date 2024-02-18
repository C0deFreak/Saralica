from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Definiranje modela korisnika
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)  # Email korisnika, jedinstveni
    password = db.Column(db.String(150))             # Hashirana lozinka korisnika
    username = db.Column(db.String(150))             # Korisničko ime korisnika
    definitions = db.relationship('Definition')      # Veza s pojmovima koje je korisnik stvorio

# Definiranje modela pojma
class Definition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)     # Naziv pojma
    description = db.Column(db.String(1100), nullable=False)  # Opis pojma
    subject = db.Column(db.String(30), nullable=False)  # Predmet pojma
    date_created = db.Column(db.DateTime, default=func.now())  # Datum stvaranja pojma
    bookmark = db.Column(db.Boolean, default=False)      # Oznaka zabilježenosti pojma
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Vanjski ključ koji povezuje pojam s korisnikom
