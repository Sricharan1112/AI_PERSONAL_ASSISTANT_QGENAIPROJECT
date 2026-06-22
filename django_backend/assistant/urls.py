"""
API URL routing using DRF's router, which auto-generates the
standard REST endpoints for each ViewSet.

Resulting endpoints (all under /api/):
  /api/reminders/            GET, POST
  /api/reminders/<id>/       GET, PUT, PATCH, DELETE
  /api/notes/                GET, POST
  /api/notes/<id>/           GET, PUT, PATCH, DELETE
  /api/tasks/                GET, POST
  /api/tasks/<id>/           GET, PUT, PATCH, DELETE
  /api/chat-history/         GET, POST
  /api/chat-history/<id>/    GET, PUT, PATCH, DELETE
"""

from rest_framework.routers import DefaultRouter
from .views import (
    ReminderViewSet,
    NoteViewSet,
    PlannerTaskViewSet,
    ChatMessageViewSet,
)

router = DefaultRouter()
router.register(r"reminders", ReminderViewSet, basename="reminder")
router.register(r"notes", NoteViewSet, basename="note")
router.register(r"tasks", PlannerTaskViewSet, basename="plannertask")
router.register(r"chat-history", ChatMessageViewSet, basename="chatmessage")

urlpatterns = router.urls
