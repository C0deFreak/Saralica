from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
functionDatabase = SQLAlchemy(app)

create_post = False
title = '~/Scriptopedia'


class FunctionSite(functionDatabase.Model):
    id = functionDatabase.Column(functionDatabase.Integer, primary_key=True)
    name = functionDatabase.Column(functionDatabase.String(12), nullable=False, default='bruh')
    description = functionDatabase.Column(functionDatabase.String(600), nullable=False)
    author = functionDatabase.Column(functionDatabase.String(20), nullable=False, default='bruh')
    language = functionDatabase.Column(functionDatabase.String(25), nullable=False, default='bruh')
    date_created = functionDatabase.Column(functionDatabase.DateTime, default=datetime.utcnow)


    def __repr__(self):
        return '<Site %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            return redirect('/search')
        except:
            return 'There creating your site!'

    else:
        return render_template('index.html', create_post=create_post, title=title)

@app.route('/create')
def create():
    global create_post, title
    create_post = True
    title = '~/Scriptopedia/make'
    return redirect('/')

@app.route('/close')
def close():
    global create_post, title
    create_post = False
    title = '~/Scriptopedia'
    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    site_to_delete = FunctionSite.query.get_or_404(id)

    try:
        functionDatabase.session.delete(site_to_delete)
        functionDatabase.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that site'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    site = FunctionSite.query.get_or_404(id)

    if request.method == 'POST':
        site.content = request.form['content']

        try:
            functionDatabase.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', site=site)

if __name__ == "__main__":
    app.run(debug=True)