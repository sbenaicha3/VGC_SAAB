"""Local-only UI and simulation endpoint. Run python -m vgc_sd.server."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import webbrowser
from .experiment import experiment, robustness


class Handler(BaseHTTPRequestHandler):
    def send_json(self, value, status=200):
        data=json.dumps(value,allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json')
        self.send_header('Cache-Control','no-store')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == '/health':
            self.send_json(dict(api_version=2, endpoints=['/run','/robustness']))
            return
        if self.path not in ('/', '/app.html'):
            self.send_error(404)
            return
        data=Path(__file__).with_name('app.html').read_bytes()
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path not in ('/run', '/robustness'):
            self.send_json(dict(error='Unknown simulation endpoint'),404); return
        # Prevent cross-origin pages from issuing simulations to this local service.
        if self.headers.get('Origin') not in (None, 'http://'+self.headers.get('Host','')):
            self.send_error(403); return
        try:
            length=int(self.headers.get('Content-Length',0))
            if not 0 < length <= 100000:
                raise ValueError('Invalid request size')
            payload=json.loads(self.rfile.read(length))
            result=(robustness(payload) if self.path=='/robustness' else experiment(payload))
            data=json.dumps(result,allow_nan=False).encode()
            self.send_response(200)
        except (ValueError, TypeError, KeyError, OverflowError) as error:
            data=json.dumps(dict(error=str(error))).encode()
            self.send_response(400)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(data)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--open',action='store_true',help='Open the local dashboard in your browser')
    args=parser.parse_args()
    try:
        server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    except OSError as error:
        parser.exit(1,f'Cannot start on port {args.port}: {error}\nStop the previous server or choose --port 8766.\n')
    url=f'http://127.0.0.1:{server.server_port}'
    print(f'VGC simulator: {url} (Ctrl+C to stop)',flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped.')
    finally:
        server.server_close()
