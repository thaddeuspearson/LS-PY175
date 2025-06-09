import unittest
from app import app


class TestApp(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("changes.txt", response.get_data(as_text=True))
        self.assertIn("about.md", response.get_data(as_text=True))
        self.assertIn("history.txt", response.get_data(as_text=True))

    def test_render_file_content(self):
        with self.client.get("/history.txt") as response:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, "text/plain; charset=utf-8")
            self.assertIn("Guido van Rossum", response.get_data(as_text=True))

    def test_display_file_content_redirects_not_found(self):
        with self.client.get("/does_not_exist.txt") as response:
            self.assertEqual(response.status_code, 302)

        with self.client.get(response.headers["Location"]) as response:
            self.assertEqual(response.status_code, 200)
            self.assertIn("does not exist", response.get_data(as_text=True))

        with self.client.get("/") as response:
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("does not exist", response.get_data(as_text=True))
