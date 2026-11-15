from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),  # kept, but no feature may depend on it
    path("", include("accounts.urls")),
]