import socket

def fetch_url(url):
    # Extract host and path
    if url.startswith("http://"):
        url = url[7:]
    elif url.startswith("https://"):
        print("Error: HTTPS is not supported in this version.")
        return

    host, path = url.split("/", 1) if "/" in url else (url, "")
    path = "/" + path if path else "/"

    # Open a socket and connect to the host
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

    # Print the response (headers + content)
    print(response.decode(errors="ignore"))

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "-u":
        fetch_url(sys.argv[2])
