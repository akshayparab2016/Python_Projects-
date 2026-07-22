from flask import Flask, render_template
import requests

app = Flask(__name__)

# Home route
@app.route('/')
def home():
    is_error = False
    try:
        url = "https://uselessfacts.jsph.pl/api/v2/facts/random"
        response = requests.get(url, timeout=5)
        data = response.json()
        fact = data.get("text", "No fact available.")
    except Exception:
        is_error = True
        fact = "Unable to fetch a fact right now. Please try again."
    return render_template("index.html", fact=fact, is_error=is_error)

if __name__ == '__main__':
    app.run()
