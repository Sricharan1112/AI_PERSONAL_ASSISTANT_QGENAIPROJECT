"""
DRF serializers: convert model instances <-> JSON for the API.
"""

from rest_framework import serializers
from .models import Reminder, Note, PlannerTask, ChatMessage


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = [
            "id", "title", "description", "remind_at",
            "is_done", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            "id", "title", "content", "summary",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PlannerTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlannerTask
        fields = [
            "id", "title", "notes", "priority", "due_date",
            "is_completed", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "role", "content", "created_at"]
        read_only_fields = ["id", "created_at"]
