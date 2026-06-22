"""
ViewSets: each gives a full set of CRUD endpoints automatically
(list, create, retrieve, update, partial_update, destroy) when
wired up to a DRF router in urls.py.
"""

from rest_framework import viewsets, filters

from .models import Reminder, Note, PlannerTask, ChatMessage
from .serializers import (
    ReminderSerializer,
    NoteSerializer,
    PlannerTaskSerializer,
    ChatMessageSerializer,
)


class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["remind_at", "created_at"]


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "updated_at"]


class PlannerTaskViewSet(viewsets.ModelViewSet):
    queryset = PlannerTask.objects.all()
    serializer_class = PlannerTaskSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["due_date", "priority", "created_at"]


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    Mostly used as: Flask POSTs each user message and each AI reply here
    so conversation history is persisted. GET lets the frontend reload
    history on page refresh.
    """
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
