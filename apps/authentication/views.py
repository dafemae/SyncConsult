from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("users:dashboard")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, f"¡Bienvenido, {form.get_user().get_display_name()}!")
        return redirect("users:dashboard")

    return render(request, "authentication/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("users:dashboard")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "¡Cuenta creada exitosamente! Bienvenido al sistema.")
        return redirect("users:dashboard")

    return render(request, "authentication/register.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("authentication:login")
