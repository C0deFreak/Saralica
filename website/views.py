from flask import Blueprint, render_template, request, flash, redirect, jsonify
from .models import Definition
from flask_login import login_required, current_user
from . import db
import random

views = Blueprint('views', __name__)
create_post = False  # Postavljanje globalne promenljive create_post
def_search = ''  # Inicijalizacija globalne promenljive func_search

# Prikazuje početnu stranicu sa svim funkcijama
@views.route('/', methods=['POST', 'GET'])
@login_required
def index():

    card_generated = False

    for definition in current_user.definitions:
        if definition.bookmark and definition.user_id == current_user.id:
            if not card_generated:
                card_generated = True

    if request.method == 'POST':
        global def_search
        def_search = request.form['search']
        try:
            return redirect('/pretraga')
        except:
            return 'Error: Pretraga neuspješna :('

    else:
        return render_template('index.html', create_post=create_post, generated=card_generated, user=current_user)

# Otvara stranicu za kreiranje nove funkcije
@views.route('/otvaranje')
@login_required
def open():
    global create_post
    create_post = True
    return redirect('/')

# Otvara stranicu za uređivanje postojeće funkcije
@views.route('/uređivanje/<int:id>', methods=['GET', 'POST'])
@login_required
def open_edit(id):
    def_to_edit = Definition.query.get_or_404(id)

    if def_to_edit.user_id == current_user.id:
        if request.method == 'POST':
            def_to_edit.description = request.form['description']
            def_to_edit.name = request.form['name']
            def_to_edit.subject = request.form['subject']

            try:
                db.session.commit()
                return redirect('/')

            except:
                return 'Error: Uređivanje neuspješno :('

        else:
            return render_template('update.html', definition=def_to_edit, user=current_user)
    else:
        return 'Error: Nije pronađena definicija :('
    

# Zatvara stranicu za kreiranje ili uređivanje funkcije
@views.route('/zatvaranje')
@login_required
def close():
    global create_post
    create_post = False
    return redirect('/')

# Kreira novu funkciju
@views.route('/izrada', methods=['POST', 'GET'])
@login_required
def create():
    if request.method == 'POST':
        description = request.form['description']
        name = request.form['name']
        subject = request.form['subject']
        new_def = Definition(description=description, name=name, subject=subject, user_id=current_user.id)

        try:
            db.session.add(new_def)
            db.session.commit()
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


@views.route('/zabilježeno')
@login_required
def marked():
    definitions = current_user.definitions
    bookmarked = []

    for definition in definitions:
        if definition.bookmark:
            bookmarked.append(definition)

    if len(bookmarked) < 1:
        return 'Error: Nema kartica :('

    else:
        return render_template('marked.html', bookmarked=bookmarked, user=current_user)

# Briše funkciju
@views.route('/brisanje/<int:id>')
@login_required
def delete(id):
    def_to_delete = Definition.query.get_or_404(id)

    if def_to_delete.user_id == current_user.id:
        try:
            db.session.delete(def_to_delete)
            db.session.commit()
            return redirect('/')
        except:
            return 'Error: Brisanje neuspješno :('
    else:
        return 'Error: Nije pronađena definicija :('
    

# Označava funkciju kao omiljenu ili uklanja oznaku
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
            return redirect('/')
        except:
            return 'Error: Označivanje neuspješno :('
    else:
        return 'Error: Nije pronađena definicija :('
    

# Prikazuje pojedinosti o određenoj funkciji
@views.route('/definicija/<int:id>', methods=['GET', 'POST'])
@login_required
def definition(id):
    definition = Definition.query.get(id)
    if definition.user_id == current_user.id:
        return render_template('definition.html', definition=definition, user=current_user)
    else:
        return 'Error: Nije pronađena definicija :('

# Prikazuje flash kartice za omiljene funkcije
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

    else:
        return render_template('flash.html', marked=random.choice(bookmarked), user=current_user)

# Prikazuje flash kartice za omiljene funkcije
@views.route('/kviz', methods=['GET', 'POST'])
@login_required
def quiz():
    definitions = current_user.definitions
    bookmarked = [definition for definition in definitions if definition.bookmark]

    if len(bookmarked) < 1:
        return 'Error: Nema kartica :('

    else:
        if request.method == 'POST':

            user_answer = request.form.get('user_answer')
            correct_answer = request.form.get('correct_answer')
            if user_answer and correct_answer and user_answer == correct_answer:
                result = "Correct!"
            else:
                result = "Incorrect. Try again."

            return render_template('quiz.html', definitions=[random.choice(bookmarked)], result=result, user=current_user)

        return render_template('quiz.html', definitions=[random.choice(bookmarked)], user=current_user)
