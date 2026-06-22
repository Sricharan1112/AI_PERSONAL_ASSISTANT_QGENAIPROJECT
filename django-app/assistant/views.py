"""
AI Personal Assistant — Django Views
Week 3: Full CRUD viewsets for Reminder, Note, Task
Extra: /complete action, filtering, stats endpoint
"""

from django.db.models import Count, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Reminder, Note, Task
from .serializers import ReminderSerializer, NoteSerializer, TaskSerializer


class ReminderViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for reminders.
    GET    /api/reminders/          → list all
    POST   /api/reminders/          → create
    GET    /api/reminders/<id>/     → retrieve
    PUT    /api/reminders/<id>/     → full update
    PATCH  /api/reminders/<id>/     → partial update (e.g. toggle completed)
    DELETE /api/reminders/<id>/     → delete
    POST   /api/reminders/<id>/complete/ → mark complete
    GET    /api/reminders/pending/  → only incomplete
    """
    serializer_class = ReminderSerializer

    def get_queryset(self):
        qs = Reminder.objects.all()
        # ?priority=high  filtering
        priority = self.request.query_params.get("priority")
        if priority:
            qs = qs.filter(priority=priority)
        completed = self.request.query_params.get("completed")
        if completed is not None:
            qs = qs.filter(completed=completed.lower() == "true")
        return qs

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """POST /api/reminders/<id>/complete/ — marks a reminder as done."""
        reminder = self.get_object()
        reminder.completed = True
        reminder.save()
        return Response(ReminderSerializer(reminder).data)

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """GET /api/reminders/pending/ — returns all incomplete reminders."""
        qs = Reminder.objects.filter(completed=False)
        return Response(ReminderSerializer(qs, many=True).data)


class NoteViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for notes.
    GET  /api/notes/?search=keyword  → search by title or content
    """
    serializer_class = NoteSerializer

    def get_queryset(self):
        qs = Note.objects.all()
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        return qs


class TaskViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for tasks (AI-generated productivity plans).
    POST /api/tasks/<id>/complete/ → mark done
    """
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = Task.objects.all()
        priority = self.request.query_params.get("priority")
        if priority:
            qs = qs.filter(priority=priority)
        completed = self.request.query_params.get("completed")
        if completed is not None:
            qs = qs.filter(completed=completed.lower() == "true")
        return qs

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.completed = True
        task.save()
        return Response(TaskSerializer(task).data)


@api_view(["GET"])
def dashboard_stats(request):
    """
    GET /api/stats/
    Returns aggregated counts for the dashboard overview.
    """
    stats = {
        "reminders": {
            "total": Reminder.objects.count(),
            "pending": Reminder.objects.filter(completed=False).count(),
            "high_priority": Reminder.objects.filter(priority="high", completed=False).count(),
        },
        "notes": {
            "total": Note.objects.count(),
            "with_summary": Note.objects.exclude(summary="").count(),
        },
        "tasks": {
            "total": Task.objects.count(),
            "completed": Task.objects.filter(completed=True).count(),
            "pending": Task.objects.filter(completed=False).count(),
        },
    }
    return Response(stats)
