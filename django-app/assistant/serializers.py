"""
AI Personal Assistant — Django REST Framework Serializers
"""

from rest_framework import serializers
from .models import Reminder, Note, Task


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Reminder
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Note
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Task
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
