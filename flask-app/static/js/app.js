/**
 * AI Personal Assistant — Frontend JS
 * Week 2-4: Full UI logic, Flask + Django API integration
 */

const FLASK_URL = "";          // empty = same origin (Flask serves this file)
const DJANGO_URL = "http://127.0.0.1:8000";

// ── State ──────────────────────────────────────────────────────────────────
let chatHistory = [];
let currentPlan = null;

// ── DOM Refs ───────────────────────────────────────────────────────────────
const chatWindow   = document.getElementById("chatWindow");
const chatInput    = document.getElementById("chatInput");
const sendBtn      = document.getElementById("sendBtn");
const statusDot    = document.getElementById("statusDot");
const statusText   = document.getElementById("statusText");

// ── Navigation ─────────────────────────────────────────────────────────────
document.querySelectorAll(".nav-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`panel-${btn.dataset.panel}`).classList.add("active");

    // Lazy-load data on first visit
    if (btn.dataset.panel === "reminders") loadReminders();
    if (btn.dataset.panel === "notes") loadNotes();
    if (btn.dataset.panel === "planner") loadTasks();
  });
});

// ── Health Check ───────────────────────────────────────────────────────────
async function checkHealth() {
  try {
    const r = await fetch(`${FLASK_URL}/health`);
    if (r.ok) {
      statusDot.classList.add("online");
      statusText.textContent = "AI Online";
    } else throw new Error();
  } catch {
    statusDot.classList.add("offline");
    statusText.textContent = "Offline";
  }
}
checkHealth();

// ── Toast ──────────────────────────────────────────────────────────────────
function showToast(msg, type = "") {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.className = `toast ${type}`;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3000);
}

// ── Chat ───────────────────────────────────────────────────────────────────
function appendMessage(role, text) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.innerHTML = `
    <div class="avatar">${role === "assistant" ? "🤖" : "👤"}</div>
    <div class="bubble">${escapeHtml(text)}</div>
  `;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return div;
}

function appendTyping() {
  const div = document.createElement("div");
  div.className = "message assistant";
  div.id = "typingIndicator";
  div.innerHTML = `<div class="avatar">🤖</div><div class="bubble typing"></div>`;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function removeTyping() {
  const t = document.getElementById("typingIndicator");
  if (t) t.remove();
}

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  chatInput.value = "";
  chatInput.style.height = "auto";
  appendMessage("user", text);
  chatHistory.push({ role: "user", content: text });

  sendBtn.disabled = true;
  appendTyping();

  try {
    const res = await fetch(`${FLASK_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, history: chatHistory }),
    });

    removeTyping();

    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();

    appendMessage("assistant", data.reply);
    chatHistory.push({ role: "assistant", content: data.reply });

    if (data.side_effect) {
      showToast(`✅ Auto-created ${data.side_effect.type}`, "success");
    }
  } catch (err) {
    removeTyping();
    appendMessage("assistant", `⚠️ Sorry, something went wrong: ${err.message}`);
  } finally {
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

sendBtn.addEventListener("click", sendMessage);

chatInput.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Auto-resize textarea
chatInput.addEventListener("input", () => {
  chatInput.style.height = "auto";
  chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
});

document.getElementById("clearChat").addEventListener("click", () => {
  chatHistory = [];
  chatWindow.innerHTML = `
    <div class="message assistant">
      <div class="avatar">🤖</div>
      <div class="bubble">Chat cleared! How can I help you?</div>
    </div>`;
});

// ── Reminders ──────────────────────────────────────────────────────────────
async function loadReminders() {
  const list = document.getElementById("remindersList");
  list.innerHTML = `<div class="empty-state">Loading...</div>`;
  try {
    const res = await fetch(`${DJANGO_URL}/api/reminders/`);
    const data = await res.json();
    renderReminders(data.results || data);
  } catch {
    list.innerHTML = `<div class="empty-state">⚠️ Could not connect to Django backend. Make sure it's running on port 8000.</div>`;
  }
}

function renderReminders(items) {
  const list = document.getElementById("remindersList");
  if (!items.length) {
    list.innerHTML = `<div class="empty-state">No reminders yet. Create one above!</div>`;
    return;
  }
  list.innerHTML = items.map(r => `
    <div class="item-card ${r.completed ? 'done' : ''}" id="reminder-${r.id}">
      <div class="item-body">
        <div class="item-title">${escapeHtml(r.title)}</div>
        <div class="item-meta">
          ${r.due_date ? `📅 ${r.due_date}` : "No date"}
          ${r.due_time ? ` ⏰ ${r.due_time}` : ""}
        </div>
      </div>
      <span class="priority-badge priority-${r.priority}">${r.priority}</span>
      <div class="item-actions">
        <button class="btn-icon" onclick="toggleReminder(${r.id}, ${r.completed})" title="Toggle done">
          ${r.completed ? "↩️" : "✅"}
        </button>
        <button class="btn-icon" onclick="deleteReminder(${r.id})" title="Delete">🗑️</button>
      </div>
    </div>
  `).join("");
}

async function createReminder(payload) {
  const res = await fetch(`${DJANGO_URL}/api/reminders/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to create reminder");
  return res.json();
}

document.getElementById("createReminderBtn").addEventListener("click", async () => {
  const title    = document.getElementById("reminderTitle").value.trim();
  const due_date = document.getElementById("reminderDate").value;
  const due_time = document.getElementById("reminderTime").value;
  const priority = document.getElementById("reminderPriority").value;

  if (!title) { showToast("Please enter a title", "error"); return; }
  try {
    await createReminder({ title, due_date: due_date || null, due_time: due_time || null, priority });
    showToast("✅ Reminder created!", "success");
    document.getElementById("reminderTitle").value = "";
    loadReminders();
  } catch { showToast("❌ Failed to create reminder", "error"); }
});

document.getElementById("aiReminderBtn").addEventListener("click", async () => {
  const text = document.getElementById("aiReminderInput").value.trim();
  if (!text) { showToast("Describe your reminder first", "error"); return; }

  const btn = document.getElementById("aiReminderBtn");
  btn.textContent = "Creating...";
  btn.disabled = true;

  try {
    const res = await fetch(`${FLASK_URL}/api/reminder/ai`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    showToast(`✅ AI created: "${data.extracted?.title}"`, "success");
    document.getElementById("aiReminderInput").value = "";
    loadReminders();
  } catch { showToast("❌ AI creation failed", "error"); }
  finally { btn.textContent = "AI Create"; btn.disabled = false; }
});

async function toggleReminder(id, completed) {
  try {
    await fetch(`${DJANGO_URL}/api/reminders/${id}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completed: !completed }),
    });
    loadReminders();
  } catch { showToast("❌ Update failed", "error"); }
}

