from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# Inicijalizacija SQLAlchemy objekta za rad s bazom podataka
db = SQLAlchemy()
DB_NAME = "baza.db"  # Ime baze podataka

# Funkcija za stvaranje Flask aplikacije
def create_app():
    app = Flask(__name__)  # Kreiranje instance Flask aplikacije
    app.config['SECRET_KEY'] = 'chamba machamba'  # Tajni ključ za sesije
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  # URI za SQLite bazu podataka
    db.init_app(app)  # Inicijalizacija SQLAlchemy objekta s aplikacijom

    # Uvoz blueprinta za povezivanje s aplikacijom
    from .views import views
    from .auth import auth

    # Registracija blueprinta s aplikacijom
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth/')

    # Uvoz modela
    from .models import User, Definition

    # Stvaranje baze podataka ako ne postoji
    create_database(app)

    # Inicijalizacija LoginManagera za upravljanje korisničkim sesijama
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Postavljanje rute za prijavu
    login_manager.init_app(app)

    # Funkcija koja se koristi za učitavanje korisnika iz baze podataka
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

# Funkcija za stvaranje baze podataka
def create_database(app):
    if not path.exists('website/' + DB_NAME):  # Provjera postoji li već baza podataka
        with app.app_context():
            db.create_all()  # Stvaranje svih tablica u bazi podataka ako ne postoji
