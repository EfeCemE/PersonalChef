from flask import Flask, render_template, request, jsonify, redirect, url_for
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
    user_preference = {
        'time': data.get('time'),
        'meal_type': data.get('meal_type'),
        'cuisine': data.get('cuisine')
    }

    if not user_preference['cuisine']:
        return jsonify({"success": False, "message": "Cuisine selection is required."})

    # Process the user preferences (e.g., save to session or database)

    return jsonify({"success": True})
    return redirect(url_for('frontend'))

@app.route('/frontend')
def frontend():
    return app.send_static_file('FrontEnd.html')

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
