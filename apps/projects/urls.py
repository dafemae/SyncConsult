from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("clientes/", views.clientes_list, name="clientes_list"),
    path("clientes/<int:pk>/", views.cliente_dashboard, name="cliente_dashboard"),
    path("proyectos/<int:pk>/", views.proyecto_detail, name="proyecto_detail"),
]
