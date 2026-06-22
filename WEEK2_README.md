# 🤖 AI Personal Assistant — Week 2
### Frontend Development & Flask Backend Setup

> **Project 25 | 4-Week AI Development Roadmap**
> Week 2 of 4 — Building the Conversational Chat Interface and Flask API Gateway

---

## 📌 Week 2 Overview

This week focuses on bringing the project to life visually and functionally. We built the full frontend dashboard using HTML, CSS, and JavaScript, set up all Flask API routes, and connected the frontend to the Flask backend. By the end of this week, the chat interface is fully operational and all four panels (Chat, Reminders, Notes, Planner) are wired up and ready.

---

## ✅ Week 2 Goals & Progress

| Goal | Status |
|------|--------|
| Build Conversational AI Chat Interface | ✅ Done |
| Develop frontend with HTML, CSS, JavaScript | ✅ Done |
| Setup Flask APIs | ✅ Done |
| Implement user input and response handling | ✅ Done |
| Create basic assistant dashboard | ✅ Done |
| Connect frontend with Flask backend | ✅ Done |

---

## 🗂️ Files Added This Week

```
flask-app/
├── app.py                    ← Flask app with all API routes
├── requirements.txt          ← Flask dependencies
├── .env.example              ← Environment variable template
├── templates/
│   └── index.html            ← Full SPA dashboard (4 panels)
└── static/
    ├── css/
    │   └── style.css         ← Dark-themed responsive design
    └── js/
        └── app.js            ← All frontend logic & API calls
```

---

## 🖥️ What Was Built

### 1. Conversational Chat Interface
A multi-turn chat UI with typing indicators, message bubbles, auto-scroll, and conversation history. Users can type messages and receive AI responses in real time.

**Features:**
- User and assistant message bubbles with avatars
- Typing indicator (animated dots) while waiting for AI
- Shift+Enter for new line, Enter to send
- Auto-resizing textarea
- Clear chat button that resets conversation history
- Last 10 messages sent as context to the AI

### 2. Assistant Dashboard (4 Panels)
A sidebar-navigation app with four sections, each accessible via the sidebar:

| Panel | Description |
|-------|-------------|
| 💬 Chat | Main AI conversation interface |
| ⏰ Reminders | Create, list, toggle, and delete reminders |
| 📝 Notes | Write notes, view saved notes |
| 📅 Planner | Input goals, see productivity plans |

### 3. Flask API Routes

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/` | Serves the frontend HTML |
| `GET` | `/health` | Service health check |
| `POST` | `/api/chat` | Accepts message + history, returns AI reply |
| `POST` | `/api/summarize` | Summarizes note text using AI |
| `POST` | `/api/plan` | Generates a productivity plan from a goal |
| `POST` | `/api/reminder/ai` | Extracts reminder details from natural language |

### 4. Frontend ↔ Flask Connection
All frontend API calls go through `fetch()` in `app.js`. The chat panel talks to Flask at `/api/chat`. The reminders, notes, and tasks panels are pre-wired to call Django (port 8000) — ready for Week 3.

---

## 🚀 How to Run (Week 2)

### Prerequisites
- Python 3.10+
- OpenAI API key (get one at https://platform.openai.com/api-keys)

### Setup

```bash
# 1. Navigate to flask-app
cd flask-app

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Open .env and paste your OpenAI API key

# 5. Run Flask
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

> ⚠️ **Note:** At this stage, Reminders, Notes, and Planner panels show "Could not connect to Django backend" — this is expected. Django is built in Week 3.

---

## 📡 API Usage Examples

### Chat
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What should I focus on today?",
    "history": []
  }'
