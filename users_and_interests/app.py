from flask import Flask, render_template
from functools import reduce
import yaml


app = Flask(__name__)

with open("users.yaml", "r") as f:
    users = yaml.safe_load(f)


@app.route('/')
def index():
    for value in users.values():
        print(len(value['interests']))
    total_users = len(users)
    total_interests = reduce(lambda acc, val: acc + len(val['interests']),
                             users.values(), 0)
    return render_template("index.html", total_users=total_users,
                           total_interests=total_interests)


if __name__ == '__main__':
    app.run(debug=True, port=5003)
