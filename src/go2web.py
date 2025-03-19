import sys

def print_help():
    print("Usage:")
    print("  go2web -u <URL>         # Fetch content from the specified URL")
    print("  go2web -s <search-term> # Search and print top 10 results")
    print("  go2web -h               # Show this help message")

def main():
    if len(sys.argv) < 2:
        print("Error: Missing arguments. Use -h for help.")
        return
    
    option = sys.argv[1]
    
    if option == "-h":
        print_help()
    elif option == "-u":
        print("Feature not implemented yet: Fetch URL content")
    elif option == "-s":
        print("Feature not implemented yet: Search the web")
    else:
        print("Invalid option. Use -h for help.")

if __name__ == "__main__":
    main()
