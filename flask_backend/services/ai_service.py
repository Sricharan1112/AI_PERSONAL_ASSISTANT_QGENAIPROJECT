"""
ai_service.py

Wraps all OpenAI API calls in one place. Every AI feature in the app
(chat, note summarizer, planner prioritization) goes through here.

Centralizing this means:
  - One spot to swap providers later (Anthropic, local LLM, etc.)
  - One spot to handle errors/timeouts/rate limits consistently
  - Easy prompt-engineering iteration (Week 1 & Week 4 goals)
"""

import logging
from openai import OpenAI, APIError, APITimeoutError, RateLimitError, AuthenticationError

from config import Config

logger = logging.getLogger(__name__)

_client = None


def get_client():
    """Lazily create the OpenAI client so import-time failures (e.g.
    missing key) don't crash the whole app on startup."""
    global _client
    if _client is None:
        if not Config.OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Add it to flask_backend/.env"
            )
        _client = OpenAI(api_key=Config.OPENAI_API_KEY)
    return _client


class AIServiceError(Exception):
    """Raised for any AI-call failure, with a user-friendly message
    already attached so routes can return it directly."""

    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _chat_completion(messages, temperature=0.7, max_tokens=600):
    """Single shared call point with consistent error translation."""
    try:
        client = get_client()
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=20,
        )
        return response.choices[0].message.content.strip()

    except AuthenticationError:
        logger.error("OpenAI authentication failed - check OPENAI_API_KEY")
        raise AIServiceError(
            "AI service is misconfigured (invalid API key). "
            "Please contact the administrator.",
            status_code=500,
        )
    except RateLimitError:
        logger.warning("OpenAI rate limit hit")
        raise AIServiceError(
            "The AI assistant is receiving too many requests right now. "
            "Please try again in a moment.",
            status_code=429,
        )
    except APITimeoutError:
        logger.warning("OpenAI request timed out")
        raise AIServiceError(
            "The AI assistant took too long to respond. Please try again.",
            status_code=504,
        )
    except APIError as e:
        logger.error("OpenAI API error: %s", e)
        raise AIServiceError(
            "The AI service encountered an error. Please try again shortly.",
            status_code=502,
        )
    except Exception as e:  # noqa: BLE001 - last-resort safety net
        logger.exception("Unexpected error calling OpenAI")
        raise AIServiceError(
            "Something unexpected went wrong while contacting the AI service.",
            status_code=500,
        )


# ----------------------------------------------------------------------
# Feature 1: Conversational chat (Week 2 + Week 4)
# ----------------------------------------------------------------------
def get_chat_reply(user_message: str, history: list[dict] | None = None) -> str:
    """
    history: list of {"role": "user"|"assistant", "content": "..."}
    representing prior turns, oldest first. Optional.
    """
    system_prompt = {
        "role": "system",
        "content": (
            "You are a helpful, concise personal AI assistant embedded in a "
            "productivity app. You can discuss reminders, notes, and tasks "
            "conceptually, but you do not directly modify data yourself. "
            "Keep replies friendly and to the point."
        ),
    }
    messages = [system_prompt]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    return _chat_completion(messages, temperature=0.7, max_tokens=500)


# ----------------------------------------------------------------------
# Feature 2: AI Note Summarizer (Week 3 + Week 4)
# ----------------------------------------------------------------------
def summarize_note(content: str) -> str:
    if not content or not content.strip():
        raise AIServiceError("Note content is empty - nothing to summarize.", 400)

    messages = [
        {
            "role": "system",
            "content": (
                "You summarize personal notes. Produce a clear summary in "
                "2-4 short bullet points capturing the key information and "
                "any action items. Do not add information that isn't in "
                "the note."
            ),
        },
        {"role": "user", "content": f"Summarize this note:\n\n{content}"},
    ]
    return _chat_completion(messages, temperature=0.3, max_tokens=300)


# ----------------------------------------------------------------------
# Feature 3: AI Productivity Planner (Week 3 + Week 4)
# ----------------------------------------------------------------------
def suggest_task_priority(title: str, notes: str = "", due_date: str | None = None) -> dict:
    """
    Asks the model to suggest a priority level + a one-line rationale
    for a planner task. Returns a small dict the route can merge into
    the task payload sent to Django.
    """
    due_text = f" Due date: {due_date}." if due_date else " No due date given."
    messages = [
        {
            "role": "system",
            "content": (
                "You are a productivity planning assistant. Given a task, "
                "respond with EXACTLY two lines in this format, nothing else:\n"
                "Priority: <low|medium|high>\n"
                "Reason: <one short sentence>"
            ),
        },
        {
            "role": "user",
            "content": f"Task: {title}\nNotes: {notes or '(none)'}.{due_text}",
        },
    ]
    raw = _chat_completion(messages, temperature=0.2, max_tokens=80)

    priority = "medium"
    reason = raw
    for line in raw.splitlines():
        if line.lower().startswith("priority:"):
            value = line.split(":", 1)[1].strip().lower()
            if value in ("low", "medium", "high"):
                priority = value
        if line.lower().startswith("reason:"):
            reason = line.split(":", 1)[1].strip()

    return {"priority": priority, "reason": reason}


def generate_daily_plan(tasks: list[dict]) -> str:
    """
    Given a list of task dicts (title, priority, due_date), ask the AI
    to produce a short, ordered daily plan / suggested schedule.
    """
    if not tasks:
        raise AIServiceError("No tasks provided to plan around.", 400)

    task_lines = "\n".join(
        f"- {t.get('title')} (priority: {t.get('priority', 'medium')}, "
        f"due: {t.get('due_date') or 'none'})"
        for t in tasks
    )
    messages = [
        {
            "role": "system",
            "content": (
                "You are a productivity planner. Given a list of tasks, "
                "propose a sensible order to tackle them today, with a "
                "one-line reason. Keep it under 150 words, formatted as "
                "a short numbered list."
            ),
        },
        {"role": "user", "content": f"My tasks:\n{task_lines}"},
    ]
    return _chat_completion(messages, temperature=0.4, max_tokens=350)
