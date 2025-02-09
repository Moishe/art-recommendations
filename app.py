import json
import os
import time
from loguru import logger
from openai_client import get_openai_recommendations
from flask import Flask, render_template, request
import modal

app = modal.App("moishes-art-recommendations")
image = (modal.Image.debian_slim()
         .pip_install("flask", "openai", "loguru")
         .add_local_dir("templates", remote_path="/root/templates"))

@app.function(image=image, secrets=[modal.Secret.from_name("openai_api_key")])
@modal.wsgi_app()
def flask_app():
    web_app = Flask(__name__)

    @web_app.post('/')
    def index_post() -> str:
        return index()

    @web_app.get('/')
    def index():
        if request.method == 'POST':
            inspirations = request.form.getlist('inspiration')
            project_themes = request.form.get('project-themes', '')

            # Check if debug is enabled
            debug = 'debug' in request.form

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

            # Ensure the "shots" directory exists
            os.makedirs("shots", exist_ok=True)

            # Generate a unique ID for both prompt and response
            unique_id = int(time.time())

            openai_response, recommendations = get_openai_recommendations(prompt)

            return render_template('index.html', inspirations=inspirations, recommendations=recommendations, project_themes=project_themes, debug=debug, raw_prompt=prompt, raw_response=openai_response)

        return render_template('index.html', inspirations=[])

    return web_app
