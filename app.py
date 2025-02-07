import openai
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
        openai.api_key = "YOUR_OPENAI_API_KEY"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )

        # Extract the response text
        openai_response = response.choices[0].text.strip()

        return render_template('index.html', inspirations=inspirations, openai_response=openai_response)
    return render_template('index.html', inspirations=[])

if __name__ == '__main__':
    app.run(debug=True)
