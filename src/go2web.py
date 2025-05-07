#!/usr/bin/env python3

import sys
import socket
import ssl
import os
import hashlib
import json
from urllib.parse import urlparse, quote_plus
from bs4 import BeautifulSoup

# ====== Caching ======
CACHE_DIR = ".go2web_cache"

def _hash_key(url):
    return hashlib.sha256(url.encode()).hexdigest()

def get_cache(url):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, _hash_key(url))
    return open(path, 'r', encoding='utf-8').read() if os.path.exists(path) else None

def set_cache(url, content):
    path = os.path.join(CACHE_DIR, _hash_key(url))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# ====== HTML/JSON Parsing ======
def clean_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text(separator='\n', strip=True)

def parse_response(headers, body):
    for line in headers.splitlines():
        if 'Content-Type:' in line:
            if 'application/json' in line:
                try:
                    return json.dumps(json.loads(body), indent=2)
                except:
                    return body
    return clean_html(body)

# ====== Manual HTTP Client ======
class HTTPClient:
    def __init__(self):
        pass

    def make_request(self, url, redirects=5):
        parsed = urlparse(url)
        host = parsed.hostname
        port = 443 if parsed.scheme == 'https' else 80
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query

        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: go2web/1.0\r\nAccept: text/html,application/json\r\nConnection: close\r\n\r\n"

        with socket.create_connection((host, port)) as sock:
            if parsed.scheme == 'https':
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=host)
            sock.sendall(request.encode())
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk

        header_data, _, body = response.partition(b"\r\n\r\n")
        headers = header_data.decode(errors='ignore')
        status = int(headers.split()[1])

        if status in (301, 302, 303, 307, 308) and redirects > 0:
            for line in headers.splitlines():
                if line.lower().startswith("location:"):
                    new_url = line.split(":", 1)[1].strip()
                    if not new_url.startswith("http"):
                        new_url = f"{parsed.scheme}://{host}{new_url}"
                    return self.make_request(new_url, redirects - 1)
        return headers, body.decode(errors='ignore')

# ====== Core Functions ======
def handle_help():
    print("""Usage:
  go2web -u <URL>         Make an HTTP request to the specified URL and print the response
  go2web -s <search-term> Search using DuckDuckGo and print top 10 results
  go2web -h               Show this help message""")

def handle_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url  # Default to HTTPS

    cached = get_cache(url)
    if cached:
        print("[*] Loaded from cache")
        print(cached)
        return

    client = HTTPClient()
    try:
        headers, body = client.make_request(url)
        parsed = parse_response(headers, body)
        print(parsed)
        set_cache(url, parsed)
    except Exception as e:
        print(f"Error: {e}")


def handle_search(term):
    query = quote_plus(term)
    search_url = f"https://html.duckduckgo.com/html/?q={query}"
    client = HTTPClient()
    try:
        headers, body = client.make_request(search_url)
        soup = BeautifulSoup(body, 'html.parser')
        results = soup.find_all('a', class_='result__a', limit=10)
        for i, a in enumerate(results, 1):
            print(f"{i}. {a.get_text(strip=True)}\n   {a['href']}")
    except Exception as e:
        print(f"Search failed: {e}")

# ====== Main Entry Point ======
def main():
    if len(sys.argv) < 2 or sys.argv[1] == '-h':
        handle_help()
    elif sys.argv[1] == '-u' and len(sys.argv) >= 3:
        handle_url(sys.argv[2])
    elif sys.argv[1] == '-s' and len(sys.argv) >= 3:
        handle_search(" ".join(sys.argv[2:]))
    else:
        print("Invalid usage.\n")
        handle_help()

if __name__ == "__main__":
    main()
