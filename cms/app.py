import os
from flask import (
    Flask,
    render_template,
    send_from_directory,
)


app = Flask(__name__)


ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_DIR_PATH = os.path.join(ROOT_PATH, "src", "cms", "data")


@app.route("/")
def index():
    filenames = [
        f for f in os.listdir(DATA_DIR_PATH)
        if os.path.isfile(os.path.join(DATA_DIR_PATH, f))
    ]
    return render_template('index.html', filenames=filenames)


@app.route("/<filename>")
def display_file_content(filename):
    return send_from_directory(DATA_DIR_PATH, filename)


if __name__ == "__main__":
    app.run(debug=True, port=5003)
