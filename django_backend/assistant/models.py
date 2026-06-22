"""
Models for the AI Personal Assistant.

These map directly to the three "AI feature modules" in the roadmap:
  - Reminder        -> AI Reminder Assistant
  - Note            -> AI Note Summarizer
  - PlannerTask     -> AI Productivity Planner

Django owns the schema and persistence. The Flask service never writes
to this database directly -- it calls the REST API defined in views.py
and exposed via urls.py.
"""

from django.db import models


class Reminder(models.Model):
    """A single reminder, optionally created/parsed with AI help."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    remind_at = models.DateTimeField(null=True, blank=True)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["remind_at", "-created_at"]

    def __str__(self):
        return self.title


class Note(models.Model):
    """A note. `summary` is filled in by the AI Note Summarizer feature."""

    title = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    summary = models.TextField(blank=True)  # AI-generated summary lives here
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"Note #{self.pk}"


class PlannerTask(models.Model):
    """A productivity/planner task, optionally prioritized by AI."""

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    due_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["is_completed", "due_date", "-priority"]

    def __str__(self):
        return self.title


class ChatMessage(models.Model):
    """
    Optional: persisted chat history, so the conversational assistant
    has memory across sessions. Flask writes here after every exchange.
    """

    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"
