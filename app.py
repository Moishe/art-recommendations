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
        prompt += (
            f"\nMy themes are {project_themes}\n\n"
            "Please provide the recommendations in the following JSON format:\n"
            "[\n"
            "  {\n"
            "    \"artist\": \"Artist Name\",\n"
            "    \"description\": \"Description of the artist or work\",\n"
            "    \"image\": \"URL to a representative image\",\n"
            "    \"link\": \"URL to their work\"\n"
            "  },\n"
            "  ...\n"
            "]\n\n"
            "Please enclose the JSON response in triple backticks (```)."
        )

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

        # Extract JSON from the response
        json_start = openai_response.find("```")
        json_end = openai_response.rfind("```")
        if json_start != -1 and json_end != -1:
            json_content = openai_response[json_start + 3:json_end].strip()
            try:
                recommendations = json.loads(json_content)
            except json.JSONDecodeError as e:
                print("Error parsing JSON content: %s", e)
                recommendations = []
        else:
            print("No JSON content found in the response.")
            recommendations = []

        return render_template('index.html', inspirations=inspirations, recommendations=recommendations)

    return render_template('index.html', inspirations=[])

if __name__ == '__main__':
    app.run(debug=True)
