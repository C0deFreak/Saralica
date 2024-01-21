from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
functionDatabase = SQLAlchemy(app)

create_post = False  # Postavljanje globalne promenljive create_post
title = 'Šaralica'  # Postavljanje globalne promenljive title
func_search = ''  # Inicijalizacija globalne promenljive func_search

# Definisanje modela za funkcije sajtova u bazi podataka
class FunctionSite(functionDatabase.Model):
    id = functionDatabase.Column(functionDatabase.Integer, primary_key=True)
    name = functionDatabase.Column(functionDatabase.String(30), nullable=False, default=' ')
    description = functionDatabase.Column(functionDatabase.String(600), nullable=False, default=' ')
    language = functionDatabase.Column(functionDatabase.String(12), nullable=False, default=' ')
    date_created = functionDatabase.Column(functionDatabase.DateTime, default=datetime.utcnow)
    bookmark = functionDatabase.Column(functionDatabase.Boolean, default=False)

    def __repr__(self):
        return '<Site %r>' % self.id

# Prikazuje početnu stranicu sa svim funkcijama
@app.route('/', methods=['POST', 'GET'])
def index():
    functions = FunctionSite.query.order_by(FunctionSite.name).all()
    card_generated = False

    for function in functions:
        if function.bookmark:
            if not card_generated:
                card_generated = True

    if request.method == 'POST':
        global func_search
        func_search = request.form['search']
        try:
            return redirect('/pretraga')
        except:
            return 'Error: Pretraga neuspješna :('

    else:
        return render_template('index.html', create_post=create_post, title=title, functions=functions, generated=card_generated)

# Otvara stranicu za kreiranje nove funkcije
@app.route('/otvaranje')
def open():
    global create_post, title
    create_post = True
    title = 'Izrada'
    return redirect('/')

# Otvara stranicu za uređivanje postojeće funkcije
@app.route('/uređivanje/<int:id>', methods=['GET', 'POST'])
def open_edit(id):
    function_to_edit = FunctionSite.query.get_or_404(id)

    if request.method == 'POST':
        function_to_edit.description = request.form['description']
        function_to_edit.name = request.form['name']
        function_to_edit.language = request.form['language']

        try:
            functionDatabase.session.commit()
            return redirect('/')

        except:
            return 'Error: Uređivanje neuspješno :('

    else:
        return render_template('update.html', function=function_to_edit)

# Zatvara stranicu za kreiranje ili uređivanje funkcije
@app.route('/zatvaranje')
def close():
    global create_post, title
    create_post = False
    title = 'Šaralica'
    return redirect('/')

# Kreira novu funkciju
@app.route('/izrada', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        func_description = request.form['description']
        func_name = request.form['name']
        func_language = request.form['language']
        new_func = FunctionSite(description=func_description, name=func_name, language=func_language)

        try:
            functionDatabase.session.add(new_func)
            functionDatabase.session.commit()
            return redirect('/zatvaranje')
        except:
            return 'Error: Izrada neuspješna :('

    else:
        return render_template('index.html', functions=functions)

# Prikazuje stranicu sa rezultatima pretrage
@app.route('/pretraga')
def search():
    global func_search
    global isFound
    isFound = False
    functions = FunctionSite.query.order_by(FunctionSite.name).all()

    for function in functions:
        if (func_search.lower() in function.name.lower()) or (func_search.lower() in function.language.lower()):
            isFound = True

    return render_template('search.html', search=func_search, functions=functions, isFound=isFound)

# Briše funkciju
@app.route('/brisanje/<int:id>')
def delete(id):
    function_to_delete = FunctionSite.query.get_or_404(id)

    try:
        functionDatabase.session.delete(function_to_delete)
        functionDatabase.session.commit()
        return redirect('/')
    except:
        return 'Error: Brisanje neuspješno :('

# Označava funkciju kao omiljenu ili uklanja oznaku
@app.route('/označivanje/<int:id>')
def bookmark(id):
    function_to_mark = FunctionSite.query.get_or_404(id)

    try:
        if function_to_mark.bookmark:
            function_to_mark.bookmark = False
        else:
            function_to_mark.bookmark = True
        functionDatabase.session.commit()
        return redirect('/')
    except:
        return 'Error: Označivanje neuspješno :('

# Prikazuje pojedinosti o određenoj funkciji
@app.route('/definicija/<int:id>', methods=['GET', 'POST'])
def function(id):
    function = FunctionSite.query.get_or_404(id)
    return render_template('function.html', function=function)

# Prikazuje flash kartice za omiljene funkcije
@app.route('/flash-kartice')
def flash():
    functions = FunctionSite.query.order_by(FunctionSite.name).all()
    card_generated = False
    bookmarked = []
    marked = 0

    for function in functions:
        if function.bookmark:
            if not card_generated:
                card_generated = True
            bookmarked.append(function)
            marked = random.choice(bookmarked)

    if not card_generated:
        return 'Error: Nema kartica :('

    else:
        return render_template('flash.html', marked=marked)

# Ako se fajl pokreće direktno (a ne kao import u drugom fajlu)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=2412, debug=True)
