import sys
import requests

def main():
    print(f"Python version: {sys.version}")
    print(f"Requests version: {requests.__version__}")
    print("Bazel hermetic Python template is working!")

if __name__ == "__main__":
    main()
