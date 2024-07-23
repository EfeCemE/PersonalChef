from flask import Flask, render_template, request, jsonify, session
import openai
import os
import time
import dataset_manager

app = Flask(__name__)

app.secret_key = 'BAD_SECRET_KEY_16851wqdjnjhb'
openai.api_key = ''
# Initialize the OpenAI client with API key
client = openai.OpenAI(api_key='')

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
        'cuisine': data.get('cuisine'),
        'ingredientsOption': data.get('ingredientsOption')
    }

    if not user_preference['cuisine']:
        return jsonify({"success": False, "message": "Cuisine selection is required."})

    session['user_preference'] = user_preference
    session['chat_count'] = 0

    return jsonify({"success": True})

@app.route('/frontend')
def frontend():
    return app.send_static_file('FrontEnd.html')

@app.route('/chatty', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    bot_response = ''

    if not user_message:
        return jsonify({'success': False, 'message': 'No message provided'})

     # to clear session count
    if(user_message == 'clear'):
        session['chat_count'] = 0
        return jsonify({"response": "Please Enter the ingredients like Chicken;Bread"})

        # Initial input for user ingredients
    if(session['chat_count'] == 0):
        user_ingredients = user_message.split(';')
        if(len(user_ingredients) == 0):
            session['chat_count'] = 0
            return jsonify({"response": "Please Enter the ingredients like Chicken;Bread"})
        else:
            session['chat_count'] = 1
            session['user_ingredients'] = user_ingredients
            print("=============== user ingredients======================")
            print(session['user_ingredients'])

            session['chat_count'] = 1
            return jsonify({"response": "Please Enter the ingredients that you want to exclude like Chicken;Bread"})
    
        # Getting excluded ingredients
    elif(session['chat_count'] == 1):
        session['chat_count'] = 2

        user_preference = session['user_preference']
        user_ingredients = session['user_ingredients']
        user_exclude_ingredients = user_message.split(';')

        # !!! stripped the chosen and excluded ingredients for accurate formatted parameters
        user_ingredients = [ingredient.strip() for ingredient in user_ingredients]
        user_exclude_ingredients = [ingredient.strip() for ingredient in user_exclude_ingredients]

        recipe = dataset_manager.get_recipe_recommendations(user_ingredients,
                                                             user_exclude_ingredients,
                                                             user_preference['meal_type'],
                                                             user_preference['time'])
        
        if True:
            session['recipe'] = recipe
            print(recipe)
            return jsonify({"response" : recipe})
        else:
            session['recipe'] = []
            return jsonify({"response": recipe})

    elif session['chat_count']:
        user_preference = session.get('user_preference', {})
        initial_message = (f"You are a personal chef. Here are my preferences: I have {user_preference['ingredientsOption']} "
                           f"and I want to spend {user_preference['time']} minutes on a {user_preference['meal_type']} "
                           f"with {user_preference['cuisine']} cuisine and this reciepe" + reciepe + "Based on these"
                            + user_message)
        bot_response = retry_with_backoff(lambda: generate_response(initial_message))
        session['chat_count'] = chat_count + 1
    else:
        bot_response = retry_with_backoff(lambda: generate_response(user_message))

    return jsonify({'success': True, 'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
