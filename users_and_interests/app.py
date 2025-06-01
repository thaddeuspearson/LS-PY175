from flask import Flask, render_template, redirect, url_for
from functools import reduce
import yaml


app = Flask(__name__)

try:
    with open("users.yaml", "r") as f:
        users = yaml.safe_load(f)
except (FileNotFoundError, yaml.YAMLError) as e:
    print(f"Error loading users data: {e}")
    users = {}


def total_interests(users: dict) -> int:
    return reduce(
        lambda acc, val: acc + len(val['interests']), users.values(), 0
    )


@app.context_processor
def inject_user_data():
    return {
        'users': users,
        'total_users': len(users),
        'total_interests': total_interests(users)
    }


@app.route('/')
def home():
    return redirect(url_for("users_list"))


@app.route('/users')
def users_list():
    return render_template("users.html")


@app.route('/users/<username>')
def user_profile(username):
    user = users.get(username)
    if not user:
        return redirect(url_for('home'))
    return render_template("user.html", username=username, user=user)


if __name__ == '__main__':
    app.run(debug=True, port=5003)
