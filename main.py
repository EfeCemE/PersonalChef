from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

openai.api_key = '' #put the api key here but be careful with the reference

# Sample dataset
dataset = {
    "ingredients": ["chicken", "beef", "pasta", "tomato", "onion", "garlic", "carrot", "potato", "pepper", "cheese"],
    "cuisines": ["Italian", "Chinese", "Mexican", "Indian", "French", "Japanese"],
    "meal_types": ["breakfast", "lunch", "dinner", "snack"]
}

def filter_user_input(user_input, valid_options):
    return [item.strip() for item in user_input.split(',') if item.strip() in valid_options]

def get_recipe_recommendation(ingredients, exclude_ingredients, cuisine, meal_type):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that provides recipe recommendations."},
        {"role": "user", "content": (
            f"I have the following ingredients: {', '.join(ingredients)}.\n"
            f"Please exclude these ingredients: {', '.join(exclude_ingredients)}.\n"
            f"I prefer {cuisine} cuisine for {meal_type}.\n"
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

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data['message']

    parts = user_message.split(';')
    user_ingredients = parts[0].split(':')[1].strip()
    user_exclude_ingredients = parts[1].split(':')[1].strip()
    user_cuisine = parts[2].split(':')[1].strip()
    user_meal_type = parts[3].split(':')[1].strip()

    ingredients = filter_user_input(user_ingredients, dataset["ingredients"])
    exclude_ingredients = filter_user_input(user_exclude_ingredients, dataset["ingredients"])
    cuisine = user_cuisine if user_cuisine in dataset["cuisines"] else None
    meal_type = user_meal_type if user_meal_type in dataset["meal_types"] else None

    if not ingredients or not cuisine or not meal_type:
        return jsonify({"response": "Invalid input provided."})

    recipe = get_recipe_recommendation(ingredients, exclude_ingredients, cuisine, meal_type)
    return jsonify({"response": recipe})

if __name__ == "__main__":
    app.run(debug=True)
