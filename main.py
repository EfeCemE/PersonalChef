from flask import Flask, request, jsonify, render_template
import openai
import dataset_manager 

app = Flask(__name__)

openai.api_key = '' #put the api key here but be careful with the reference

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
    user_max_time = int(parts[3].split(':')[1].strip()) if len(parts) > 3 and parts[3].split(':')[1].strip().isdigit() else None

    ingredients = dataset_manager.filter_user_input(user_ingredients, [item for sublist in dataset_manager.df['ingredients'].apply(eval).tolist() for item in sublist])
    exclude_ingredients = dataset_manager.filter_user_input(user_exclude_ingredients, [item for sublist in dataset_manager.df['ingredients'].apply(eval).tolist() for item in sublist])
    cuisine = user_cuisine
    
    if not ingredients or not cuisine:
        return jsonify({"response": "Invalid input provided."})

    dataset_managers = dataset_manager.get_dataset_managers(ingredients, exclude_ingredients, cuisine, user_max_time)
    return jsonify({"response": dataset_managers})

if __name__ == "__main__":
    app.run(debug=True)
