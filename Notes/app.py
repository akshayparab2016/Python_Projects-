from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SECRET_KEY"] = "secret123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"

db = SQLAlchemy(app)


# ------------------ MODELS ------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


with app.app_context():
    db.create_all()


# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return render_template("index.html")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        user = User.query.filter_by(username=username).first()

        if user:
            flash("Username already exists")
            return redirect(url_for("register"))

        new_user = User(username=username, password=password)

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully")

        return redirect(url_for("login"))

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login successful")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password")
    return render_template("login.html")


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully")
    return redirect(url_for("home"))


# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    notes = Note.query.filter_by(user_id=session["user_id"]).all()
    return render_template("dashboard.html", notes=notes)


# CREATE NOTE
@app.route("/create_note", methods=["GET", "POST"])
def create_note():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]
        content = request.form["content"]

        note = Note(
            title=title,
            content=content,
            user_id=session["user_id"]
        )

        db.session.add(note)
        db.session.commit()
        flash("Note created successfully")
        return redirect(url_for("dashboard"))
    return render_template("create_note.html")


# EDIT NOTE
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    note = Note.query.get_or_404(id)
    if request.method == "POST":
        note.title = request.form["title"]
        note.content = request.form["content"]
        db.session.commit()
        flash("Note updated")
        return redirect(url_for("dashboard"))
    return render_template("edit_note.html", note=note)


# DELETE NOTE
@app.route("/delete/<int:id>")
def delete(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    flash("Note deleted")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run()
    
    