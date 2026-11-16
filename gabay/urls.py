from django.urls import path
from . import views

urlpatterns = [
    path("reviewer/content/symptoms/", views.symptom_list, name="symptom_list"),
    path("reviewer/content/symptoms/new/", views.symptom_create, name="symptom_create"),
    path("reviewer/content/symptoms/<int:pk>/edit/", views.symptom_edit, name="symptom_edit"),
    path("reviewer/content/symptoms/<int:pk>/delete/", views.symptom_delete, name="symptom_delete"),
    path("reviewer/content/illnesses/", views.illness_list, name="illness_list"),
    path("reviewer/content/illnesses/new/", views.illness_create, name="illness_create"),
    path("reviewer/content/illnesses/<int:pk>/edit/", views.illness_edit, name="illness_edit"),
    path("reviewer/content/illnesses/<int:pk>/delete/", views.illness_delete, name="illness_delete"),
    path("reviewer/content/illnesses/<int:pk>/approve/", views.illness_approve, name="illness_approve"),
]
