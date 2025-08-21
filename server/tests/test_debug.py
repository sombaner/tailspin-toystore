import unittest
from flask import Flask
from routes.debug import debug_bp


class TestDebugLeak(unittest.TestCase):
    def setUp(self) -> None:
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        # Register only the debug blueprint for isolated tests
        self.app.register_blueprint(debug_bp)
        self.client = self.app.test_client()

    def test_stats_initial(self) -> None:
        resp = self.client.get('/api/debug/leak/stats')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['chunks'], 0)
        self.assertEqual(data['totalBytes'], 0)

    def test_induce_and_clear(self) -> None:
        # Induce 2 chunks of 1MB each
        resp = self.client.post('/api/debug/leak?mb=1&count=2')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['chunks'], 2)
        self.assertGreaterEqual(data['totalBytes'], 2 * 1024 * 1024)

        # Stats reflect retained memory
        resp = self.client.get('/api/debug/leak/stats')
        self.assertEqual(resp.status_code, 200)
        data2 = resp.get_json()
        self.assertEqual(data2['chunks'], 2)

        # Clear
        resp = self.client.post('/api/debug/leak/clear')
        self.assertEqual(resp.status_code, 200)
        data3 = resp.get_json()
        self.assertEqual(data3['chunks'], 0)
        self.assertEqual(data3['totalBytes'], 0)

    def test_invalid_params(self) -> None:
        resp = self.client.post('/api/debug/leak?mb=0&count=-1')
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data['error'], 'invalid_parameters')


if __name__ == '__main__':
    unittest.main()
