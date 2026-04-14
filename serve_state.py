#!/usr/bin/env python3
"""Serve /root/medical-rag/ over HTTP on port 8080."""

import http.server
import os

PORT = 8080
SERVE_DIR = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SERVE_DIR, **kwargs)

    def log_message(self, format, *args):
        # Let systemd/journald handle logging via stdout
        print(f"{self.address_string()} - {format % args}", flush=True)


if __name__ == "__main__":
    with http.server.HTTPServer(("", PORT), Handler) as httpd:
        print(f"Serving {SERVE_DIR} on port {PORT}", flush=True)
        httpd.serve_forever()
