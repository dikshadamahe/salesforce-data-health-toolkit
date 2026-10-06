#!/usr/bin/env python3
"""
Interactive Web Application for Salesforce Data Health & Support Diagnostic Toolkit.
Compatible with Vercel Python Serverless Runtime and Local WSGI Execution.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

HTML_FILE = os.path.join(BASE_DIR, "public", "index.html")
if not os.path.exists(HTML_FILE):
    HTML_FILE = os.path.join(BASE_DIR, "static", "index.html")


def app(environ, start_response):
    """Standard WSGI entrypoint for Vercel and local WSGI servers."""
    path = environ.get("PATH_INFO", "/")

    if path == "/" or path == "/index.html":
        try:
            with open(HTML_FILE, "rb") as f:
                content = f.read()
            status = "200 OK"
            headers = [
                ("Content-Type", "text/html; charset=utf-8"),
                ("Content-Length", str(len(content))),
                ("Access-Control-Allow-Origin", "*"),
            ]
            start_response(status, headers)
            return [content]
        except Exception as e:
            status = "500 Internal Server Error"
            body = f"Error reading index.html: {str(e)}".encode("utf-8")
            start_response(status, [("Content-Type", "text/plain")])
            return [body]

    status = "404 Not Found"
    body = b"Not Found"
    start_response(status, [("Content-Type", "text/plain"), ("Content-Length", "9")])
    return [body]


# Exports for Vercel
application = app
handler = app

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    port = 8081
    print(f"\n[+] Serving Data Health Toolkit at http://127.0.0.1:{port}")
    httpd = make_server("127.0.0.1", port, app)
    httpd.serve_forever()
