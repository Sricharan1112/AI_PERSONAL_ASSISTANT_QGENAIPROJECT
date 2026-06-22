"""
AI Personal Assistant — Django Models
Week 3: Reminder, Note, Task with full field sets
"""

from django.db import models


class Reminder(models.Model):
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    due_date    = models.DateField(null=True, blank=True)
    due_time    = models.TimeField(null=True, blank=True)
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    completed   = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.priority.upper()}] {self.title}"


class Note(models.Model):
    title      = models.CharField(max_length=255)
    content    = models.TextField()
    summary    = models.TextField(blank=True, default="")  # AI-generated summary
    tags       = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Task(models.Model):
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")  # AI-generated plan
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    completed   = models.BooleanField(default=False)
    due_date    = models.DateField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
