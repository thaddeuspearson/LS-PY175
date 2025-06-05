def error_for_list_title(title: str, lists: list) -> str | None:
    error = None

    if any(lst["title"] == title for lst in lists):
        error = "Title must be unique."
    elif not 1 <= len(title) <= 100:
        error = "Title must be between 1 and 100 characters."

    return error


def error_for_todo(title: str) -> str | None:
    error = None

    if not 1 <= len(title) <= 100:
        error = "Title must be between 1 and 100 characters."

    return error


def find_todo_lst_by_id(todo_lst_id: str, lists: list) -> dict | None:
    return next(
        (lst for lst in lists if lst['id'] == todo_lst_id), None
    )


def find_todo_by_id(todo_id: str, todo_list: list) -> dict | None:
    return next(
        (todo for todo in todo_list["todos"] if todo["id"] == todo_id), None
    )


def delete_todo_by_id(todo_id: str, todo_lst: list) -> None:
    todo_lst["todos"] = [todo for todo in todo_lst["todos"] if todo["id"] != todo_id]


def mark_all_todos_completed(todo_lst: list) -> None:
    for todo in todo_lst["todos"]:
        todo["completed"] = not todo["completed"]
