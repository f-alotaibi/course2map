from flask import Flask, send_from_directory, render_template, request, abort
from waitress import serve
import os
from image_extraction import extractClasses

app = Flask(__name__)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route("/")
def main():
    return render_template('index.html')

@app.post("/extract-classes")
def extract_classes():
    inputValue = request.form["Input"]
    try:
        val = extractClasses(inputValue)
    except Exception as e:
        abort(422, e)
    return val

if __name__ == '__main__':
    port = 80
    if os.getenv("PORT"):
        port = int(os.getenv("PORT"))
    serve(app, host="0.0.0.0", port=port)