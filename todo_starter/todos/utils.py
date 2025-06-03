def error_for_list_title(title: str, lists: list) -> str | None:
    error = None

    if any(lst["title"] == title for lst in lists):
        error = "Title must be unique."
    elif not 1 <= len(title) <= 100:
        error = "Title must be between 1 and 100 chracters."

    return error


def find_todo_lst_by_id(todo_lst_id: str, lists: list) -> dict | None:
    for lst in lists:
        print(lst['id'])
    return next(
        (todo_lst for todo_lst in lists if todo_lst['id'] == todo_lst_id), None
    )
