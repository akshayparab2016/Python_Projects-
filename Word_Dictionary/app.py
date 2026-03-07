from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"

@app.route('/', methods=['GET', 'POST'])
def index():
    meanings = None
    error = None
    if request.method == 'POST':
        word = request.form.get('word')
        if word:
            try:
                response = requests.get(API_URL + word)
                data = response.json()
                if response.status_code == 200:
                    meanings = data
                else:
                    error = "Word not found. Please try another word."
            except:
                error = "API Error. Try again later."
        else:
            error = "Please enter a word."
    return render_template("index.html", meanings=meanings, error=error)


if __name__ == "__main__":
    app.run()