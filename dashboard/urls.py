from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard_redirect, name="dashboard"),
    path("citizen/dashboard/", views.citizen_dashboard, name="citizen_dashboard"),
    path("reviewer/dashboard/", views.reviewer_dashboard, name="reviewer_dashboard"),
]