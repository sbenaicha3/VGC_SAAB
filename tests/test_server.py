import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from vgc_sd.server import Handler


class QuietHandler(Handler):
    def log_message(self, *args):
        pass


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'
        cls.client = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def post(self, path, payload):
        request = urllib.request.Request(self.url + path, data=json.dumps(payload).encode(),
                                         headers={'Content-Type': 'application/json'})
        return self.client.open(request, timeout=15)

    def test_health_and_browser_page(self):
        with self.client.open(self.url + '/health', timeout=5) as response:
            self.assertIn('/robustness', json.load(response)['endpoints'])
        with self.client.open(self.url, timeout=5) as response:
            self.assertIn('no-store', response.headers['Cache-Control'])
            self.assertIn(b'Robustness dashboard', response.read())

    def test_simulation_and_sensitivity(self):
        config = dict(parameters=dict(horizon=1), samples=1)
        with self.post('/run', config) as response:
            self.assertEqual(len(json.load(response)['runs']), 4)
        with self.post('/robustness', dict(experiment=config, thresholds=[2500, 2800])) as response:
            self.assertEqual(len(json.load(response)['rows']), 2)

    def test_invalid_and_unknown_endpoint_return_json(self):
        for path, payload, status in [('/robustness', {}, 400), ('/missing', {}, 404)]:
            with self.assertRaises(urllib.error.HTTPError) as caught:
                self.post(path, payload)
            with caught.exception as response:
                self.assertEqual(response.code, status)
                self.assertIn('error', json.load(response))
