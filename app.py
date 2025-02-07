import json
import os
from openai import OpenAI
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        inspirations = request.form.getlist('inspiration')
        project_themes = request.form.get('project-themes', '')

        # Construct the prompt
        prompt = (
            "Hey, I have a list of inspirations for a photo project I'm working on. "
            "Can you recommend 5 or 6 more artists or specific pieces of work that might be similar? "
            "Here's my list:\n"
        )
        for inspiration in inspirations:
            prompt += f"* {inspiration}\n"
        prompt += f"\nMy themes are {project_themes}"

        # Make a request to OpenAI
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "developer", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the response text
        print(completion)
        openai_response = completion.choices[0].message.content

        return render_template('index.html', inspirations=inspirations, openai_response=openai_response)

    return render_template('index.html', inspirations=[])

if __name__ == '__main__':
    app.run(debug=True)
