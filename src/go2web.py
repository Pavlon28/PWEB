import socket
import sys
import urllib.parse
import re

def extract_links(html):
    """Extracts up to 10 links from the search results page."""
    links = re.findall(r'<a.*?href="(http[^"]+)".*?>(.*?)</a>', html)
    return links[:10]  # Return first 10 links

def search_web(query):
    search_url = f"duckduckgo.com/?q={urllib.parse.quote(query)}"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("duckduckgo.com", 80))
        request = f"GET /?q={urllib.parse.quote(query)} HTTP/1.1\r\nHost: duckduckgo.com\r\nConnection: close\r\n\r\n"
        s.sendall(request.encode())

        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk

    body = response.decode(errors="ignore").split("\r\n\r\n", 1)[1]  # Remove headers
    links = extract_links(body)

    print("\nTop 10 Search Results:")
    for i, (link, text) in enumerate(links, 1):
        print(f"{i}. {text}: {link}")


def fetch_url(url):
    if url.startswith("http://"):
        url = url[7:]
    elif url.startswith("https://"):
        print("Error: HTTPS is not supported in this version.")
        return

    host, path = url.split("/", 1) if "/" in url else (url, "")
    path = "/" + path if path else "/"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, 80))
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        s.sendall(request.encode())

        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk

    # Convert response from bytes to string
    response_text = response.decode(errors="ignore")

    # Split headers and body
    if "\r\n\r\n" in response_text:
        headers, body = response_text.split("\r\n\r\n", 1)
    else:
        body = response_text  # If no headers are found, treat everything as the body

    print(body)  # Print only the HTML body


if __name__ == "__main__":
    if len(sys.argv) > 2:
        if sys.argv[1] == "-u":
            fetch_url(sys.argv[2])
        elif sys.argv[1] == "-s":
            search_web(sys.argv[2])