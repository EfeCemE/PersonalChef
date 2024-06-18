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
