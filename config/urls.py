from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", lambda _: redirect("authentication:login"), name="home"),
    path("auth/", include("authentication.urls")),
    path("usuarios/", include("users.urls")),
]
