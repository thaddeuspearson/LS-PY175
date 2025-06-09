import os
from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    send_from_directory,
    request,
    url_for
)
from functools import wraps
from markdown import markdown


app = Flask(__name__)
app.secret_key = "th1515@b@ds3cr3t"


ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_DIR_PATH = os.path.join(ROOT_PATH, "src", "cms", "data")


def require_filepath(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        filename = kwargs.get("filename")
        file_path = os.path.join(DATA_DIR_PATH, filename)

        if os.path.isfile(file_path):
            return f(file_path=file_path, *args, **kwargs)

        flash(f"{filename} does not exist.")
        return redirect(url_for('index'))
    return decorated_function


@app.route("/")
def index():
    filenames = [
        f for f in os.listdir(DATA_DIR_PATH)
        if os.path.isfile(os.path.join(DATA_DIR_PATH, f))
    ]
    return render_template('index.html', filenames=filenames)


@app.route("/<filename>")
@require_filepath
def display_file_content(filename, file_path):
    if filename.endswith(".md"):
        with open(file_path) as f:
            content = f.read()
            return markdown(content)
    return send_from_directory(DATA_DIR_PATH, filename)


@app.route("/<filename>/edit")
@require_filepath
def edit_file_content(filename, file_path):
    with open(file_path, "r") as f:
        content = f.read()
    return render_template('edit.html', content=content, filename=filename)


@app.route("/<filename>", methods=["POST"])
@require_filepath
def save_file(filename, file_path):
    updated_content = request.form["content"]

    with open(file_path, "w") as f:
        f.write(updated_content)

    flash(f"{filename} has been updated.")
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, port=5003)
