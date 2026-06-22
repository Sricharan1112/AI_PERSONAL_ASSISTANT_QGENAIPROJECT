# 🤖 AI Personal Assistant — Week 3
### Django Integration & AI Features Development

> **Project 25 | 4-Week AI Development Roadmap**
> Week 3 of 4 — Building the Django Backend, Database, and Full AI Feature Modules

---

## 📌 Week 3 Overview

This week is where the app becomes truly functional. We built the entire Django backend — models, serializers, viewsets, URL routing, and the admin panel — and connected it to the Flask AI gateway from Week 2. All four dashboard panels now work end-to-end with real data persisted in SQLite. The three AI feature modules (Reminder Assistant, Note Summarizer, Productivity Planner) are fully operational.

---

## ✅ Week 3 Goals & Progress

| Goal | Status |
|------|--------|
| Integrate Django backend components | ✅ Done |
| Configure database operations (SQLite) | ✅ Done |
| Implement AI Reminder Assistant | ✅ Done |
| Develop AI Note Summarizer | ✅ Done |
| Build AI Productivity Planner | ✅ Done |
| Create personalized response functionality | ✅ Done |

---

## 🗂️ Files Added This Week

```
django-app/
├── manage.py                         ← Django CLI entry point
├── requirements.txt                  ← Django dependencies
├── db.sqlite3                        ← Auto-created on first migrate
├── core/
│   ├── __init__.py
│   ├── settings.py                   ← CORS, DRF, installed apps config
│   ├── urls.py                       ← Root URL dispatcher
│   └── wsgi.py                       ← WSGI server entry point
└── assistant/
    ├── __init__.py
    ├── models.py                     ← Reminder, Note, Task models
    ├── serializers.py                ← DRF serializers (JSON ↔ model)
    ├── views.py                      ← ViewSets + stats endpoint
    ├── urls.py                       ← API routing via DRF router
    ├── admin.py                      ← Django admin panel registration
    └── migrations/
        ├── __init__.py
        └── 0001_initial.py           ← Auto-generated migration
```

---

## 🏗️ Architecture This Week

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (Week 2)                   │
│              HTML + CSS + JavaScript                    │
└────────────┬────────────────────┬───────────────────────┘
             │                    │
             ▼                    ▼
┌────────────────────┐  ┌────────────────────────────────┐
│   FLASK (port 5000)│  │  ✨ DJANGO (port 8000) NEW      │
│   AI Gateway       │  │     Data Backend                │
│                    │  │                                 │
│  /api/chat         │  │  /api/reminders/   CRUD         │
│  /api/summarize  ──┼──▶  /api/notes/       CRUD         │
│  /api/plan         │  │  /api/tasks/       CRUD         │
│  /api/reminder/ai──┼──▶  /api/stats/       Dashboard    │
└────────────────────┘  └────────────────┬────────────────┘
                                          │
                                          ▼
                                 ┌──────────────────┐
                                 │  SQLite Database  │
                                 │  (db.sqlite3)     │
                                 │                   │
                                 │  ├─ reminder      │
                                 │  ├─ note          │
                                 │  └─ task          │
                                 └──────────────────┘
```

**Key principle:** Flask never touches the database directly. When the AI creates a reminder or saves a summarized note, Flask calls Django's REST API via HTTP. Django owns all data.

---

## 🗄️ Database Models

### Reminder Model
Stores user reminders with optional due date/time and priority level.

```python
class Reminder(models.Model):
    title       = CharField(max_length=255)
    description = TextField(blank=True)
    due_date    = DateField(null=True, blank=True)
    due_time    = TimeField(null=True, blank=True)
    priority    = CharField(choices=['low','medium','high'], default='medium')
    completed   = BooleanField(default=False)
    created_at  = DateTimeField(auto_now_add=True)
    updated_at  = DateTimeField(auto_now=True)
```

### Note Model
Stores raw notes plus an optional AI-generated summary field.

```python
class Note(models.Model):
    title      = CharField(max_length=255)
    content    = TextField()
    summary    = TextField(blank=True)    # ← filled by Flask AI Summarizer
    tags       = CharField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Task Model
Stores productivity tasks, including full AI-generated plans in the `description` field.

```python
class Task(models.Model):
    title       = CharField(max_length=255)
    description = TextField(blank=True)   # ← AI-generated plan text
    priority    = CharField(choices=['low','medium','high'], default='medium')
    completed   = BooleanField(default=False)
    due_date    = DateField(null=True, blank=True)
    created_at  = DateTimeField(auto_now_add=True)
    updated_at  = DateTimeField(auto_now=True)
```

---

## 📡 Django REST API — Full Reference

All endpoints are under `http://127.0.0.1:8000/api/`

