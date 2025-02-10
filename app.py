import json
import os
import time
from loguru import logger
from openai_client import create_prompt, get_openai_recommendations
from flask import Flask, render_template, request
from search_collections import MuseumImageFinder
import modal

app = modal.App("moishes-art-recommendations")
image = (modal.Image.debian_slim()
         .pip_install("flask", "openai", "loguru", "requests")
         .add_local_dir("templates", remote_path="/root/templates"))

@app.function(image=image, secrets=[modal.Secret.from_name("openai_api_key"), modal.Secret.from_name("Smithsonian API")])
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

            # Initialize the MuseumImageFinder
            finder = MuseumImageFinder(smithsonian_api_key=os.environ["SMITHSONIAN_API_KEY"])

            openai_response, recommendations = get_openai_recommendations(prompt)

            FIND_IMAGES = False
            if FIND_IMAGES:
                for recommendation in recommendations:
                    artist_name = recommendation.get("artist")
                    if artist_name:
                        image_result = finder.find_artwork_image(artist_name)
                        logger.info(f"image for {artist_name}: {image_result}")
                        if image_result['success']:
                            recommendation['image_url'] = image_result['url']

            return render_template('index.html', inspirations=inspirations, recommendations=recommendations, project_themes=project_themes, debug=debug, raw_prompt=prompt, raw_response=openai_response)

        return render_template('index.html', inspirations=[])

    return web_app
