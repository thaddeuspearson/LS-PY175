# LS-PY175 - Networked Applications with Python
Repository for working through Launch School's PY175 Course

## :green_book: Books
1. 

## :memo: Articles
1. [Flask Documentation](https://flask.palletsprojects.com/en/stable/)

1. [Book Viewer Project Template](https://dicf9ht99spz0.cloudfront.net/py175/zips/book_viewer_starter.zip)

1. [Flask Quick Start Guide](https://launchschool.com/gists/b1fd339b)

## :clipboard: Notes
- [Hosted todo app](https://ls-170-sinatra-todos.herokuapp.com/)

- Use `os.path.abspath(os.path.dirname(__file__))` if you need to know the directory of the current file

- New flask app with poetry workflow:


    1. Create a new "poetry" project 

        ```
        poetry new <project-name>
        ```

    1. In the root directory created by "poetry", create a new file

        ```
        touch app.py
        ```

    1. From the root directory, install the flask framework with:
        
        ```
        poetry add flask
        ```

    1. Starter code for app.py:

        ```
        from flask import Flask

        app = Flask(__name__)

        @app.route("/")
        def index():
            return 'Getting started.'

        if __name__ == "__main__":
            app.run(debug=True, port=5000)
        ```

    1. Run your application using the command from the root directory:
        
        ```
        poetry run python app.py
        ```

    1. Connect to the app in your browser by visiting:
        
        ```
        http://localhost:5000
        ```
