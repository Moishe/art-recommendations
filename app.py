import json
import os
import time
from loguru import logger
from openai_client import create_prompt, get_openai_recommendations
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

            prompt = create_prompt(inspirations, project_themes)

            openai_response, recommendations = get_openai_recommendations(prompt)

            return render_template('index.html', inspirations=inspirations, recommendations=recommendations, project_themes=project_themes, debug=debug, raw_prompt=prompt, raw_response=openai_response)

        return render_template('index.html', inspirations=[])

    return web_app
