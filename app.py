from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
dbTerms = SQLAlchemy(app)

class TermSite(dbTerms.Model):
    id = dbTerms.Column(dbTerms.Integer, primary_key=True)
    name = dbTerms.Column(dbTerms.String(100), nullable=False, default='bruh')
    content = dbTerms.Column(dbTerms.String(200), nullable=False)
    author = dbTerms.Column(dbTerms.String(50), nullable=False, default='bruh')
    language = dbTerms.Column(dbTerms.String(25), nullable=False, default='bruh')
    date_created = dbTerms.Column(dbTerms.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Site %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            return redirect('/create')
        except:
            return 'There creating your site!'

    else:

        sitesNum = TermSite.query.count()
        return render_template('index.html', sitesNum = sitesNum)

@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        site_content = request.form['content']
        new_site = TermSite(content=site_content)

        try:
            dbTerms.session.add(new_site)
            dbTerms.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        sites = TermSite.query.order_by(TermSite.date_created).all()
        return render_template('create.html', sites = sites)

@app.route('/delete/<int:id>')
def delete(id):
    site_to_delete = TermSite.query.get_or_404(id)

    try:
        dbTerms.session.delete(site_to_delete)
        dbTerms.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that site'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    site = TermSite.query.get_or_404(id)

    if request.method == 'POST':
        site.content = request.form['content']

        try:
            dbTerms.session.commit()
            return redirect('/')

        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', site=site)

if __name__ == "__main__":
    app.run(debug=True)