"""
django_client.py

Flask never touches the SQLite database directly. Instead, it calls
Django's REST API for all persistence (Reminders, Notes, Tasks, Chat
History). This file centralizes those calls.
"""

import logging
import requests
from requests.exceptions import RequestException, Timeout

from config import Config

logger = logging.getLogger(__name__)

BASE = Config.DJANGO_API_BASE_URL


class DjangoAPIError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _request(method, path, **kwargs):
    url = f"{BASE}{path}"
    try:
        response = requests.request(method, url, timeout=10, **kwargs)
        response.raise_for_status()
        if response.status_code == 204 or not response.content:
            return None
        return response.json()
    except Timeout:
        logger.warning("Django API timed out: %s %s", method, url)
        raise DjangoAPIError("The data service took too long to respond.", 504)
    except RequestException as e:
        logger.error("Django API error: %s %s -> %s", method, url, e)
        raise DjangoAPIError(
            "Could not reach the data service. Is the Django server running?", 502
        )


# ---------------- Reminders ----------------
def list_reminders():
    return _request("GET", "/reminders/")


def create_reminder(data: dict):
    return _request("POST", "/reminders/", json=data)


def update_reminder(reminder_id: int, data: dict):
    return _request("PATCH", f"/reminders/{reminder_id}/", json=data)


def delete_reminder(reminder_id: int):
    return _request("DELETE", f"/reminders/{reminder_id}/")


# ---------------- Notes ----------------
def list_notes():
    return _request("GET", "/notes/")


def create_note(data: dict):
    return _request("POST", "/notes/", json=data)


def update_note(note_id: int, data: dict):
    return _request("PATCH", f"/notes/{note_id}/", json=data)


def delete_note(note_id: int):
    return _request("DELETE", f"/notes/{note_id}/")


# ---------------- Planner Tasks ----------------
def list_tasks():
    return _request("GET", "/tasks/")


def create_task(data: dict):
    return _request("POST", "/tasks/", json=data)


def update_task(task_id: int, data: dict):
    return _request("PATCH", f"/tasks/{task_id}/", json=data)


def delete_task(task_id: int):
    return _request("DELETE", f"/tasks/{task_id}/")


# ---------------- Chat History ----------------
def list_chat_history():
    return _request("GET", "/chat-history/")


def save_chat_message(role: str, content: str):
    return _request("POST", "/chat-history/", json={"role": role, "content": content})