### Reminders

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/reminders/` | List all reminders |
| `POST` | `/api/reminders/` | Create a reminder |
| `GET` | `/api/reminders/<id>/` | Get one reminder |
| `PUT` | `/api/reminders/<id>/` | Full update |
| `PATCH` | `/api/reminders/<id>/` | Partial update (e.g. toggle `completed`) |
| `DELETE` | `/api/reminders/<id>/` | Delete |
| `POST` | `/api/reminders/<id>/complete/` | Mark as done (shortcut) |
| `GET` | `/api/reminders/pending/` | Only incomplete reminders |

**Filter params:**
```
GET /api/reminders/?priority=high
GET /api/reminders/?completed=false
```

### Notes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/notes/` | List all notes |
| `POST` | `/api/notes/` | Create a note |
| `GET` | `/api/notes/<id>/` | Get one note |
| `PUT` | `/api/notes/<id>/` | Full update |
| `PATCH` | `/api/notes/<id>/` | Partial update |
| `DELETE` | `/api/notes/<id>/` | Delete |

**Search param:**
```
GET /api/notes/?search=python
```

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tasks/` | List all tasks |
| `POST` | `/api/tasks/` | Create a task |
| `GET` | `/api/tasks/<id>/` | Get one task |
| `PUT` | `/api/tasks/<id>/` | Full update |
| `PATCH` | `/api/tasks/<id>/` | Partial update |
| `DELETE` | `/api/tasks/<id>/` | Delete |
| `POST` | `/api/tasks/<id>/complete/` | Mark as done |

### Dashboard Stats

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/stats/` | Aggregated counts for all three models |

**Response:**
```json
{
  "reminders": { "total": 5, "pending": 3, "high_priority": 1 },
  "notes":     { "total": 8, "with_summary": 6 },
  "tasks":     { "total": 4, "completed": 1, "pending": 3 }
}
```

---

## 🤖 AI Feature Modules

### Module 1: AI Reminder Assistant
**Flask endpoint:** `POST /api/reminder/ai`
**Django endpoint:** `POST /api/reminders/`

The user types a natural-language reminder: *"Remind me to submit the report tomorrow at 9am"*. Flask sends this to OpenAI with an extraction prompt. The model returns structured JSON:

```json
{
  "title": "Submit the report",
  "due_date": "2025-07-24",
  "due_time": "09:00",
  "priority": "high"
}
```

Flask then `POST`s this to Django's `/api/reminders/` to persist it. The frontend shows it immediately in the Reminders panel.

**System prompt used:**
```
Extract reminder details from the user's message.
Return a JSON object with keys: title, due_date (YYYY-MM-DD or null),
due_time (HH:MM or null), priority (high/medium/low).
Respond ONLY with the JSON object.
```

---

### Module 2: AI Note Summarizer
**Flask endpoint:** `POST /api/summarize`
**Django endpoint:** `POST /api/notes/`

User writes a raw note and clicks "AI Summarize & Save". Flask sends the text to OpenAI, gets back a structured summary, then saves both the original content and the summary to Django's `Note` model.

**Summary format the AI returns:**
```
TL;DR: [1-2 sentence overview]

Key Points:
• Point 1
• Point 2
• Point 3

✅ Action Items:
• Follow up with X
• Submit Y by Friday
```

The `summary` field is stored separately from `content` in the database, so both are always retrievable.

---

### Module 3: AI Productivity Planner
**Flask endpoint:** `POST /api/plan`
**Django endpoint:** `POST /api/tasks/`

User enters a goal: *"Build a portfolio website in 2 weeks"*. Flask calls OpenAI with the planner system prompt and returns a step-by-step plan. User clicks "Save to Tasks" and Flask calls Django to store it as a `Task` record.

**Plan format:**
```
📌 Goal: Build a portfolio website in 2 weeks

Week 1 — Foundation
  [High] Set up project repo and choose tech stack — 2 hrs
  [High] Design wireframes for 3 pages — 3 hrs
  [Medium] Build homepage with responsive layout — 4 hrs
  ...

Week 2 — Polish & Launch
  ...

💡 Tip: Start with the homepage — completing one page early builds momentum.
```

---

## 🚀 How to Run (Week 3)

Both Flask (Week 2) and Django must run simultaneously.

### Terminal 1 — Django
```bash
cd django-app

python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Create the database tables
python manage.py migrate

# Optional: create an admin account for /admin panel
python manage.py createsuperuser

# Start the server
python manage.py runserver
# → Running at http://127.0.0.1:8000
```

### Terminal 2 — Flask (same as Week 2)
```bash
cd flask-app
source venv/bin/activate
python app.py
# → Running at http://127.0.0.1:5000
```

Open **http://127.0.0.1:5000** — all four panels are now fully functional.

---

## 🧪 Manual API Tests

