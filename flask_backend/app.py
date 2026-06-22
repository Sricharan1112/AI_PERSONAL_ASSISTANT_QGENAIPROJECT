"""
app.py - Main Flask application.

Responsibilities (per the roadmap):
  Week 2: Serve the frontend, handle chat input/response
  Week 3: Trigger AI feature logic (summarizer, planner) on top of
          data stored in Django
  Week 4: Real OpenAI integration, robust error handling

Flask is intentionally a thin layer:
  - It does NOT define its own database models.
  - All persistence goes through services/django_client.py.
  - All LLM calls go through services/ai_service.py.
"""

import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from config import Config
from services import ai_service, django_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app, origins=Config.CORS_ORIGINS)


# ------------------------------------------------------------------
# Error handling helpers
# ------------------------------------------------------------------
@app.errorhandler(ai_service.AIServiceError)
def handle_ai_error(err):
    return jsonify({"error": err.message}), err.status_code


@app.errorhandler(django_client.DjangoAPIError)
def handle_django_error(err):
    return jsonify({"error": err.message}), err.status_code


@app.errorhandler(404)
def handle_404(err):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def handle_500(err):
    logger.exception("Unhandled server error")
    return jsonify({"error": "Internal server error"}), 500


# ------------------------------------------------------------------
# Frontend serving
# ------------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "flask-ai-layer"})


# ------------------------------------------------------------------
# Chat (Week 2 + Week 4)
# ------------------------------------------------------------------
@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    user_message = (payload.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    # Pull recent history from Django so the AI has context.
    # If Django is unreachable, fall back to no history rather than failing.
    history = []
    try:
        raw_history = django_client.list_chat_history() or []
        items = raw_history.get("results", raw_history) if isinstance(raw_history, dict) else raw_history
        for item in items[-10:]:
            history.append({"role": item["role"], "content": item["content"]})
    except django_client.DjangoAPIError:
        logger.warning("Could not load chat history from Django; continuing without it.")

    reply = ai_service.get_chat_reply(user_message, history=history)

    # Persist both turns (best-effort; don't fail the chat if this fails)
    try:
        django_client.save_chat_message("user", user_message)
        django_client.save_chat_message("assistant", reply)
    except django_client.DjangoAPIError:
        logger.warning("Could not persist chat history to Django.")

    return jsonify({"reply": reply})


@app.route("/api/chat/history", methods=["GET"])
def chat_history():
    history = django_client.list_chat_history()
    return jsonify(history)


# ------------------------------------------------------------------
# Reminders (Week 3) - thin pass-through + optional AI parsing
# ------------------------------------------------------------------
@app.route("/api/reminders", methods=["GET"])
def get_reminders():
    return jsonify(django_client.list_reminders())


@app.route("/api/reminders", methods=["POST"])
def add_reminder():
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    if not title:
        return jsonify({"error": "Reminder title is required."}), 400

    data = {
        "title": title,
        "description": payload.get("description", ""),
        "remind_at": payload.get("remind_at"),
    }
    created = django_client.create_reminder(data)
    return jsonify(created), 201


@app.route("/api/reminders/<int:reminder_id>", methods=["PATCH"])
def edit_reminder(reminder_id):
    payload = request.get_json(silent=True) or {}
    updated = django_client.update_reminder(reminder_id, payload)
    return jsonify(updated)


@app.route("/api/reminders/<int:reminder_id>", methods=["DELETE"])
def remove_reminder(reminder_id):
    django_client.delete_reminder(reminder_id)
    return "", 204


# ------------------------------------------------------------------
# AI Note Summarizer (Week 3 + Week 4)
# ------------------------------------------------------------------
@app.route("/api/notes", methods=["GET"])
def get_notes():
    return jsonify(django_client.list_notes())


@app.route("/api/notes", methods=["POST"])
def add_note():
    payload = request.get_json(silent=True) or {}
    content = (payload.get("content") or "").strip()
    if not content:
        return jsonify({"error": "Note content is required."}), 400

    summary = ai_service.summarize_note(content)

    data = {
        "title": payload.get("title", ""),
        "content": content,
        "summary": summary,
    }
    created = django_client.create_note(data)
    return jsonify(created), 201


@app.route("/api/notes/<int:note_id>/resummarize", methods=["POST"])
def resummarize_note(note_id):
    """Re-run the AI summarizer on an existing note's content."""
    payload = request.get_json(silent=True) or {}
    content = payload.get("content", "")
    summary = ai_service.summarize_note(content)
    updated = django_client.update_note(note_id, {"summary": summary})
    return jsonify(updated)


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def remove_note(note_id):
    django_client.delete_note(note_id)
    return "", 204


# ------------------------------------------------------------------
# AI Productivity Planner (Week 3 + Week 4)
# ------------------------------------------------------------------
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(django_client.list_tasks())


@app.route("/api/tasks", methods=["POST"])
def add_task():
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    if not title:
        return jsonify({"error": "Task title is required."}), 400

    use_ai_priority = payload.get("auto_priority", True)
    priority = payload.get("priority", "medium")
    ai_reason = None

    if use_ai_priority:
        suggestion = ai_service.suggest_task_priority(
            title, payload.get("notes", ""), payload.get("due_date")
        )
        priority = suggestion["priority"]
        ai_reason = suggestion["reason"]

    data = {
        "title": title,
        "notes": payload.get("notes", ""),
        "priority": priority,
        "due_date": payload.get("due_date"),
    }
    created = django_client.create_task(data)
    if ai_reason:
        created["ai_priority_reason"] = ai_reason
    return jsonify(created), 201


@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def edit_task(task_id):
    payload = request.get_json(silent=True) or {}
    updated = django_client.update_task(task_id, payload)
    return jsonify(updated)


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def remove_task(task_id):
    django_client.delete_task(task_id)
    return "", 204


@app.route("/api/tasks/plan", methods=["GET"])
def get_daily_plan():
    """AI Productivity Planner: generate a suggested order for today's
    incomplete tasks."""
    raw = django_client.list_tasks() or []
    items = raw.get("results", raw) if isinstance(raw, dict) else raw
    incomplete = [t for t in items if not t.get("is_completed")]

    if not incomplete:
        return jsonify({"plan": "You have no open tasks. Nicely done!"})

    plan = ai_service.generate_daily_plan(incomplete)
    return jsonify({"plan": plan})


if __name__ == "__main__":
    app.run(debug=Config.FLASK_DEBUG, port=Config.FLASK_PORT)
