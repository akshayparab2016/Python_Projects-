from flask import Flask, render_template, request
import random
import string

app = Flask(__name__)

def generate_password(length, use_alphabets, use_numbers, use_specials):
    characters = ""
    
    if use_alphabets:
        characters += string.ascii_letters
    if use_numbers:
        characters += string.digits
    if use_specials:
        characters += string.punctuation

    if not characters:
        return "Please select at least one option!"

    return ''.join(random.choice(characters) for _ in range(length))

@app.route("/", methods=["GET", "POST"])
def index():
    password = ""
    if request.method == "POST":
        try:
            length = int(request.form["length"])
            use_alphabets = "alphabets" in request.form
            use_numbers = "numbers" in request.form
            use_specials = "specials" in request.form

            if length < 1 or length > 100:
                password = "Invalid length! Choose between 1 and 99."
            else:
                password = generate_password(length, use_alphabets, use_numbers, use_specials)

        except ValueError:
            password = "Invalid input!"

    return render_template("index.html", password=password)

if __name__ == "__main__":
    app.run()