```bash
# Create a reminder manually
curl -X POST http://localhost:8000/api/reminders/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Team meeting", "due_date": "2025-07-25", "priority": "high"}'

# List all reminders
curl http://localhost:8000/api/reminders/

# Only pending (incomplete) reminders
curl http://localhost:8000/api/reminders/pending/

# Mark reminder #1 as done
curl -X POST http://localhost:8000/api/reminders/1/complete/

# Create a note
curl -X POST http://localhost:8000/api/notes/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Django Notes", "content": "DRF makes REST APIs very fast to build."}'

# Search notes
curl http://localhost:8000/api/notes/?search=Django

# Dashboard stats
curl http://localhost:8000/api/stats/
```

---

## 🛠️ Django Admin Panel

Django ships with a built-in admin interface at `/admin`. After running `createsuperuser`:

1. Go to `http://127.0.0.1:8000/admin/`
2. Log in with your superuser credentials
3. You can view, edit, filter, and delete all Reminders, Notes, and Tasks

The admin is configured in `assistant/admin.py` with search, filter, and column display for each model.

---

## ⚙️ Django Configuration Highlights

### CORS (Cross-Origin Resource Sharing)
Since Flask (port 5000) and the frontend call Django (port 8000), CORS must be enabled:

```python
# core/settings.py
INSTALLED_APPS = [..., "corsheaders", ...]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # ← must be FIRST
    ...
]

CORS_ALLOW_ALL_ORIGINS = True  # Restrict in production
```

### Django REST Framework
```python
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}
```

### DRF Router (auto-generates all URLs)
```python
# assistant/urls.py
router = DefaultRouter()
router.register(r"reminders", ReminderViewSet, basename="reminder")
router.register(r"notes",     NoteViewSet,     basename="note")
router.register(r"tasks",     TaskViewSet,     basename="task")
```
One line per model generates all 6 CRUD endpoints automatically.

---

## 📦 Dependencies

**django-app/requirements.txt**

| Package | Version | Purpose |
|---------|---------|---------|
| `django` | 5.0.6 | Web framework, ORM, admin, migrations |
| `djangorestframework` | 3.15.2 | REST API ViewSets, serializers, routing |
| `django-cors-headers` | 4.3.1 | Allow cross-origin requests from Flask + frontend |
| `python-dotenv` | 1.0.1 | Load `.env` variables |

---

## 🔄 How Flask and Django Work Together

Here's the exact flow when a user clicks "AI Summarize & Save":

```
1. User clicks button in browser
         ↓
2. app.js → POST /api/summarize (Flask:5000)
         ↓
3. Flask calls OpenAI API
         ↓
4. OpenAI returns summary text
         ↓
5. Flask → POST /api/notes/ (Django:8000)
         ↓
6. Django serializer validates data
         ↓
7. Django ORM saves to SQLite
         ↓
8. Django returns saved Note object (JSON)
         ↓
9. Flask returns summary + save status to frontend
         ↓
10. app.js displays summary, reloads notes list
```

---

## 🐛 Common Issues & Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| `No such table: assistant_reminder` | Migration not run | Run `python manage.py migrate` |
| CORS error in browser console | corsheaders not first in MIDDLEWARE | Move it to top of MIDDLEWARE list |
| Django 8000 not reachable from Flask | Both not running | Open two separate terminals |
| `ModuleNotFoundError: rest_framework` | DRF not installed | Run `pip install -r requirements.txt` |
| Admin panel shows no models | `admin.py` not configured | Check `assistant/admin.py` |

---

## 📸 Screenshots

> *Add screenshots of the working app before submitting.*

| Reminders Panel | Notes with AI Summary |
|---|---|
| `[screenshot]` | `[screenshot]` |

| Planner Output | Django Admin Panel |
|---|---|
| `[screenshot]` | `[screenshot]` |

---

## 🔜 Coming in Week 4

- Real OpenAI API integrated across all endpoints
- Prompt optimization for better AI responses
- Error handling for API rate limits and failures
- UI/UX improvements and responsiveness polish
- Testing and debugging full end-to-end
- Deployment (Render / Railway)
- Final README, demo video, GitHub cleanup

---

## 🔗 Resources Used This Week

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [django-cors-headers](https://pypi.org/project/django-cors-headers/)
- [DRF ViewSets](https://www.django-rest-framework.org/api-guide/viewsets/)
- [DRF Serializers](https://www.django-rest-framework.org/api-guide/serializers/)
- [Django ORM Queries](https://docs.djangoproject.com/en/5.0/topics/db/queries/)

---

## 👨‍💻 Author

**Your Name** | [GitHub](https://github.com/YOUR_USERNAME) | [LinkedIn](https://linkedin.com/in/YOUR_PROFILE)

---

*[← Week 2](../week2/README.md) | → Week 4*
