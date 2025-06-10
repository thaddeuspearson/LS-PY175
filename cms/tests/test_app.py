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

    def teardown(self):
        shutil.rmtree(self.data_path, ignore_errors=True)

    def create_test_document(self, name, content=""):
        with open(os.path.join(self.data_path, name), "w") as f:
            f.write(content)

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
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, "text/plain; charset=utf-8")
            self.assertIn("Billy Bob Joe Steve", response.get_data(as_text=True))

    def test_display_file_content_redirects_not_found(self):
        with self.client.get("/does_not_exist.txt") as response:
            self.assertEqual(response.status_code, 302)

        with self.client.get(response.headers["Location"]) as response:
            self.assertEqual(response.status_code, 200)
            self.assertIn("does not exist", response.get_data(as_text=True))

        with self.client.get("/") as response:
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("does not exist", response.get_data(as_text=True))

    def test_display_file_content_md_file(self):
        self.create_test_document("about.md", "# About")

        with self.client.get("about.md") as response:
            self.assertEqual(response.status_code, 200)
            self.assertIn("<h1>About</h1>", response.get_data(as_text=True))

    def test_get_edit_file_content(self):
        self.create_test_document("changes.txt",
                                  'These are the changes')

        with self.client.get("/changes.txt/edit") as response:
            data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Edit content", data)
            self.assertIn("These are the changes", data)

    def test_save_file(self):
        self.create_test_document("changes.txt",
                                  'This should be overwritten')
        with self.client.post(
                "/changes.txt", data={'content': 'test content'}) as response:
            self.assertEqual(response.status_code, 302)

        with self.client.get(response.headers["Location"]) as response:
            self.assertEqual(response.status_code, 200)
            self.assertIn("changes.txt has been updated.",
                          response.get_data(as_text=True))

        with self.client.get("/changes.txt") as response:
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("this should be overwritten", 
                             response.get_data(as_text=True))
            self.assertIn("test content", response.get_data(as_text=True))
