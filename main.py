from flask import Flask, render_template, request, jsonify, session
import openai
from openai import OpenAI
import os
import time
import dataset_manager

app = Flask(__name__)

app.secret_key = 'BAD_SECRET_KEY_16851wqdjnjhb'

openai.api_key = 'sk-proj-dCED1zg0GuDJNeNOnL0yT3BlbkFJ7aInQ69mfQAIsw1SUvB3'

client = OpenAI(api_key='sk-proj-dCED1zg0GuDJNeNOnL0yT3BlbkFJ7aInQ69mfQAIsw1SUvB3')

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
    print(user_preference)

    if not user_preference['cuisine']:
        return jsonify({"success": False, "message": "Cuisine selection is required."})
    
    session['user_preference'] = user_preference
    session['chat_count'] = 0

    return jsonify({"success": True})
    return redirect(url_for('frontend'))

@app.route('/frontend')
def frontend():
    return app.send_static_file('FrontEnd.html')

@app.route('/chatty', methods=['POST'])
def chat():

    # logs for debugging
    print("=============== chat count ======================")
    print(session['chat_count'])
    print("=====================================")
    data = request.get_json()
    user_message = data.get('message', '')
    bot_response = ''

    if not user_message:
        return jsonify({"response": "Message cannot be empty."})
    
    # to clear session count
    if(user_message == 'clear'):
        session['chat_count'] = 0
        return jsonify({"response": "Please Enter the ingriediets like Chicken;Bread"})
    
    # Initial input for user ingriedients
    if(session['chat_count'] == 0):
        user_ingriedinets = user_message.split(';')
        if(len(user_ingriedinets) == 0):
            session['chat_count'] = 0
            return jsonify({"response": "Please Enter the ingriediets like Chicken;Bread"})
        else:
            session['chat_count'] = 1
            session['user_ingriedients'] = user_ingriedinets
            print("=============== user ingriedients======================")
            print(session['user_ingriedients'])

            session['chat_count'] = 1
            return jsonify({"response": "Please Enter the ingriediets that you want to exclude like Chicken;Bread"})
        
    # Getting excluded Ingriedients
    elif(session['chat_count'] == 1):
        session['chat_count'] = 2

        user_prefrence = session['user_preference']
        user_ingriedinets = session['user_ingriedients']
        user_exclude_ingredients = user_message.split(';')
        
        reciepe = dataset_manager.get_recipe_recommendations(user_ingriedinets,
                                                             user_exclude_ingredients,
                                                             user_prefrence['cuisine'],
                                                             user_prefrence['time'])
        
        session['reciepe'] = reciepe
        print(reciepe)
        return jsonify({"response" : reciepe})


    try:
        print("bot")

        # First message to chat bot added reciepe as chatgpt should have context
        if(session['chat_count'] == 2):
            user_message = 'given this reciepe ' + session['reciepe'] + user_message
        bot_response = retry_with_backoff(lambda: generate_response(user_message))
    except Exception as e:
        bot_response = f"An error occurred after retries: {str(e)}"

    return jsonify({"response": bot_response})
    parts = user_message.split(';')
    user_ingredients = parts[0].split(':')[1].strip()
    user_exclude_ingredients = parts[1].split(':')[1].strip()
    user_cuisine = parts[2].split(':')[1].strip()
    user_max_time = int(parts[3].split(':')[1].strip()) if len(parts) > 3 and parts[3].split(':')[
        1].strip().isdigit() else None

    ingredients = dataset_manager.filter_user_input(user_ingredients, [item for sublist in
                                                                       dataset_manager.df['ingredients'].apply(
                                                                           eval).tolist() for item in sublist])
    exclude_ingredients = dataset_manager.filter_user_input(user_exclude_ingredients, [item for sublist in
                                                                                       dataset_manager.df[
                                                                                           'ingredients'].apply(
                                                                                           eval).tolist() for item in
                                                                                       sublist])
    cuisine = user_cuisine

    if not ingredients or not cuisine:
        return jsonify({"response": "Invalid input provided."})

    dataset_managers = dataset_manager.get_dataset_managers(ingredients, exclude_ingredients, cuisine, user_max_time)

if __name__ == "__main__":
    app.run(debug=True)

