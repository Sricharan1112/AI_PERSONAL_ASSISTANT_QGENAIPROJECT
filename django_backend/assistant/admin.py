"""
Registering models with Django admin gives a free, working UI at
/admin/ to view and edit Reminders, Notes, Tasks, and Chat History
without writing any extra code. Useful for debugging during dev.
"""

from django.contrib import admin
from .models import Reminder, Note, PlannerTask, ChatMessage


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ("title", "remind_at", "is_done", "created_at")
    list_filter = ("is_done",)
    search_fields = ("title", "description")


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "updated_at")
    search_fields = ("title", "content", "summary")


@admin.register(PlannerTask)
class PlannerTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "priority", "due_date", "is_completed")
    list_filter = ("priority", "is_completed")
    search_fields = ("title", "notes")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("role", "content", "created_at")
    list_filter = ("role",)
