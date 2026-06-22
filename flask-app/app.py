"""
AI Personal Assistant - Flask Application
Week 2-4: Chat gateway, LLM integration, AI features
"""

import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DJANGO_BASE_URL = os.getenv("DJANGO_BASE_URL", "http://127.0.0.1:8000")

# ─── System Prompts ───────────────────────────────────────────────────────────

CHAT_SYSTEM_PROMPT = """You are a helpful AI personal assistant. You help users with:
- General questions and conversations
- Reminders and scheduling
- Note-taking and summarization
- Productivity planning

When a user asks to create a reminder, note, or task, acknowledge it warmly and confirm details.
Keep responses concise, friendly, and actionable."""

SUMMARIZER_SYSTEM_PROMPT = """You are an expert note summarizer. Given raw notes or text:
1. Extract the key points in bullet form
2. Provide a 1-2 sentence TL;DR at the top
3. Highlight any action items with ✅
Keep the summary shorter than the original. Be precise, not verbose."""

PLANNER_SYSTEM_PROMPT = """You are a productivity coach and AI planner. Given a user's goal or task list:
1. Break it into clear, achievable daily/weekly steps
2. Prioritize by impact (High / Medium / Low)
3. Suggest time estimates for each step
4. Add one motivational tip at the end
Format your output clearly with sections."""


# ─── Health Check ─────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "flask-ai-gateway"})


# ─── Frontend (serves the chat UI) ───────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ─── Chat API ─────────────────────────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint. Receives a message, sends to OpenAI, returns reply.
    Also detects intent to create reminders/notes/tasks and forwards to Django.
    """
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_message = data["message"].strip()
    history = data.get("history", [])  # [{"role": "user"/"assistant", "content": "..."}]

    messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
    messages.extend(history[-10:])  # keep last 10 turns for context
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        reply = response.choices[0].message.content.strip()

        # Intent detection: auto-create reminder if user says "remind me"
        side_effect = None
        lower = user_message.lower()
        if "remind me" in lower or "set a reminder" in lower:
            side_effect = _create_reminder_from_message(user_message)
        elif "save note" in lower or "note that" in lower:
            side_effect = _create_note_from_message(user_message)

        return jsonify({
            "reply": reply,
            "side_effect": side_effect
        })

    except Exception as e:
        return jsonify({"error": f"AI service error: {str(e)}"}), 503


# ─── AI Note Summarizer ───────────────────────────────────────────────────────

@app.route("/api/summarize", methods=["POST"])
def summarize():
    """
    Accepts raw note text, returns AI-generated summary.
    Optionally saves summarized note to Django.
    """
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    raw_text = data["text"].strip()
    title = data.get("title", "Untitled Note")
    save_to_django = data.get("save", False)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SUMMARIZER_SYSTEM_PROMPT},
                {"role": "user", "content": f"Summarize this:\n\n{raw_text}"}
            ],
            max_tokens=400,
            temperature=0.5,
        )
        summary = response.choices[0].message.content.strip()

        result = {"summary": summary}

        if save_to_django:
            saved = _save_note_to_django(title, raw_text, summary)
            result["saved"] = saved

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Summarization failed: {str(e)}"}), 503


# ─── AI Productivity Planner ──────────────────────────────────────────────────

@app.route("/api/plan", methods=["POST"])
def plan():
    """
    Accepts a goal or task description, returns an AI-generated productivity plan.
    Optionally saves generated tasks to Django.
    """
    data = request.get_json()
    if not data or "goal" not in data:
        return jsonify({"error": "Missing 'goal' field"}), 400

    goal = data["goal"].strip()
    save_to_django = data.get("save", False)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": f"Help me plan: {goal}"}
            ],
            max_tokens=600,
            temperature=0.7,
        )
        plan_text = response.choices[0].message.content.strip()

        result = {"plan": plan_text, "goal": goal}

        if save_to_django:
            saved = _save_task_to_django(goal, plan_text)
            result["saved"] = saved

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Planning failed: {str(e)}"}), 503


# ─── AI Reminder Assistant ────────────────────────────────────────────────────

@app.route("/api/reminder/ai", methods=["POST"])
def ai_reminder():
    """
    Takes a natural-language reminder request and extracts structured data.
    E.g. "Remind me to call mom tomorrow at 5pm" → {title, due_date, due_time}
    """
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    text = data["text"].strip()

    extraction_prompt = """Extract reminder details from the user's message. 
    Return a JSON object with keys: title (string), due_date (YYYY-MM-DD or null), 
    due_time (HH:MM or null), priority (high/medium/low).
    Respond ONLY with the JSON object, no extra text."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": extraction_prompt},
                {"role": "user", "content": text}
            ],
            max_tokens=150,
            temperature=0.2,
        )
        import json
        extracted = json.loads(response.choices[0].message.content.strip())

        # Save to Django
        saved = _create_reminder_structured(
            title=extracted.get("title", text),
            due_date=extracted.get("due_date"),
            due_time=extracted.get("due_time"),
            priority=extracted.get("priority", "medium"),
        )
        return jsonify({"extracted": extracted, "saved": saved})

    except Exception as e:
        return jsonify({"error": f"Reminder creation failed: {str(e)}"}), 503


# ─── Django Bridge Helpers ────────────────────────────────────────────────────

def _create_reminder_from_message(message: str) -> dict:
    try:
        r = requests.post(
            f"{DJANGO_BASE_URL}/api/reminders/",
            json={"title": message[:200], "priority": "medium"},
            timeout=3,
        )
        return {"type": "reminder", "status": r.status_code}
    except Exception:
        return {"type": "reminder", "status": "django_unavailable"}


def _create_note_from_message(message: str) -> dict:
    try:
        r = requests.post(
            f"{DJANGO_BASE_URL}/api/notes/",
            json={"title": "Quick Note", "content": message},
            timeout=3,
        )
        return {"type": "note", "status": r.status_code}
    except Exception:
        return {"type": "note", "status": "django_unavailable"}


def _save_note_to_django(title: str, content: str, summary: str) -> dict:
    try:
        r = requests.post(
            f"{DJANGO_BASE_URL}/api/notes/",
            json={"title": title, "content": content, "summary": summary},
            timeout=3,
        )
        return {"status": r.status_code, "data": r.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _save_task_to_django(goal: str, plan_text: str) -> dict:
    try:
        r = requests.post(
            f"{DJANGO_BASE_URL}/api/tasks/",
            json={"title": goal[:200], "description": plan_text, "priority": "high"},
            timeout=3,
        )
        return {"status": r.status_code}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _create_reminder_structured(title, due_date, due_time, priority) -> dict:
    payload = {"title": title, "priority": priority}
    if due_date:
        payload["due_date"] = due_date
    if due_time:
        payload["due_time"] = due_time
    try:
        r = requests.post(
            f"{DJANGO_BASE_URL}/api/reminders/",
            json=payload,
            timeout=3,
        )
        return {"status": r.status_code, "data": r.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
