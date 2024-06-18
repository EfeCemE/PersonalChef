from flask import Flask, render_template, request, jsonify
import openai
from openai import OpenAI
import os
import time

app = Flask(__name__)

openai.api_key = ''

client = OpenAI(api_key='')

def generate_response(user_message):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"You are a personal chef. You are only giving recipes depending on my input, nothing else. If you understand, say OK."},
                {"role": "system", "content": "OK"},
                {"role": "user", "content": user_message}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"

def retry_with_backoff(func, max_retries=5, backoff_factor=2):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(backoff_factor ** attempt)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def open_chat():
    data = request.get_json()
    user_preference = {
        'time': data.get('time'),
        'meal_type': data.get('meal_type'),
        'cuisine': data.get('cuisine')
    }

    if not user_preference['cuisine']:
        return jsonify({"success": False, "message": "Cuisine selection is required."})

    return jsonify({"success": True})

@app.route('/frontend')
def frontend():
    return app.send_static_file('FrontEnd.html')

@app.route('/chatty', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"response": "Message cannot be empty."})

    try:
        bot_response = retry_with_backoff(lambda: generate_response(user_message))
    except Exception as e:
        bot_response = f"An error occurred after retries: {str(e)}"

    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)

#parts = user_message.split(';')
    #        user_ingredients = parts[0].split(':')[1].strip()
    #    user_exclude_ingredients = parts[1].split(':')[1].strip()
    #   user_cuisine = parts[2].split(':')[1].strip()
    #   user_max_time = int(parts[3].split(':')[1].strip()) if len(parts) > 3 and parts[3].split(':')[
    #       1].strip().isdigit() else None
    #except (IndexError, ValueError):
    #   return jsonify({"response": "Invalid message format."})

    #ingredients = dataset_manager.filter_user_input(user_ingredients, [item for sublist in
    #                                                                   dataset_manager.df['ingredients'].apply(
    #                                                                       eval).tolist() for item in sublist])
    #exclude_ingredients = dataset_manager.filter_user_input(user_exclude_ingredients, [item for sublist in
     #                                                                                  dataset_manager.df[
     #                                                                                      'ingredients'].apply(
     #                                                                                      eval).tolist() for item in
      #                                                                                 sublist])
    #cuisine = user_cuisine

    #if not ingredients or not cuisine:
    #    return jsonify({"response": "Invalid input provided."})

    #dataset_managers = dataset_manager.get_dataset_managers(ingredients, exclude_ingredients, cuisine, user_max_time)
    #return jsonify({"response": dataset_managers})
