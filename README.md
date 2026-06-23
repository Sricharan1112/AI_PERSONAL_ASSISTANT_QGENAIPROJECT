# AI Assistant — Project Setup (Week 1)

This repo contains two parallel implementations of the same AI Assistant
backend — one in **Flask**, one in **Django** — so you can compare them
hands-on before committing to one for the rest of the project.

## 🌐 Project Website
[ai-roadmap-website.html](https://Sricharan1112/AI_PERSONAL_ASSISTANT_QGENAIPROJECT/)

Both implement the same architecture:

```
Client → Route/View handler → Prompt builder → LLM API → Response handler → Client
                  ↕
            SQLite database
```

## Structure

```
ai-assistant-project/
├── shared/
│   └── schema.sql          # Reference schema (both apps implement this shape)
├── flask-app/
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routes/         # Blueprints (route handlers)
│   │   └── services/       # LLM API call logic
│   ├── config.py
│   ├── run.py
│   └── requirements.txt
└── django-app/
    ├── config/              # Project settings, URLs, WSGI
    ├── assistant/           # The Django "app" — models, views, urls
    │   └── services/        # LLM API call logic
    ├── manage.py
    └── requirements.txt
```

## Database schema

Three tables: `users`, `conversations`, `messages`.

- A `conversation` belongs to a `user`.
- A `message` belongs to a `conversation` and has a `role`
  (`user` / `assistant` / `system`) matching the LLM API's own message format.
- See `shared/schema.sql` for the canonical definition.

Flask implements this via SQLAlchemy models (`flask-app/app/models/models.py`).
Django implements the same shape via its ORM (`django-app/assistant/models.py`)
and generates the actual SQL through migrations.

## Getting started — Flask

```bash
cd flask-app
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in your ANTHROPIC_API_KEY
python run.py
```

## Getting started — Django

```bash
cd django-app
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then fill in your ANTHROPIC_API_KEY
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin access
python manage.py runserver
```

## Key differences you'll notice

| | Flask | Django |
|---|---|---|
| Boilerplate | Minimal — you choose your own structure | More upfront — fixed project layout |
| Database access | SQLAlchemy (you write models, `db.create_all()`) | Built-in ORM + migrations (`makemigrations`/`migrate`) |
| User auth | You build it or add a library | Built-in `User` model + auth system |
| Admin UI | None by default | Free admin panel at `/admin` |
| Best for | Small APIs, full control, fast prototyping | Larger apps, built-in batteries, less custom plumbing |

## Next steps

- Wire up a frontend (or test with `curl`/Postman first)
- Add streaming responses from the LLM API
- Add proper authentication (sessions or JWT)
- Move `ANTHROPIC_API_KEY` handling into environment-specific secrets before deploying

---

## Week 2 — Frontend (chat UI + dashboard)

The runnable frontend lives in `flask-app-runnable/` (zero extra pip
installs beyond Flask — uses stdlib `sqlite3` + `urllib` instead of
SQLAlchemy/anthropic-sdk, so you can get it running immediately).

### Run it

```bash
cd flask-app-runnable
export ANTHROPIC_API_KEY=sk-ant-your-key-here
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
python3 app.py
```

Then open:
- `http://127.0.0.1:5000/` — redirects to `/login` if you're not signed in
- Sign up for an account, then you'll land on the dashboard / can visit `/chat`

### What's in it

```
flask-app-runnable/
├── app.py                  # Flask app: page routes + JSON API routes
├── templates/
│   ├── chat.html            # Chat interface (sidebar + message pane + composer)
│   └── dashboard.html       # Conversation list + stats
└── static/
    ├── css/
    │   ├── base.css          # Design tokens + shared status bar
    │   ├── chat.css           # Chat-specific styles
    │   └── dashboard.css      # Dashboard-specific styles
    └── js/
        ├── chat.js            # Message sending/rendering, sidebar refresh
        └── dashboard.js        # Stats + conversation table, delete handling
```

### Design direction

Dark "dev-tool" aesthetic: near-black surfaces, hairline borders, a
single amber accent (`--accent: #FF9E2C`), `JetBrains Mono` for
structural/UI text paired with `Inter` for message content. Messages
are tagged `[user]` / `[assistant]` rather than rendered as avatar
bubbles, and the composer uses a terminal-style `>` prompt — reinforces
the dev-tool identity instead of defaulting to a generic chat-bubble look.

All tokens live in `static/css/base.css` as CSS custom properties if
you want to retheme.

### API endpoints this frontend uses

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Status bar connection indicator |
| `POST` | `/api/auth/signup` | Create an account, log in immediately |
| `POST` | `/api/auth/login` | Log in with username/password |
| `POST` | `/api/auth/logout` | Clear the session |
| `GET` | `/api/auth/me` | Current logged-in user (used for "am I logged in?" checks) |
| `POST` | `/api/conversations` | Create a new conversation (owned by the logged-in user) |
| `GET` | `/api/conversations` | List the logged-in user's conversations |
| `DELETE` | `/api/conversations/<id>` | Delete a conversation (only if you own it) |
| `POST` | `/api/conversations/<id>/messages` | Send a message, get assistant reply |
| `GET` | `/api/conversations/<id>/messages` | Load conversation history |

### Authentication

Session-based auth using Flask's signed-cookie `session` (no Flask-Login
needed). Passwords are hashed with PBKDF2-HMAC-SHA256 (`hashlib`, stdlib)
plus a random per-user salt (`secrets.token_hex`) — no external hashing
library required.

