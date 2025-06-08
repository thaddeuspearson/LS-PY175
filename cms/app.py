from flask import (
    Flask,
    render_template,
)
import os


app = Flask(__name__)


@app.route("/")
def index():
    root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(root, "cms", "data")
    filenames = [
        f for f in os.listdir(data_dir)
        if os.path.isfile(os.path.join(data_dir, f))
    ]
    print(os.path.abspath(os.path.dirname(__file__)))
    return render_template('index.html', filenames=filenames)


if __name__ == "__main__":
    app.run(debug=True, port=5003)
