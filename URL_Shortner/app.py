from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import string, random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # For flash messages

db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(10), unique=True, nullable=False)

def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=6))

with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form['original_url']
        existing_url = URL.query.filter_by(original_url=original_url).first()
        if existing_url:
            flash('URL already shortened!', 'info')
            return render_template('index.html', short_url=request.host_url + existing_url.short_url, urls=URL.query.all())
        
        short_url = generate_short_url()
        new_url = URL(original_url=original_url, short_url=short_url)
        db.session.add(new_url)
        db.session.commit()
        return render_template('index.html', short_url=request.host_url + short_url, urls=URL.query.all())
    
    return render_template('index.html', urls=URL.query.all())

@app.route('/<short_url>')
def redirect_url(short_url):
    url_entry = URL.query.filter_by(short_url=short_url).first()
    if url_entry:
        return redirect(url_entry.original_url)
    else:
        flash('Invalid URL!', 'danger')
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
