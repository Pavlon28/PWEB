#!/usr/bin/env python3

import socket
import urllib.parse

def fetch_url(url):
    """Fetches and prints the content of a given URL using raw sockets."""
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

    body = response.decode(errors="ignore").split("\r\n\r\n", 1)[1]  # Remove headers
    print("\n--- Response ---\n")
    print(body[:1000])  # Print first 1000 characters to avoid too much output

def search_web(query):
    """Performs a web search using DuckDuckGo and prints the top 10 results."""
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
    print("\n--- Search Results ---\n")
    print(body[:1000])  # Print first 1000 characters for now

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
            print("\nUsage:")
            print("  1 -> Fetch content from a URL")
            print("  2 -> Search the web")
            print("  3 -> Show this help")
            print("  4 -> Exit")
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    interactive_mode()
