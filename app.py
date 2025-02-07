from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        inspirations = request.form.getlist('inspiration')
        return render_template('index.html', inspirations=inspirations)
    return render_template('index.html', inspirations=[])

if __name__ == '__main__':
    app.run(debug=True)
