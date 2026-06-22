"""
Root URL configuration for the Django backend.

Routes:
  /admin/        -> Django admin panel (manage data visually)
  /api/          -> All REST API endpoints (see assistant/urls.py)
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("assistant.urls")),
]