async function deleteReminder(id) {
  try {
    await fetch(`${DJANGO_URL}/api/reminders/${id}/`, { method: "DELETE" });
    showToast("Deleted", "");
    loadReminders();
  } catch { showToast("❌ Delete failed", "error"); }
}

// ── Notes ──────────────────────────────────────────────────────────────────
async function loadNotes() {
  const list = document.getElementById("notesList");
  list.innerHTML = `<div class="empty-state">Loading...</div>`;
  try {
    const res = await fetch(`${DJANGO_URL}/api/notes/`);
    const data = await res.json();
    renderNotes(data.results || data);
  } catch {
    list.innerHTML = `<div class="empty-state">⚠️ Could not connect to Django backend.</div>`;
  }
}

function renderNotes(items) {
  const list = document.getElementById("notesList");
  if (!items.length) {
    list.innerHTML = `<div class="empty-state">No notes yet.</div>`;
    return;
  }
  list.innerHTML = items.map(n => `
    <div class="item-card">
      <div class="item-body">
        <div class="item-title">${escapeHtml(n.title)}</div>
        <div class="item-meta">${escapeHtml(n.content?.slice(0, 100))}${n.content?.length > 100 ? "..." : ""}</div>
        ${n.summary ? `<div class="item-meta" style="margin-top:6px;color:var(--accent)">💡 ${escapeHtml(n.summary?.slice(0, 120))}</div>` : ""}
      </div>
      <div class="item-actions">
        <button class="btn-icon" onclick="deleteNote(${n.id})">🗑️</button>
      </div>
    </div>
  `).join("");
}

