from flask import Flask, render_template, request, jsonify, session
import openai
import os
import time

app = Flask(__name__)

app.secret_key = 'BAD_SECRET_KEY_16851wqdjnjhb'

# Initialize the OpenAI client with API key
client = openai.OpenAI(api_key='')

def generate_response(user_message):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a personal chef. You are only giving recipes depending on my input, nothing else. If you understand, say OK."},
                {"role": "user", "content": "OK"},
                {"role": "user", "content": user_message}
            ]
        )
        return completion['choices'][0].message.content.strip()
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

    chat_count = session.get('chat_count', 0)

    if chat_count == 0:
        user_preference = session.get('user_preference', {})
        initial_message = (f"You are a personal chef. Here are my preferences: I have {user_preference['ingredientsOption']} "
                           f"and I want to spend {user_preference['time']} minutes on a {user_preference['meal_type']} "
                           f"with {user_preference['cuisine']} cuisine. Based on these, can you suggest some recipes?")
        bot_response = retry_with_backoff(lambda: generate_response(initial_message))
    else:
        bot_response = retry_with_backoff(lambda: generate_response(user_message))

    session['chat_count'] = chat_count + 1

    return jsonify({'success': True, 'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
