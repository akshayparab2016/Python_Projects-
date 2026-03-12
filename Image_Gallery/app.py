from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import requests

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gallery.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# 👉 Add your Unsplash API Key here
UNSPLASH_ACCESS_KEY = 'Ju8EoHoB2zM_BP7mHwJt8pOFwumTRwW5_6Jz8fEd2s8'

# ---------------------------
# DATABASE MODELS
# ---------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------------
# HOME + SEARCH PAGE
# ---------------------------
@app.route("/", methods=["GET","POST"])
def home():
    import random
    query = request.args.get("query")
    images = []
    no_results = False

    # Get page from query param
    page = request.args.get("page", type=int)

    if query:
        # For search, default page = 1
        if not page:
            page = 1
    else:
        # For home page (no query), pick a random page
        if not page:
            page = random.randint(1, 50)

    try:
        if query:
            # Search photos
            url = f"https://api.unsplash.com/search/photos?query={query}&page={page}&per_page=15&client_id={UNSPLASH_ACCESS_KEY}"
            r = requests.get(url)
            data = r.json()
            results = data.get("results", [])
            if not results:
                no_results = True
            else:
                for img in results:
                    images.append(img["urls"]["regular"])
        else:
            # Latest photos for home page with random page
            url = f"https://api.unsplash.com/photos?page={page}&per_page=15&order_by=latest&client_id={UNSPLASH_ACCESS_KEY}"
            r = requests.get(url)
            data = r.json()
            for img in data:
                images.append(img["urls"]["regular"])
    except Exception as e:
        print(e)
        no_results = True

    return render_template(
        "search.html",
        images=images,
        query=query,
        no_results=no_results,
        page=page
    )
# ---------------------------
# REGISTER
# ---------------------------

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("✅ Registration successful!")
        return redirect(url_for("login"))
    return render_template("register.html")

# ---------------------------
# LOGIN
# ---------------------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            flash("✅ User Logged in successfully!")
            return redirect(url_for("gallery"))
        else:
            flash("❌ Invalid credentials!")
    return render_template("login.html")

# ---------------------------
# LOGOUT
# ---------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("🔒 User Logged out successfully!")
    return redirect(url_for("home"))

# ---------------------------
# SAVE IMAGE (LOGIN REQUIRED)
# ---------------------------
@app.route("/save")
@login_required
def save():
    url = request.args.get("url")
    image = Image(url=url, user_id=current_user.id)
    db.session.add(image)
    db.session.commit()
    flash("💾 Image saved to gallery!")
    return redirect(url_for("gallery"))

# ---------------------------
# USER GALLERY
# ---------------------------
@app.route("/gallery")
@login_required
def gallery():
    images = Image.query.filter_by(user_id=current_user.id).all()
    return render_template("gallery.html", images=images)

# ---------------------------
# DELETE IMAGE
# ---------------------------
@app.route("/delete/<int:id>")
@login_required
def delete(id):
    image = Image.query.get(id)
    if image.user_id == current_user.id:
        db.session.delete(image)
        db.session.commit()
    flash("🗑️ Image deleted!")
    return redirect(url_for("gallery"))

# ---------------------------
@app.route("/load")
def load():
    page = request.args.get("page", 1, type=int)
    query = request.args.get("query")
    images = []
    if query:
        url = f"https://api.unsplash.com/search/photos?query={query}&page={page}&per_page=15&client_id={UNSPLASH_ACCESS_KEY}"
        r = requests.get(url)
        data = r.json()
        for img in data["results"]:
            images.append(img["urls"]["regular"])

    else:
        url = f"https://api.unsplash.com/photos?page={page}&per_page=15&client_id={UNSPLASH_ACCESS_KEY}"
        r = requests.get(url)
        data = r.json()
        for img in data:
            images.append(img["urls"]["regular"])
    return {"images": images}
# ---------------------------
# RUN
# ---------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()