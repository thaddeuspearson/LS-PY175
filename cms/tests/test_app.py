import unittest
import os
import shutil
from app import app


class TestApp(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.data_path = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_path, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.data_path, ignore_errors=True)

    def create_test_document(self, name, content=""):
        with open(os.path.join(self.data_path, name), "w") as f:
            f.write(content)

    def admin_session(self):
        with self.client as c:
            with c.session_transaction() as session:
                session['username'] = "admin"

    def test_index(self):
        self.create_test_document("changes.txt")
        self.create_test_document("about.md")

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("changes.txt", response.get_data(as_text=True))
        self.assertIn("about.md", response.get_data(as_text=True))

    def test_render_file_content(self):
        self.create_test_document("history.txt", "Billy Bob Joe Steve")

        with self.client.get("/history.txt") as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type,
                             "text/plain; charset=utf-8")
            self.assertIn("Billy Bob Joe Steve", data)

    def test_display_file_content_redirects_not_found(self):
        with self.client.get("/does_not_exist.txt") as response:
            self.assertEqual(response.status_code, 302)

        with self.client.get(response.headers["Location"]) as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("does not exist", data)

        with self.client.get("/") as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("does not exist", data)

    def test_display_file_content_md_file(self):
        self.create_test_document("about.md", "# About")

        with self.client.get("about.md") as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("<h1>About</h1>", data)

    def test_get_edit_file_content(self):
        self.admin_session()
        self.create_test_document("changes.txt", 'These are the changes')

        with self.client.get("/changes.txt/edit") as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Edit content", data)
            self.assertIn("These are the changes", data)

    def test_get_edit_file_content_signed_out(self):
        self.create_test_document("changes.txt", 'These are the changes')

        with self.client.get("/changes.txt/edit",
                             follow_redirects=True) as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("You must be signed in to do that.", data)
            self.assertIn("Username", data)

    def test_save_file(self):
        self.admin_session()
        self.create_test_document("changes.txt", 'To be overwritten')

        with self.client.post("/changes.txt",
                              data={'content': 'test content'}) as response:
            self.assertEqual(response.status_code, 302)

        with self.client.get(response.headers["Location"]) as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("changes.txt has been updated.", data)

        with self.client.get("/changes.txt") as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("this should be overwritten", data)
            self.assertIn("test content", data)

    def test_save_file_signed_out(self):
        self.create_test_document("changes.txt", 'To be overwritten')

        with self.client.post("/changes.txt",
                              data={'content': 'test content'},
                              follow_redirects=True) as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("You must be signed in to do that.", data)
            self.assertIn("Username", data)

    def test_new(self):
        self.admin_session()
        with self.client.get("/new") as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("<input", data)
            self.assertIn("Create</button>", data)

    def test_new_signed_out(self):
        with self.client.get("/new",
                             follow_redirects=True) as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("You must be signed in to do that.", data)
            self.assertIn("Username", data)

    def test_create_document(self):
        self.admin_session()
        with self.client.post("/new",
                              data={"filename": "test_file.txt"},
                              follow_redirects=True) as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("test_file.txt", data)
            self.assertIn("test_file.txt was created.", data)

        with self.client.post("/new",
                              data={"filename": "test_file.txt"}) as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 422)
            self.assertIn("test_file.txt already exists.", data)

    def test_create_document_signed_out(self):
        with self.client.post("/new",
                              data={"filename": "test_file.txt"},
                              follow_redirects=True) as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("You must be signed in to do that.", data)
            self.assertIn("Username", data)

    def test_create_document_without_filename(self):
        self.admin_session()
        with self.client.post("/new",
                              data={"filename": ""}) as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 422)
            self.assertIn("A name is required.", data)

    def test_delete_file(self):
        self.admin_session()
        self.create_test_document("test_doc.txt", "This should be deleted")

        with self.client.get("/") as response:
            data = response.get_data(as_text=True)
            self.assertIn('<a href="/test_doc.txt"', data)

        with self.client.post("/test_doc.txt/delete",
                              follow_redirects=True) as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("test_doc.txt has been deleted.", data)
            self.assertNotIn('<a href="/test_doc.txt"', data)

    def test_delete_file_signed_out(self):
        self.create_test_document("test_doc.txt", "This should be deleted")

        with self.client.get("/") as response:
            data = response.get_data(as_text=True)
            self.assertIn('<a href="/test_doc.txt"', data)

        with self.client.post("/test_doc.txt/delete",
                              follow_redirects=True) as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("You must be signed in to do that.", data)
            self.assertIn('Username', data)

    def test_render_signin(self):
        with self.client.get('/users/signin',
                             follow_redirects=True) as response:
            self.assertEqual(response.status_code, 200)

    def test_signin(self):
        with self.client.post("/users/signin",
                              data={"username": 'test_admin',
                                    "password": "test_password"},
                              follow_redirects=True) as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("admin", data)

    def test_signin_with_bad_creds(self):
        with self.client.post("/users/signin",
                              data={"username": 'ooga',
                                    "password": "booga"},
                              follow_redirects=True) as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 422)
            self.assertIn("Sign In</button>", data)

    def test_signout(self):
        self.admin_session()
        with self.client.post("/users/signout",
                              follow_redirects=True) as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("signed out", data)
