(() => {
  const list = document.getElementById("todo-list");
  const form = document.getElementById("add-form");
  const input = document.getElementById("new-title");
  const empty = document.getElementById("empty");
  const counter = document.getElementById("counter");
  const errorBox = document.getElementById("error");
  const filterButtons = document.querySelectorAll(".filters button");

  let todos = [];
  let filter = "all";

  function showError(msg) {
    errorBox.textContent = msg;
    errorBox.hidden = !msg;
  }

  async function api(path, options = {}) {
    const res = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!res.ok) {
      let message = "Request failed";
      try {
        message = (await res.json()).error || message;
      } catch (_) {}
      throw new Error(message);
    }
    return res.status === 204 ? null : res.json();
  }

  function render() {
    list.innerHTML = "";
    const visible = todos.filter((t) =>
      filter === "all" ? true : filter === "done" ? t.done : !t.done
    );

    visible.forEach((t) => {
      const li = document.createElement("li");
      if (t.done) li.classList.add("done");

      const box = document.createElement("input");
      box.type = "checkbox";
      box.checked = t.done;
      box.addEventListener("change", () => toggle(t));

      const title = document.createElement("span");
      title.className = "title";
      title.textContent = t.title; // textContent avoids XSS

      const del = document.createElement("button");
      del.className = "delete";
      del.setAttribute("aria-label", "Delete task");
      del.textContent = "×";
      del.addEventListener("click", () => remove(t));

      li.append(box, title, del);
      list.appendChild(li);
    });

    empty.hidden = visible.length > 0;
    const left = todos.filter((t) => !t.done).length;
    counter.textContent = `${left} task${left === 1 ? "" : "s"} left`;
  }

  async function load() {
    try {
      todos = await api("/api/todos");
      showError("");
      render();
    } catch (e) {
      showError(e.message);
    }
  }

  async function toggle(todo) {
    try {
      const updated = await api(`/api/todos/${todo.id}`, {
        method: "PATCH",
        body: JSON.stringify({ done: !todo.done }),
      });
      todos = todos.map((t) => (t.id === updated.id ? updated : t));
      render();
    } catch (e) {
      showError(e.message);
    }
  }

  async function remove(todo) {
    try {
      await api(`/api/todos/${todo.id}`, { method: "DELETE" });
      todos = todos.filter((t) => t.id !== todo.id);
      render();
    } catch (e) {
      showError(e.message);
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const title = input.value.trim();
    if (!title) return;
    try {
      const created = await api("/api/todos", {
        method: "POST",
        body: JSON.stringify({ title }),
      });
      todos.unshift(created);
      input.value = "";
      showError("");
      render();
    } catch (e) {
      showError(e.message);
    }
  });

  filterButtons.forEach((btn) =>
    btn.addEventListener("click", () => {
      filter = btn.dataset.filter;
      filterButtons.forEach((b) => b.classList.toggle("active", b === btn));
      render();
    })
  );

  load();
})();
