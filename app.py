import json
import os
from loguru import logger
from openai import OpenAI
from flask import Flask, render_template, request
import modal

stub = modal.Stub("my-flask-app")

app = Flask(__name__)

@stub.function()
def run_flask_app():
    app.run(host="0.0.0.0", port=5000)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        inspirations = request.form.getlist('inspiration')
        project_themes = request.form.get('project-themes', '')

        # Construct the prompt
        prompt = (
            "I have a list of inspirations for a photo project I'm working on. "
            "Can you recommend 5 or 6 more artists or and specific pieces of their work that might be similar? "
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
            "    \"description\": \"Description of the artist\",\n"
            "    \"link\": \"URL to their website, if they have one, or (in descending order of preference) a book of their work, a book about their work, a gallery page about them, or a wikipedia page about them.\"\n"
            "  },\n"
            "  ...\n"
            "]\n\n"
            "Please enclose the JSON response in triple backticks (```).\n"
            "Be sure that the representative image URLs are correct and up to date and can be loaded right now."
        )

        # Check if the response is cached
        cache_file = "openai-response.txt"
        SHOULD_CACHE = False
        if SHOULD_CACHE and os.path.exists(cache_file):
            with open(cache_file, "r") as file:
                openai_response = file.read()
        else:
            # Make a request to OpenAI
            client = OpenAI()
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "developer", "content": "You are an expert art historian, with deep knowledge of many artists, both mainstream and esoteric, including who they studied with and the themes of their work. Your goal is to help an artist find more inspiration for their art, given their current inspirations. You always provide images that are available on the internet at the time you respond to the prompt."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract the response text
            openai_response = completion.choices[0].message.content

            # Cache the response
            with open(cache_file, "w") as file:
                file.write(openai_response)

        if openai_response is None:
            logger.error("No response from OpenAI.")
            return render_template('index.html', inspirations=inspirations, project_themes=project_themes)

        # Extract JSON from the response
        START_TOKEN = '```json\n'
        json_start = openai_response.find(START_TOKEN)
        json_end = openai_response.rfind("```")
        if json_start != -1 and json_end != -1:
            json_content = openai_response[json_start + len(START_TOKEN):json_end].strip()
            print("\n\n" + json_content + "\n\n")
            try:
                recommendations = json.loads(json_content)
            except json.JSONDecodeError as e:
                print("Error parsing JSON content: %s", e)
                recommendations = []
        else:
            print("No JSON content found in the response.")
            recommendations = []

        return render_template('index.html', inspirations=inspirations, recommendations=recommendations, project_themes=project_themes)

    return render_template('index.html', inspirations=[])

if __name__ == '__main__':
    with stub.run():
        run_flask_app()