- `/`, `/chat`, and all `/api/conversations*` routes require login —
  unauthenticated browser requests redirect to `/login`; unauthenticated
  API/fetch requests get a `401` JSON response.
- Every conversation is scoped to `user_id`. Reading, sending to, or
  deleting another user's conversation returns `404` (not `403`) — this
  is deliberate, so a user can't even confirm that a given conversation
  ID belongs to someone else.
- Login failures (wrong password vs. nonexistent username) return the
  identical error message and status code, to avoid leaking which
  usernames exist.
- **Before deploying anywhere beyond local dev**: set a real `SECRET_KEY`
  env var (the default is a placeholder), and serve over HTTPS — Flask's
  session cookie isn't marked `Secure` by default, which matters once
  this leaves localhost.

### Markdown rendering

Assistant replies are rendered as markdown client-side using `marked.js`,
sanitized through `DOMPurify` before insertion into the DOM (both via
CDN — no install needed). User messages stay as plain text. Code blocks,
tables, lists, and links are styled in `chat.css` to match the dark
theme.

### Settings page (`/settings`)

Account management, reachable from the nav bar on every page once logged in:

- **Account stats** — member-since date, total conversations, total messages
- **Assistant personality** — a per-user custom system prompt (up to 2000
  chars), stored on the `users` row and passed into every LLM call for
  that user's conversations. Empty = falls back to the app's default
  prompt. This is genuinely wired in — `send_message` looks up the
  user's `system_prompt` before calling the LLM, not just stored and
  unused.
- **Change username** — same validation as signup, rejects duplicates
- **Change password** — requires the current password before accepting
  a new one (so a logged-in-but-unattended session can't be used to lock
  out the real owner)
- **Delete account** — requires a password confirmation; cascades to
  delete all of that user's conversations and messages via the existing
  foreign key `ON DELETE CASCADE`

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/settings/profile` | Stats + current system prompt for the settings page |
| `PUT` | `/api/settings/username` | Change username |
| `PUT` | `/api/settings/password` | Change password (requires current password) |
| `PUT` | `/api/settings/system-prompt` | Set/clear the custom system prompt |
| `DELETE` | `/api/settings/account` | Delete account (requires password) |

### Known limitations to revisit later

- No streaming — the assistant reply waits for the full response before showing it (a "Thinking…" placeholder fills the gap)
- No "forgot password" flow — this is local single-user dev auth, not production-grade
- No rate limiting on login/signup attempts
- `SECRET_KEY` defaults to a placeholder — must be overridden before any real deployment


