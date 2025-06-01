from flask import Flask, render_template, g, redirect, request

app = Flask(__name__)


@app.before_request
def load_contents():
    with open("book_viewer/data/toc.txt", "r") as f:
        g.toc = f.readlines()


@app.route("/")
def index():
    return render_template("home.html", toc=g.toc)


@app.route("/chapters/<chapter_num>")
def chapter(chapter_num):
    if chapter_num.isdigit() and (1 <= int(chapter_num) <= len(g.toc)):
        chapter_name = g.toc[int(chapter_num) - 1]
        chapter_title = f"Chapter {chapter_num}: {chapter_name}"

        with open(f"book_viewer/data/chp{chapter_num}.txt", "r") as f:
            chapter = f.read()

        return render_template("chapter.html",
                               chapter_title=chapter_title, chapter=chapter)
    else:
        return redirect("/")


@app.route("/search")
def search():
    query = request.args.get("query", '')
    results = []

    for chapter_idx, chapter_name in enumerate(g.toc, start=1):
        with open(f"book_viewer/data/chp{chapter_idx}.txt") as f:
            content = f.read()
            query = query.lower()
            matches = {}

            for para_idx, paragraph in enumerate(content.split("\n\n"), start=1):
                search_idx = paragraph.lower().find(query)
                if search_idx != -1:
                    matches[para_idx] = paragraph

            if matches:
                results.append({
                    "name": chapter_name,
                    "number": chapter_idx,
                    "paragraphs": matches
                })
    return render_template('search.html', query=query, results=results)


def in_paragraphs(text: str):
    paragraphs = text.split("\n\n")
    return "\n".join(f"<p id={i+1}>{p}</p>" for i, p in enumerate(paragraphs))


def bold(text: str, term: str):
    return text.replace(term, f"<strong>{term}</strong>")


app.jinja_env.filters["in_paragraphs"] = in_paragraphs
app.jinja_env.filters["bold"] = bold


@app.errorhandler(404)
def page_not_found(error):
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, port=5003)
