from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
functionDatabase = SQLAlchemy(app)

create_post = False
title = 'Šaralica'
func_search = ''


class FunctionSite(functionDatabase.Model):
    id = functionDatabase.Column(functionDatabase.Integer, primary_key=True)
    name = functionDatabase.Column(functionDatabase.String(30), nullable=False, default=' ')
    description = functionDatabase.Column(functionDatabase.String(600), nullable=False, default=' ')
    language = functionDatabase.Column(functionDatabase.String(12), nullable=False, default=' ')
    date_created = functionDatabase.Column(functionDatabase.DateTime, default=datetime.utcnow)
    bookmark = functionDatabase.Column(functionDatabase.Boolean, default=False)


    def __repr__(self):
        return '<Site %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    functions = FunctionSite.query.order_by(FunctionSite.name).all()
    card_generated = False

    for function in functions:
        if function.bookmark and not card_generated:
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

@app.route('/otvaranje')
def open():
    global create_post, title
    create_post = True
    title = 'Izrada'
    return redirect('/')
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


@app.route('/zatvaranje')
def close():
    global create_post, title
    create_post = False
    title = 'Šaralica'
    return redirect('/')

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
            return redirect('/')
        except:
            return 'Error: Izrada neuspješna :('

    else:
        return render_template('index.html', functions=functions)

@app.route('/pretraga')
def search():
    global func_search
    global isFound
    isFound = False
    functions = FunctionSite.query.order_by(FunctionSite.name).all()

    for function in functions:
        if (func_search in function.name or func_search in function.language) or (function.name in func_search or function.language in func_search):
            isFound = True

    return render_template('search.html', search=func_search, functions=functions, isFound=isFound)

@app.route('/brisanje/<int:id>')
def delete(id):
    function_to_delete = FunctionSite.query.get_or_404(id)

    try:
        functionDatabase.session.delete(function_to_delete)
        functionDatabase.session.commit()
        return redirect('/')
    except:
        return 'Error: Brisanje neuspješno :('

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

@app.route('/definicija/<int:id>', methods=['GET', 'POST'])
def function(id):
    function = FunctionSite.query.get_or_404(id)
    return render_template('function.html', function=function)

if __name__ == "__main__":
    app.run(debug=True)
