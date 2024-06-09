from flask import Flask, request, jsonify
import openai

app = Flask(__name__)
openai.api_key = 'YOUR_OPENAI_API_KEY'


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')

    # OpenAI API Request
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a personal chef, giving people recipes considering their prompts."},
            {"role": "user", "content": user_message}
        ]
    )

    # API Response processing
    chat_response = response['choices'][0]['message']['content']
    return jsonify({"response": chat_response})


if __name__ == '__main__':
    app.run(debug=True)