document.getElementById("saveNoteBtn").addEventListener("click", async () => {
  const title   = document.getElementById("noteTitle").value.trim();
  const content = document.getElementById("noteContent").value.trim();
  if (!title || !content) { showToast("Fill in title and content", "error"); return; }
  try {
    await fetch(`${DJANGO_URL}/api/notes/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, content }),
    });
    showToast("✅ Note saved!", "success");
    document.getElementById("noteTitle").value = "";
    document.getElementById("noteContent").value = "";
    loadNotes();
  } catch { showToast("❌ Save failed", "error"); }
});

document.getElementById("summarizeBtn").addEventListener("click", async () => {
  const title   = document.getElementById("noteTitle").value.trim() || "Untitled";
  const content = document.getElementById("noteContent").value.trim();
  if (!content) { showToast("Write some content first", "error"); return; }

  const btn = document.getElementById("summarizeBtn");
  btn.textContent = "🤖 Summarizing...";
  btn.disabled = true;

  try {
    const res = await fetch(`${FLASK_URL}/api/summarize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, text: content, save: true }),
    });
    const data = await res.json();
    document.getElementById("summaryText").textContent = data.summary;
    document.getElementById("summaryOutput").classList.remove("hidden");
    showToast("✅ Summarized & saved!", "success");
    loadNotes();
  } catch { showToast("❌ Summarization failed", "error"); }
  finally { btn.textContent = "🤖 AI Summarize & Save"; btn.disabled = false; }
});

async function deleteNote(id) {
  try {
    await fetch(`${DJANGO_URL}/api/notes/${id}/`, { method: "DELETE" });
    showToast("Deleted", "");
    loadNotes();
  } catch { showToast("❌ Delete failed", "error"); }
}

// ── Planner ────────────────────────────────────────────────────────────────
async function loadTasks() {
  const list = document.getElementById("tasksList");
  list.innerHTML = `<div class="empty-state">Loading...</div>`;
  try {
    const res = await fetch(`${DJANGO_URL}/api/tasks/`);
    const data = await res.json();
    renderTasks(data.results || data);
  } catch {
    list.innerHTML = `<div class="empty-state">⚠️ Could not connect to Django backend.</div>`;
  }
}

function renderTasks(items) {
  const list = document.getElementById("tasksList");
  if (!items.length) {
    list.innerHTML = `<div class="empty-state">No tasks yet. Generate a plan above!</div>`;
    return;
  }
  list.innerHTML = items.map(t => `
    <div class="item-card ${t.completed ? 'done' : ''}">
      <div class="item-body">
        <div class="item-title">${escapeHtml(t.title)}</div>
        ${t.description ? `<div class="item-meta">${escapeHtml(t.description?.slice(0, 120))}...</div>` : ""}
      </div>
      <span class="priority-badge priority-${t.priority}">${t.priority}</span>
      <div class="item-actions">
        <button class="btn-icon" onclick="toggleTask(${t.id}, ${t.completed})">${t.completed ? "↩️" : "✅"}</button>
        <button class="btn-icon" onclick="deleteTask(${t.id})">🗑️</button>
      </div>
    </div>
  `).join("");
}

document.getElementById("generatePlanBtn").addEventListener("click", async () => {
  const goal = document.getElementById("plannerGoal").value.trim();
  if (!goal) { showToast("Describe your goal first", "error"); return; }

  const btn = document.getElementById("generatePlanBtn");
  btn.textContent = "⏳ Planning...";
  btn.disabled = true;

  try {
    const res = await fetch(`${FLASK_URL}/api/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal }),
    });
    const data = await res.json();
    currentPlan = data;
    document.getElementById("planText").textContent = data.plan;
    document.getElementById("planOutput").classList.remove("hidden");
    document.getElementById("savePlanBtn").disabled = false;
    showToast("✅ Plan generated!", "success");
  } catch { showToast("❌ Planning failed", "error"); }
  finally { btn.textContent = "🚀 Generate Plan"; btn.disabled = false; }
});

document.getElementById("savePlanBtn").addEventListener("click", async () => {
  if (!currentPlan) return;
  const btn = document.getElementById("savePlanBtn");
  btn.textContent = "Saving...";
  btn.disabled = true;

  try {
    await fetch(`${FLASK_URL}/api/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal: currentPlan.goal, save: true }),
    });
    showToast("✅ Saved to tasks!", "success");
    loadTasks();
  } catch { showToast("❌ Save failed", "error"); }
  finally { btn.textContent = "💾 Save to Tasks"; btn.disabled = false; }
});

async function toggleTask(id, completed) {
  try {
    await fetch(`${DJANGO_URL}/api/tasks/${id}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completed: !completed }),
    });
    loadTasks();
  } catch { showToast("❌ Update failed", "error"); }
}

async function deleteTask(id) {
  try {
    await fetch(`${DJANGO_URL}/api/tasks/${id}/`, { method: "DELETE" });
    showToast("Deleted", "");
    loadTasks();
  } catch { showToast("❌ Delete failed", "error"); }
}

// ── Utility ────────────────────────────────────────────────────────────────
function escapeHtml(str = "") {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
