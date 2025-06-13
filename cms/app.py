import os
from flask import (  # type: ignore
    flash,
    Flask,
    redirect,
    render_template,
    send_from_directory,
    session,
    request,
    url_for
)
from functools import wraps
from markdown import markdown  # type: ignore
from yaml import safe_load  # type: ignore


app = Flask(__name__)
app.secret_key = "th1515@b@ds3cr3t"


ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


def get_dir_path(basename):
    base_dir = os.path.join(
        ROOT_PATH, "tests" if app.config["TESTING"] else "src", "cms"
    )
    return os.path.join(base_dir, basename)


def load_user_creds():
    user_creds_path = get_dir_path("users.yaml")
    with open(user_creds_path, "r") as user_creds:
        return safe_load(user_creds)


def user_signed_in():
    return 'username' in session


def require_signin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not user_signed_in():
            flash("You must be signed in to do that.")
            return redirect(url_for("render_signin"))

        return f(*args, **kwargs)
    return wrapper


def require_filepath(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        data_dir_path = get_dir_path("data")
        filename = kwargs.get("filename")
        file_path = os.path.join(data_dir_path, filename)

        if os.path.isfile(file_path):
            return f(file_path=file_path, *args, **kwargs)

        flash(f"{filename} does not exist.")
        return redirect(url_for('index'))
    return wrapper


@app.route("/")
def index():
    data_dir_path = get_dir_path("data")
    filenames = [
        f for f in os.listdir(data_dir_path)
        if os.path.isfile(os.path.join(data_dir_path, f))
    ]
    return render_template('index.html', filenames=filenames)


@app.route("/<filename>")
@require_filepath
def display_file_content(filename, file_path):
    data_dir_path = get_dir_path("data")
    if filename.endswith(".md"):
        with open(file_path) as f:
            content = f.read()
            return render_template('markdown.html', content=markdown(content))
    return send_from_directory(data_dir_path, filename, as_attachment=False)


@app.route("/<filename>/edit")
@require_signin
@require_filepath
def edit_file_content(filename, file_path):
    with open(file_path, "r") as f:
        content = f.read()
    return render_template('edit.html', content=content, filename=filename)


@app.route("/<filename>", methods=["POST"])
@require_signin
@require_filepath
def save_file(filename, file_path):
    updated_content = request.form["content"]

    with open(file_path, "w") as f:
        f.write(updated_content)

    flash(f"{filename} has been updated.")
    return redirect(url_for('index'))


@app.route('/new')
@require_signin
def new_document():
    return render_template("new.html")


@app.route("/new", methods=["POST"])
@require_signin
def create_document():
    data_dir_path = get_dir_path("data")
    filename = request.form["filename"]
    file_path = os.path.join(data_dir_path, filename)

    if not filename:
        flash("A name is required.")
        return render_template('new.html'), 422
    elif os.path.exists(file_path):
        flash(f"{filename} already exists.")
        return render_template('new.html'), 422

    with open(file_path, "w") as f:
        f.write("")

    flash(f"{filename} was created.")
    return redirect(url_for('index'))


@app.route("/<filename>/delete", methods={"POST"})
@require_signin
@require_filepath
def delete_file(filename, file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f"{filename} has been deleted.")
        return redirect(url_for('index'))


@app.route("/users/signin")
def render_signin():
    return render_template('signin.html')


@app.route("/users/signin", methods=["POST"])
def signin():
    username = request.form["username"]
    password = request.form["password"]
    users = load_user_creds()
    if users.get(username) == password:
        session["username"] = username
        flash("Welcome")
        return redirect(url_for('index'))
    else:
        flash("Invalid credentials")
        return render_template('signin.html'), 422


@app.route("/users/signout", methods=['POST'])
def signout():
    session.pop('username', None)
    flash("You have been signed out")
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, port=5003)
