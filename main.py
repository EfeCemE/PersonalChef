from flask import Flask, request, jsonify, render_template
import openai
import ingredients_cuisine_dataset

app = Flask(__name__)

openai.api_key = '' #put the api key here but be careful with the reference


def filter_user_input(user_input, valid_options):
    return [item.strip() for item in user_input.split(',') if item.strip() in valid_options]

def get_recipe_recommendation(ingredients, exclude_ingredients, cuisine, meal_type):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that provides recipe recommendations."},
        {"role": "user", "content": (
            f"I have the following ingredients: {', '.join(ingredients)}.\n"
            f"Please exclude these ingredients: {', '.join(exclude_ingredients)}.\n"
            f"I prefer {cuisine}.\n"
            f"Can you suggest a recipe for me?")
         }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150
    )

    recipe = response['choices'][0]['message']['content'].strip()
    return recipe

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/chat', methods = ['POST'])
def open_chat():
    data = request.get_json()
    user_preference = data['user_prefrence']

    user_ingredients = user_preference['ingredients']
    user_exclude_ingredients = []
    user_cuisine = user_preference['cuisine']

    ingredients = ingredients_cuisine_dataset.filter_user_input(user_ingredients, ingredients_cuisine_dataset.df['ingredients'].tolist())
    exclude_ingredients = ingredients_cuisine_dataset.filter_user_input(user_exclude_ingredients, ingredients_cuisine_dataset.df['ingredients'].tolist())
    cuisine = user_cuisine

    if not ingredients or not cuisine:
        return jsonify({"response": "Invalid input provided."})

    recipe_id = ingredients_cuisine_dataset.get_recipe_recommendations(ingredients, exclude_ingredients, cuisine)
    
    return jsonify({"response": recipe_id})

@app.route('/chatty', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data['message']

    parts = user_message.split(';')
    user_ingredients = parts[0].split(':')[1].strip()
    user_exclude_ingredients = parts[1].split(':')[1].strip()
    user_cuisine = parts[2].split(':')[1].strip()

    ingredients = ingredients_cuisine_dataset.filter_user_input(user_ingredients, ingredients_cuisine_dataset.df['ingredients'].tolist())
    exclude_ingredients = ingredients_cuisine_dataset.filter_user_input(user_exclude_ingredients, ingredients_cuisine_dataset.df['ingredients'].tolist())
    cuisine = user_cuisine
    
    if not ingredients or not cuisine:
        return jsonify({"response": "Invalid input provided."})

    recipe_id = ingredients_cuisine_dataset.get_recipe_recommendations(ingredients, exclude_ingredients, cuisine)
    return jsonify({"response": recipe_id})

if __name__ == "__main__":
    app.run(debug=True)
