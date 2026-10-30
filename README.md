# Flask To-Do App

A small, complete to-do application built with Flask and SQLite. It has a web UI (add, complete, delete, filter tasks) and a JSON REST API, plus tests and GitHub Actions CI.

## Features

- Add, complete, and delete tasks
- Filter by All / Active / Done
- Data persists in a local SQLite database (no extra setup)
- JSON REST API
- Automated tests (pytest) and CI workflow

## Project structure

```
flask-todo-app/
├── app.py                  # Flask app + API routes
├── templates/index.html    # Web UI
├── static/style.css        # Styles
├── static/app.js           # Front-end logic
├── tests/test_app.py       # Tests
├── requirements.txt
├── .github/workflows/ci.yml
├── .gitignore
├── LICENSE
└── README.md
```

## Run locally

```bash
git clone https://github.com/<your-username>/flask-todo-app.git
cd flask-todo-app

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

Optional environment variables: `PORT` (default 5000), `TODO_DB` (database file path), `FLASK_DEBUG=1`.

## Run the tests

```bash
pytest -v
```

## API

| Method | Endpoint            | Body                              | Description        |
|--------|---------------------|-----------------------------------|--------------------|
| GET    | `/api/todos`        | –                                 | List all tasks     |
| POST   | `/api/todos`        | `{"title": "Buy milk"}`           | Create a task      |
| PATCH  | `/api/todos/<id>`   | `{"done": true}` / `{"title": ""}`| Update a task      |
| DELETE | `/api/todos/<id>`   | –                                 | Delete a task      |
| GET    | `/health`           | –                                 | Health check       |

Example:

```bash
curl -X POST http://localhost:5000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Flask"}'
```

## Upload to GitHub

```bash
cd flask-todo-app
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/flask-todo-app.git
git push -u origin main
```

## License

MIT
