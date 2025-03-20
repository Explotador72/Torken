import http.server
import socketserver

PORT = 8087


class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')


def run_web_server():
    with socketserver.TCPServer(("", PORT), MyRequestHandler) as httpd:
        print(f"Web server running on port {PORT}")
        httpd.serve_forever()