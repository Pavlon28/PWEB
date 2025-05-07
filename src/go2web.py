import socket
import ssl
import zlib

def fetch_url(url):
    """Fetches and prints the content of a given URL using raw sockets, supporting HTTP and HTTPS."""
    if url.startswith("http://"):
        use_ssl = False
        url = url[7:]
        port = 80
    elif url.startswith("https://"):
        use_ssl = True
        url = url[8:]
        port = 443  # Default HTTPS port
    else:
        print("Error: URL must start with http:// or https://")
        return

    # Extract host and path
    host, path = url.split("/", 1) if "/" in url else (url, "")
    path = "/" + path if path else "/"

    # Create a socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if use_ssl:
            context = ssl.create_default_context()  # Create an SSL context
            s = context.wrap_socket(s, server_hostname=host)  # Wrap socket with SSL
        s.connect((host, port))  # Connect to host

        # Send HTTP GET request with Accept-Encoding header for compression handling
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"User-Agent: go2web/1.0\r\n"
            f"Accept-Encoding: gzip, deflate\r\n"
            f"Connection: close\r\n\r\n"
        )
        s.sendall(request.encode())

        # Receive full response
        response = b""
        while True:
            chunk = s.recv(4096)  # Read in chunks
            if not chunk:
                break
            response += chunk  # Append until full data is received

    # Decode response properly
    response_text = response.decode("iso-8859-1")  # Use ISO-8859-1 to properly split headers
    headers, body = response_text.split("\r\n\r\n", 1) if "\r\n\r\n" in response_text else ("", response_text)

    # Check for chunked transfer encoding and decompress if necessary
    if "Transfer-Encoding: chunked" in headers:
        body = decode_chunked(body)

    if "Content-Encoding: gzip" in headers:
        body = decompress_gzip(body)
    elif "Content-Encoding: deflate" in headers:
        body = decompress_deflate(body)

    # Ensure UTF-8 decoding
    try:
        body = body.decode("utf-8")
    except UnicodeDecodeError:
        body = body.decode("iso-8859-1")

    print("\n--- Response ---\n")
    print(body[:2000])  # Print first 2000 characters to prevent terminal overflow


def decode_chunked(body):
    """Decodes an HTTP response with Transfer-Encoding: chunked."""
    decoded_body = b""
    while body:
        try:
            chunk_size_end = body.index("\r\n")  # Find the first newline
            chunk_size = int(body[:chunk_size_end], 16)  # Convert hex size to int
            if chunk_size == 0:
                break  # End of chunked response
            body = body[chunk_size_end + 2:]  # Remove chunk size line
            decoded_body += body[:chunk_size]  # Append chunk data
            body = body[chunk_size + 2:]  # Remove chunk data and trailing \r\n
        except (ValueError, IndexError):
            break  # If parsing fails, stop processing
    return decoded_body


def decompress_gzip(body):
    """Decompresses a gzip-compressed HTTP response body."""
    try:
        return zlib.decompress(body, 16 + zlib.MAX_WBITS)
    except zlib.error:
        return body  # Return unchanged if decompression fails


def decompress_deflate(body):
    """Decompresses a deflate-compressed HTTP response body."""
    try:
        return zlib.decompress(body)
    except zlib.error:
        try:
            return zlib.decompress(body, -zlib.MAX_WBITS)  # Try raw deflate
        except zlib.error:
            return body  # Return unchanged if decompression fails


def search_web(query):
    """Performs a web search using DuckDuckGo and prints the top 10 results."""
    search_url = f"duckduckgo.com/?q={urllib.parse.quote(query)}"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("duckduckgo.com", 80))
        request = f"GET /?q={urllib.parse.quote(query)} HTTP/1.1\r\nHost: duckduckgo.com\r\nConnection: close\r\n\r\n"
        s.sendall(request.encode())

        response = b""
        while True:
            chunk = s.recv(4096)  # Read full response
            if not chunk:
                break
            response += chunk

    body = response.decode(errors="ignore").split("\r\n\r\n", 1)[1]  # Remove headers

    print("\n--- Search Results ---\n")
    print(body[:2000])  # Print first 2000 characters

def print_help():
    """Displays the help message."""
    print("\nUsage:")
    print("  go2web -u <URL>         # Fetch content from the specified URL")
    print("  go2web -s <search-term> # Search and print top 10 results")
    print("  go2web -h               # Show this help message")
    print("\nInteractive Mode:")
    print("  Just run 'go2web' and follow the menu.")

def interactive_mode():
    """Runs the program in interactive mode, asking the user for input."""
    while True:
        print("\nChoose an option:")
        print("1. Fetch a URL (-u)")
        print("2. Search the web (-s)")
        print("3. Show help (-h)")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            url = input("Enter the URL (must start with http://): ").strip()
            fetch_url(url)
        elif choice == "2":
            query = input("Enter search term: ").strip()
            search_web(query)
        elif choice == "3":
            print_help()
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        interactive_mode()  # Run interactive mode if no arguments are provided
    elif len(sys.argv) > 2:
        if sys.argv[1] == "-u":
            fetch_url(sys.argv[2])
        elif sys.argv[1] == "-s":
            search_web(sys.argv[2])
        else:
            print("Invalid argument. Use -h for help.")
    elif sys.argv[1] == "-h":
        print_help()
    else:
        print("Invalid usage. Use -h for help.")
