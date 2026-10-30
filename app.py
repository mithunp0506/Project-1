"""Flask To-Do app with a JSON API and a simple web UI (SQLite storage)."""
import os
import sqlite3

from flask import Flask, g, jsonify, render_template, request

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["DATABASE"] = os.environ.get(
        "TODO_DB", os.path.join(BASE_DIR, "todos.db")
    )
    if test_config:
        app.config.update(test_config)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        db = sqlite3.connect(app.config["DATABASE"])
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.commit()
        db.close()

    init_db()

    def row_to_dict(row):
        return {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"]),
            "created_at": row["created_at"],
        }

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    @app.route("/api/todos", methods=["GET"])
    def list_todos():
        rows = get_db().execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
        return jsonify([row_to_dict(r) for r in rows])

    @app.route("/api/todos", methods=["POST"])
    def create_todo():
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify(error="title is required"), 400
        if len(title) > 200:
            return jsonify(error="title must be 200 characters or fewer"), 400
        db = get_db()
        cur = db.execute("INSERT INTO todos (title) VALUES (?)", (title,))
        db.commit()
        row = db.execute("SELECT * FROM todos WHERE id = ?", (cur.lastrowid,)).fetchone()
        return jsonify(row_to_dict(row)), 201

    @app.route("/api/todos/<int:todo_id>", methods=["PATCH"])
    def update_todo(todo_id):
        db = get_db()
        row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if row is None:
            return jsonify(error="not found"), 404
        data = request.get_json(silent=True) or {}
        title = row["title"]
        done = row["done"]
        if "title" in data:
            title = (data["title"] or "").strip()
            if not title:
                return jsonify(error="title cannot be empty"), 400
            if len(title) > 200:
                return jsonify(error="title must be 200 characters or fewer"), 400
        if "done" in data:
            done = 1 if data["done"] else 0
        db.execute(
            "UPDATE todos SET title = ?, done = ? WHERE id = ?", (title, done, todo_id)
        )
        db.commit()
        row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        return jsonify(row_to_dict(row))

    @app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
    def delete_todo(todo_id):
        db = get_db()
        cur = db.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        db.commit()
        if cur.rowcount == 0:
            return jsonify(error="not found"), 404
        return "", 204

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
