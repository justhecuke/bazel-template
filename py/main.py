import sys
import requests
from cyclopts import App
from py.calculator import evaluate_expression

app = App()

@app.command
def info():
    """Display information about the Python environment and dependencies."""
    print(f"Python version: {sys.version}")
    print(f"Requests version: {requests.__version__}")
    print("Bazel hermetic Python template is working!")

@app.command
def fetch(url: str):
    """Fetch the status code from a given URL."""
    try:
        response = requests.get(url, timeout=5)
        print(f"Fetched {url} - Status Code: {response.status_code}")
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")

@app.command
def calc(expression: str):
    """Evaluate a mathematical expression securely using AST parsing."""
    try:
        result = evaluate_expression(expression)
        print(f"{expression} = {result}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    app()
