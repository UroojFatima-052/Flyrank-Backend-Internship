# BE-01: Build Your First API Endpoint

## What this does
A minimal Flask server with two JSON endpoints.

## Endpoints
- `GET /` — returns student details (name, father name, gender)
- `GET /marks` — returns student marks by subject

## How to run
```bash
pip install flask
python app.py
```
Then open `http://127.0.0.1:5000/` in your browser.

## What I learned
- How to create a Flask app and run it
- What a JSON endpoint is and how routes work
- Why `if __name__ == "__main__"` controls when the server starts