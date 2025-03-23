from flask import Flask, render_template_string
import random

app = Flask(__name__)

# List of fun facts
FUN_FACTS = [
    "Bananas are berries, but strawberries aren't.",
    "Octopuses have three hearts.",
    "Honey never spoils. Archaeologists have found edible honey in ancient Egyptian tombs.",
    "Wombat poop is cube-shaped.",
    "Sharks existed before trees.",
    "There are more stars in the universe than grains of sand on Earth.",
    "A group of flamingos is called a 'flamboyance'.",
    "The dot over a lowercase 'i' or 'j' is called a tittle.",
    "Sloths can hold their breath longer than dolphins.",
    "Cats have fewer toes on their back paws."
    "Bananas are berries, but strawberries aren't.",
    "A day on Venus is longer than a year on Venus. It takes Venus 243 Earth days to rotate once but only 225 Earth days to orbit the Sun.",
    "Octopuses have three hearts. Two pump blood to the gills, while the third pumps it to the rest of the body.",
    "The Eiffel Tower can be 15 cm taller during the summer due to the expansion of iron in the heat.",
    "There are more stars in the universe than grains of sand on all the Earth's beaches.",
    "A group of flamingos is called a 'flamboyance'.",
    "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.",
    "Humans share 60 percent of their DNA with bananas."
]

# Home route


@app.route('/')
def home():
    # Pick a random fun fact
    fun_fact = random.choice(FUN_FACTS)
    # Simple HTML template
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fun Fact Generator</title>
        <style>
            body {

                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background-color: #0F2027;
                color: white;
            }
            .fact {
                font-size: 24px;
                margin-top: 40px;
                font-family: calibri;
            }
            .button {
                margin-top: 60px;
                font-size: 18px;
                padding: 10px 20px;
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            .button:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <h1>Random Fact Generator</h1>
        <div class="fact">{{ fact }}</div>
        <form method="get">
            <button class="button" type="submit">Generate Another Fact</button>
        </form>
    </body>
    </html>
    """
    # Render the template with the random fact
    return render_template_string(html_template, fact=fun_fact)


if __name__ == '__main__':
    app.run(debug=True)
