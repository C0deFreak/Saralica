from flask import Blueprint, render_template, request, flash, redirect, session
from .models import Definition
from flask_login import login_required, current_user
from . import db

# Stvaranje Blueprinta za povezivanje rutiranja
views = Blueprint('views', __name__)

# Postavljanje globalnih varijabli
create_post = False  # Ova varijabla označava da li je korisnik na stranici za kreiranje pojma
def_search = ''      # Ova varijabla čuva rezultate pretrage

# Prikazuje početnu stranicu sa svim pojmovima
@views.route('/', methods=['POST', 'GET'])
@login_required
def index():
    if request.method == 'POST':
        global def_search
        def_search = request.form['search']
        try:
            return redirect('/pretraga')
        except:
            return 'Error: Pretraga neuspješna :('
    else:
        # Renderiranje templatea index.html s odgovarajućim podacima
        return render_template('index.html', create_post=create_post, user=current_user)

# Otvara stranicu za kreiranje novg pojma
@views.route('/otvaranje')
@login_required
def open():
    global create_post
    create_post = True
    return redirect('/')

# Otvara stranicu za uređivanje postojećeg pojma
@views.route('/uređivanje/<int:id>', methods=['GET', 'POST'])
@login_required
def open_edit(id):
    def_to_edit = Definition.query.get_or_404(id)

    # Provjera da li je korisnik vlasnik pojma koju želi urediti
    if def_to_edit.user_id == current_user.id:
        if request.method == 'POST':
            # Ažuriranje informacija o pojmu na temelju korisničkog unosa
            def_to_edit.description = request.form['description']
            def_to_edit.name = request.form['name']
            def_to_edit.subject = request.form['subject']

            # Provjera valjanosti unosa
            if len(def_to_edit.description) == 0:
                flash('Nadupunite opis', category='error')
                return redirect(f'/uređivanje/{id}')
            elif len(def_to_edit.name) == 0:
                flash('Nadupunite ime', category='error')
                return redirect(f'/uređivanje/{id}')
            elif len(def_to_edit.subject) == 0:
                flash('Nadupunite predmet', category='error')
                return redirect(f'/uređivanje/{id}')
            else:
                try:
                    db.session.commit()
                    flash('Uspješno uređen pojam', category='success')
                    return redirect(f'/pojam/{id}')

                except:
                    return 'Error: Uređivanje neuspješno :('

        else:
            return render_template('update.html', definition=def_to_edit, user=current_user)
    else:
        return 'Error: Nije pronađen pojam :('

# Zatvara stranicu za kreiranje ili uređivanje pojmova
@views.route('/zatvaranje')
@login_required
def close():
    global create_post
    create_post = False
    return redirect('/')

# Kreira novi pojam
@views.route('/izrada', methods=['POST', 'GET'])
@login_required
def create():
    if request.method == 'POST':
        # Dobivanje podataka o novom pojmu iz formulara
        description = request.form['description']
        name = request.form['name']
        subject = request.form['subject']

        # Provjera valjanosti unosa
        if len(description) == 0:
            flash('Nadupunite opis', category='error')
            return redirect('/')
        elif len(name) == 0:
            flash('Nadupunite ime', category='error')
            return redirect('/')
        elif len(subject) == 0:
            flash('Nadupunite predmet', category='error')
            return redirect('/')
        else:
            try:
                # Stvaranje nove instance definicije i dodavanje u bazu podataka
                new_def = Definition(description=description, name=name, subject=subject, user_id=current_user.id)
                db.session.add(new_def)
                db.session.commit()
                flash('Uspješno izrađen pojam', category='success')
                return redirect('/zatvaranje')
            except:
                return 'Error: Izrada neuspješna :('

    else:
        return render_template('index.html')

# Prikazuje stranicu sa rezultatima pretrage
@views.route('/pretraga')
@login_required
def search():
    global def_search
    global isFound
    isFound = False

    for definition in current_user.definitions:
        if (def_search.lower() in definition.name.lower()) or (def_search.lower() in definition.subject.lower()):
            isFound = True

    return render_template('search.html', search=def_search, isFound=isFound, user=current_user)

# Prikaz zabilježenih pojmova
@views.route('/zabilježeno')
@login_required
def marked():
    definitions = current_user.definitions
    bookmarked = []

    for definition in definitions:
        if definition.bookmark:
            bookmarked.append(definition)

    if len(bookmarked) < 1:
        return 'Error: Nema zabilježenih pojmova :('

    else:
        return render_template('marked.html', bookmarked=bookmarked, user=current_user)

# Briše pojam
@views.route('/brisanje/<int:id>')
@login_required
def delete(id):
    def_to_delete = Definition.query.get_or_404(id)

    if def_to_delete.user_id == current_user.id:
        try:
            db.session.delete(def_to_delete)
            db.session.commit()
            return redirect('/zatvaranje')
        except:
            return 'Error: Brisanje neuspješno :('
    else:
        return 'Error: Nije pronađen pojam :('
    

# Označava pojmova kao omiljenu ili uklanja oznaku
@views.route('/označivanje/<int:id>')
@login_required
def bookmark(id):
    def_to_mark = Definition.query.get_or_404(id)

    if def_to_mark.user_id == current_user.id:
        try:
            if def_to_mark.bookmark:
                def_to_mark.bookmark = False
            else:
                def_to_mark.bookmark = True
            db.session.commit()
            return redirect(f'/pojam/{id}')
        except:
            return 'Error: Označivanje neuspješno :('
    else:
        return 'Error: Nije pronađen pojam :('
    

# Prikazuje pojedinosti o određenom pojmu
@views.route('/pojam/<int:id>', methods=['GET', 'POST'])
@login_required
def definition(id):
    definition = Definition.query.get(id)
    if definition.user_id == current_user.id:
        return render_template('definition.html', definition=definition, user=current_user)
    else:
        return 'Error: Nije pronađen pojam :('

# Prikazuje flash kartice za omiljene pojmove
@views.route('/flash-kartice')
@login_required
def flash_card():
    definitions = current_user.definitions
    bookmarked = []

    for definition in definitions:
        if definition.bookmark:
            bookmarked.append(definition)

    if len(bookmarked) < 1:
        return 'Error: Nema kartica :('

    if 'bookmark_index' not in session:
        session['bookmark_index'] = len(bookmarked) - 1

    last_picked_index = session['bookmark_index']

    next_index = (last_picked_index - 1) % len(bookmarked)

    session['bookmark_index'] = next_index

    return render_template('flash.html', marked=bookmarked[next_index], user=current_user)

# Prikazuje flash kartice za omiljene pojmove
@views.route('/kviz', methods=['GET', 'POST'])
@login_required
def quiz():
    definitions = current_user.definitions
    bookmarked = [definition for definition in definitions if definition.bookmark]

    if len(bookmarked) < 1:
        return 'Error: Nema zabilježenih pojmova :('

    else:
        if 'current_index' not in session:
            session['current_index'] = 0

        if request.method == 'POST':
            user_answer = request.form.get('user_answer')
            correct_answer = request.form.get('correct_answer')
            if user_answer and correct_answer and user_answer == correct_answer:
                result = "Correct!"
            else:
                result = "Incorrect. Try again."

            return render_template('quiz.html', definitions=[bookmarked[session['current_index']]], result=result, user=current_user)

        session['current_index'] = (session['current_index'] - 1) % len(bookmarked)
        return render_template('quiz.html', definitions=[bookmarked[session['current_index']]], user=current_user)

