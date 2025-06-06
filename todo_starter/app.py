from todos.utils import (
    error_for_list_title,
    error_for_todo,
    find_todo_list_by_id,
    delete_todo_list_by_id,
    find_todo_by_id,
    delete_todo_by_id,
    mark_all_todos_completed
)
from werkzeug.exceptions import NotFound
from uuid import uuid4
from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)


app = Flask(__name__)
app.secret_key = "th1515@b@ds3cr3t"


@app.before_request
def initialize_session():
    if "lists" not in session:
        session["lists"] = []


@app.route("/")
def index():
    return redirect(url_for("get_lists"))


@app.route("/lists/new")
def add_todo_list():
    return render_template('new_list.html')


@app.route("/lists", methods=["GET"])
def get_lists():
    return render_template('lists.html', lists=session["lists"])


@app.route("/lists", methods=["POST"])
def create_list():
    title = request.form["list_title"].strip()

    error = error_for_list_title(title, session["lists"])
    if error:
        flash(error, "error")
        return render_template("/new_list.html", title=title)

    session["lists"].append({
        "id": str(uuid4()),
        "title": title,
        "todos": []
    })

    session.modified = True
    flash("The list has been created.", "success")
    return redirect(url_for("get_lists"))


@app.route("/lists/<list_id>", methods=["POST"])
def update_list(list_id):
    title = request.form["list_title"].strip()
    lst = find_todo_list_by_id(list_id, session["lists"])
    error = error_for_list_title(title, session["lists"])

    if not lst:
        raise NotFound(description="List not Found")
    elif error:
        flash(error, "error")
        return render_template("/edit_list.html", lst=lst, title=title)

    lst["title"] = title

    flash('The list title has been updated', "success")
    return redirect(url_for("display_list", list_id=list_id))


@app.route("/lists/<list_id>/delete", methods=["POST"])
def delete_list(list_id):
    lst = find_todo_list_by_id(list_id, session["lists"])

    if not lst:
        raise NotFound(description="List not Found")

    title = lst["title"]
    session["lists"] = delete_todo_list_by_id(list_id, session["lists"])

    flash(f"The list: '{title}' has been deleted", "success")
    session.modified = True
    return redirect(url_for("get_lists"))


@app.route("/lists/<list_id>/todos", methods=["POST"])
def create_todo(list_id):
    todo_title = request.form["todo"].strip()

    lst = find_todo_list_by_id(list_id, session["lists"])
    if not lst:
        raise NotFound(description="List not Found")

    error = error_for_todo(todo_title)
    if error:
        flash(error, "error")
        return render_template("/list.html", lst=lst)

    lst["todos"].append({
        "id": str(uuid4()),
        "title": todo_title,
        "completed": False
    })

    session.modified = True
    flash("The todo has been created.", "success")
    return redirect(url_for("display_list", list_id=list_id))


@app.route("/lists/<list_id>", methods=["GET"])
def display_list(list_id):
    lst = find_todo_list_by_id(list_id, session["lists"])

    if not lst:
        raise NotFound(description="List not Found")

    return render_template("list.html", lst=lst)


@app.route("/lists/<list_id>/edit", methods=["GET"])
def edit_list(list_id):
    lst = find_todo_list_by_id(list_id, session["lists"])

    if not lst:
        raise NotFound(description="List not Found")

    return render_template("edit_list.html", lst=lst)


@app.route("/lists/<list_id>/todos/<todo_id>/toggle", methods=["POST"])
def toggle_todo_complete(list_id, todo_id):
    lst = find_todo_list_by_id(list_id, session["lists"])
    if not lst:
        raise NotFound(description="List not found")

    todo = find_todo_by_id(todo_id, lst)
    if not todo:
        raise NotFound(description="Todo not found")

    todo["completed"] = request.form["completed"] == "True"

    session.modified = True
    flash("The todo has been updated.", "success")
    return redirect(url_for("display_list", list_id=list_id))


@app.route("/lists/<list_id>/todos/<todo_id>/delete", methods=["POST"])
def delete_todo(list_id, todo_id):
    lst = find_todo_list_by_id(list_id, session["lists"])
    if not lst:
        raise NotFound(description="List not found")

    todo = find_todo_by_id(todo_id, lst)
    if not todo:
        raise NotFound(description="Todo not found")

    delete_todo_by_id(todo_id, lst)

    session.modified = True
    flash("The todo has been deleted.", "success")
    return redirect(url_for("display_list", list_id=list_id))


@app.route("/lists/<list_id>/complete_all", methods=["POST"])
def complete_all_todos(list_id):
    lst = find_todo_list_by_id(list_id, session["lists"])
    if not lst:
        raise NotFound(description="List not found")

    mark_all_todos_completed(lst)

    session.modified = True
    flash("The todos have been updated.", "success")
    return redirect(url_for("display_list", list_id=list_id))


if __name__ == "__main__":
    app.run(debug=True, port=5003)
