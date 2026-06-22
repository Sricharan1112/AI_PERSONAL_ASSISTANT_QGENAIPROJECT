from django.contrib import admin
from .models import Reminder, Note, Task


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display  = ("title", "priority", "due_date", "due_time", "completed", "created_at")
    list_filter   = ("priority", "completed")
    search_fields = ("title", "description")
    ordering      = ("-created_at",)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display  = ("title", "created_at", "updated_at")
    search_fields = ("title", "content", "tags")
    ordering      = ("-created_at",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display  = ("title", "priority", "completed", "due_date", "created_at")
    list_filter   = ("priority", "completed")
    search_fields = ("title", "description")
    ordering      = ("-created_at",)
