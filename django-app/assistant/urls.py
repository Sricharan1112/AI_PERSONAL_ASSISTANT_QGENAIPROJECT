"""
AI Personal Assistant — Django URL Routing
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReminderViewSet, NoteViewSet, TaskViewSet, dashboard_stats

router = DefaultRouter()
router.register(r"reminders", ReminderViewSet, basename="reminder")
router.register(r"notes",     NoteViewSet,     basename="note")
router.register(r"tasks",     TaskViewSet,     basename="task")

urlpatterns = [
    path("", include(router.urls)),
    path("stats/", dashboard_stats, name="dashboard-stats"),
]
