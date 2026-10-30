import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402


@pytest.fixture
def client(tmp_path):
    app = create_app({"DATABASE": str(tmp_path / "test.db"), "TESTING": True})
    with app.test_client() as c:
        yield c


def test_index_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"To-Do List" in res.data


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_empty_list(client):
    res = client.get("/api/todos")
    assert res.status_code == 200
    assert res.get_json() == []


def test_create_and_list(client):
    res = client.post("/api/todos", json={"title": "Buy milk"})
    assert res.status_code == 201
    created = res.get_json()
    assert created["title"] == "Buy milk"
    assert created["done"] is False

    todos = client.get("/api/todos").get_json()
    assert len(todos) == 1
    assert todos[0]["id"] == created["id"]


def test_create_requires_title(client):
    assert client.post("/api/todos", json={"title": "   "}).status_code == 400
    assert client.post("/api/todos", json={}).status_code == 400
    assert client.post("/api/todos", json={"title": "x" * 201}).status_code == 400


def test_update_done_and_title(client):
    todo = client.post("/api/todos", json={"title": "Task"}).get_json()
    res = client.patch(f"/api/todos/{todo['id']}", json={"done": True})
    assert res.status_code == 200
    assert res.get_json()["done"] is True

    res = client.patch(f"/api/todos/{todo['id']}", json={"title": "Renamed"})
    assert res.get_json()["title"] == "Renamed"
    assert res.get_json()["done"] is True

    res = client.patch(f"/api/todos/{todo['id']}", json={"title": ""})
    assert res.status_code == 400


def test_update_missing(client):
    assert client.patch("/api/todos/999", json={"done": True}).status_code == 404


def test_delete(client):
    todo = client.post("/api/todos", json={"title": "Temp"}).get_json()
    assert client.delete(f"/api/todos/{todo['id']}").status_code == 204
    assert client.get("/api/todos").get_json() == []
    assert client.delete(f"/api/todos/{todo['id']}").status_code == 404
