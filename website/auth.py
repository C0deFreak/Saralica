from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

# Blueprint za autentikaciju
auth = Blueprint('auth', __name__)

# Rutina za prijavu korisnika
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Pronalaženje korisnika u bazi podataka po emailu
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):  # Provjera lozinke
                flash('Uspješno si ušao', category='success')
                login_user(user, remember=True)  # Prijavljivanje korisnika
                return redirect(url_for('views.index'))  # Redirekcija na početnu stranicu
            else:
                flash('Kriva lozinka', category='error')
        else:
            flash('Nema korisnika', category='error')

    return render_template("login.html", user=current_user)

# Rutina za odjavu korisnika
@auth.route('/logout')
@login_required
def logout():
    logout_user()  # Odjavljivanje korisnika
    return redirect(url_for('auth.login'))  # Redirekcija na stranicu za prijavu

# Rutina za registraciju novog korisnika
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Korisnik već postoji', category='error')
        elif len(email) < 4:
            flash('Nepostojeća E-mail adresa', category='error')
        elif len(username) < 2:
            flash('Korisničko ime je prekratko', category='error')
        elif password1 != password2:
            flash('Lozinke se ne podudaraju', category='error')
        elif len(password1) < 7:
            flash('Lozinka je prekratka', category='error')
        else:
            # Stvaranje novog korisnika i spremanje u bazu podataka
            new_user = User(email=email, username=username, password=generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)  # Prijavljivanje novog korisnika
            flash('Uspjeh', category='success')
            return redirect('/zatvaranje')  # Redirekcija na zatvaranje (možda bi trebalo biti url_for('views.close'))

    return render_template("sign_up.html", user=current_user)