```
**Response:**
```json
{
  "reply": "Great question! I'd suggest starting with your highest-priority task...",
  "side_effect": null
}
```

### Intent Detection (Auto Reminder)
If you say "remind me to..." in chat, Flask auto-detects it and tries to create a reminder:
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Remind me to submit the assignment tomorrow", "history": []}'
```
**Response:**
```json
{
  "reply": "Got it! I'll remind you to submit your assignment tomorrow. ...",
  "side_effect": {"type": "reminder", "status": "django_unavailable"}
}
```
(`django_unavailable` is normal in Week 2 — Django isn't running yet.)

### Health Check
```bash
curl http://localhost:5000/health
# {"status": "ok", "service": "flask-ai-gateway"}
```

---

## 🎨 UI Design Decisions

- **Dark theme** (`#0f1117` background) — reduces eye strain during long coding/planning sessions
- **Sidebar navigation** — keeps all four tools accessible without page reloads
- **Accent color** `#6c63ff` (indigo) — used for active states, AI bubbles, and focus outlines
- **Inter font** — clean, modern, highly readable at small sizes
- **Responsive layout** — sidebar collapses to icon-only on small screens
- **Toast notifications** — brief non-blocking feedback for every action

---

## 🧠 Prompt Engineering (Week 2 Introduction)

Flask uses carefully written system prompts for each AI feature. This week we defined three:

**Chat Prompt** — friendly assistant, acknowledges reminders/notes by name, stays concise.

**Summarizer Prompt** — extracts key points as bullets, leads with a TL;DR, flags action items with ✅.

**Planner Prompt** — breaks goals into steps with priority levels (High/Medium/Low) and time estimates.

Full prompts are in `flask-app/app.py` at the top under `# System Prompts`.

---

## 🔗 Frontend Architecture

```
index.html
│
├── Sidebar nav → switches active panel via data-panel attribute
│
├── Panel: Chat
│   ├── chatWindow (scrollable message list)
│   ├── chatInput (auto-resize textarea)
│   └── sendBtn → POST /api/chat → appendMessage()
│
├── Panel: Reminders
│   ├── AI Create → POST /api/reminder/ai (Flask)
│   ├── Manual Create → POST /api/reminders/ (Django - Week 3)
│   └── List → GET /api/reminders/ (Django - Week 3)
│
├── Panel: Notes
│   ├── AI Summarize → POST /api/summarize (Flask)
│   ├── Save Note → POST /api/notes/ (Django - Week 3)
│   └── List → GET /api/notes/ (Django - Week 3)
│
└── Panel: Planner
    ├── Generate Plan → POST /api/plan (Flask)
    ├── Save to Tasks → POST /api/tasks/ (Django - Week 3)
    └── List → GET /api/tasks/ (Django - Week 3)
```

---

## 📦 Dependencies

**flask-app/requirements.txt**

| Package | Version | Purpose |
|---------|---------|---------|
| `flask` | 3.0.3 | Web framework, routing, templates |
| `flask-cors` | 4.0.1 | Allow cross-origin requests from frontend |
| `openai` | 1.35.3 | OpenAI Python SDK for GPT-3.5 |
| `python-dotenv` | 1.0.1 | Load `.env` variables |
| `requests` | 2.32.3 | HTTP calls from Flask to Django |

---

## 🐛 Known Limitations (Fixed in Later Weeks)

| Issue | Fix |
|-------|-----|
| Reminders/Notes/Tasks panels show error | Django built in Week 3 |
| No real data persistence yet | SQLite added in Week 3 |
| No user authentication | Out of scope for this project |
| OpenAI rate limits not handled gracefully | Improved in Week 4 |

---

## 🔜 Coming in Week 3

- Django backend with SQLite database
- `Reminder`, `Note`, `Task` models and full CRUD APIs
- All four dashboard panels become fully functional with real data
- Flask calls Django's REST API to persist AI-generated content

---

## 📸 Screenshots

> *Add screenshots of your running app here before submitting.*
> Tip: `Win + Shift + S` (Windows) or `Cmd + Shift + 4` (Mac) to screenshot.

| Chat Interface | Reminders Panel |
|---|---|
| `[screenshot]` | `[screenshot]` |

---

## 🔗 Resources Used This Week

- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [MDN Web Docs — fetch()](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [Flask-CORS](https://flask-cors.readthedocs.io/)
- [Google Fonts — Inter](https://fonts.google.com/specimen/Inter)

---

## 👨‍💻 Author

**Your Name** | [GitHub](https://github.com/YOUR_USERNAME) | [LinkedIn](https://linkedin.com/in/YOUR_PROFILE)

---

*Week 1 ← | → [Week 3](../week3/README.md)*
