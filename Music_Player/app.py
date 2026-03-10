from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

API_BASE = "https://discoveryprovider.audius.co/v1"

# ===================== DATABASE MODELS =====================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class PlaylistTrack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    track_id = db.Column(db.String(100), nullable=False)
    track_title = db.Column(db.String(200), nullable=False)
    track_artist = db.Column(db.String(200), nullable=False)
    track_artwork = db.Column(db.String(500), nullable=True)
    track_url = db.Column(db.String(500), nullable=False)

# ===================== LOGIN MANAGER =====================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===================== UTILITY: NORMALIZE TRACKS =====================
def normalize_tracks(tracks):
    normalized = []
    for t in tracks:
        # Get artwork safely
        artwork_data = t.get("artwork", {})
        artwork = artwork_data.get("480x480") or \
                  artwork_data.get("1000x1000") or \
                  artwork_data.get("150x150") or \
                  "/static/noimage.jpg"
        track_id = t.get("id")
        
        # Directly construct the URL instead of fetching it via requests
        playable_url = f"{API_BASE}/tracks/{track_id}/stream?app_name=music_player"

        normalized.append({
            "id": track_id,
            "title": t.get("title", "Unknown Title"),
            "artist": t.get("user", {}).get("name", "Unknown Artist"),
            "artwork": artwork,
            "url": playable_url
        })
    return normalized 

# ===================== ROUTES =====================
@app.route('/')
def home():
    response = requests.get(f"{API_BASE}/tracks/trending?filter=popular")
    tracks = normalize_tracks(response.json().get('data', []))
    return render_template("index.html", tracks=tracks)

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    response = requests.get(f"{API_BASE}/tracks/search?query={query}")
    tracks = normalize_tracks(response.json().get('data', []))
    return render_template("index.html", tracks=tracks, query=query)

# ===================== AUTH =====================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered")
            return redirect(url_for('register'))

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully! Please login.")
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials")
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('home'))
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# ===================== PLAYLISTS =====================
@app.route('/playlists')
@login_required
def playlists():
    user_playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    return render_template("playlists.html", playlists=user_playlists)

@app.route('/playlists/create', methods=['POST'])
@login_required
def create_playlist():
    name = request.form.get('name')
    if name:
        new_playlist = Playlist(name=name, user_id=current_user.id)
        db.session.add(new_playlist)
        db.session.commit()
        flash("Playlist created!")
    return redirect(url_for('playlists'))


@app.route('/playlists/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def playlist_detail(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    # Search form
    query = None
    if request.method == 'POST':
        query = request.form.get('query')
        response = requests.get(f"{API_BASE}/tracks/search?query={query}")
        api_tracks = normalize_tracks(response.json().get('data', []))
    else:
        response = requests.get(f"{API_BASE}/tracks/trending?filter=popular")
        api_tracks = normalize_tracks(response.json().get('data', []))

    # Tracks already added to this playlist
    playlist_tracks = PlaylistTrack.query.filter_by(playlist_id=playlist_id).all()
    
    return render_template(
        "playlist_detail.html",
        playlist=playlist,
        api_tracks=api_tracks,
        playlist_tracks=playlist_tracks,
        query=query
    )


@app.route('/playlists/<int:playlist_id>/add', methods=['POST'])
@login_required
def add_track(playlist_id):
    track_id = request.form.get('track_id')  # optional
    track_title = request.form.get('track_title')
    track_artist = request.form.get('track_artist')
    track_artwork = request.form.get('track_artwork') or '/static/noimage.jpg'
    track_url = request.form.get('track_url') or '#'

    new_track = PlaylistTrack(
        playlist_id=playlist_id,
        track_id=track_id or track_title + track_artist,
        track_title=track_title,
        track_artist=track_artist,
        track_artwork=track_artwork,
        track_url=track_url
    )
    db.session.add(new_track)
    db.session.commit()
    flash("Track added in your playlist!")
    return redirect(url_for('playlist_detail', playlist_id=playlist_id))

# ===================== DELETE PLAYLIST =====================
@app.route('/playlists/<int:playlist_id>/delete', methods=['POST'])
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    
    # Make sure the user owns the playlist
    if playlist.user_id != current_user.id:
        flash("Unauthorized action!")
        return redirect(url_for('playlists'))
    
    # Delete all tracks in this playlist first
    PlaylistTrack.query.filter_by(playlist_id=playlist.id).delete()
    db.session.delete(playlist)
    db.session.commit()
    flash("Playlist deleted successfully!")
    return redirect(url_for('playlists'))

# ===================== remove songs from playlist =====================
@app.route('/playlists/<int:track_id>/remove', methods=['POST'])
@login_required
def remove_track(track_id):
    track = PlaylistTrack.query.get_or_404(track_id)
    db.session.delete(track)
    db.session.commit()
    flash("Track removed from your playlist!")
    return redirect(url_for('playlist_detail', playlist_id=track.playlist_id))
# ===================== RUN =====================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)