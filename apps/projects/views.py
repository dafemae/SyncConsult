from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from .models import Cliente, Notification, Proyecto, Requerimiento, Task


@login_required
def clientes_list(request):
    clientes = Cliente.objects.annotate(
        total_proyectos=Count("proyectos", distinct=True),
        proyectos_activos=Count("proyectos", filter=Q(proyectos__estado="activo"), distinct=True),
    ).order_by("nombre")

    context = {
        "clientes": clientes,
        "stats": {
            "total_clientes": clientes.count(),
            "total_proyectos": Proyecto.objects.count(),
            "proyectos_activos": Proyecto.objects.filter(estado="activo").count(),
            "total_tareas": Task.objects.count(),
        },
    }
    return render(request, "projects/clientes_list.html", context)


@login_required
def cliente_dashboard(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    proyectos = cliente.proyectos.prefetch_related(
        "miembros__usuario", "sprints", "requerimientos", "tareas", "entornos"
    ).all()

    tareas_qs = Task.objects.filter(proyecto__cliente=cliente)
    reqs_qs = Requerimiento.objects.filter(proyecto__cliente=cliente)

    stats = {
        "total_proyectos": proyectos.count(),
        "proyectos_activos": proyectos.filter(estado="activo").count(),
        "proyectos_completados": proyectos.filter(estado="completado").count(),
        "total_tareas": tareas_qs.count(),
        "tareas_pendientes": tareas_qs.filter(estado="pendiente").count(),
        "tareas_en_progreso": tareas_qs.filter(estado="en_progreso").count(),
        "tareas_completadas": tareas_qs.filter(estado="completada").count(),
        "total_requerimientos": reqs_qs.count(),
        "reqs_aprobados": reqs_qs.filter(estado="aprobado").count(),
        "reqs_pendientes": reqs_qs.filter(estado="nuevo").count(),
    }

    # Enriquecer cada proyecto con su progreso
    proyectos_con_stats = []
    for p in proyectos:
        t_total = p.tareas.count()
        t_completas = p.tareas.filter(estado="completada").count()
        progreso = round((t_completas / t_total) * 100) if t_total else 0
        proyectos_con_stats.append({
            "proyecto": p,
            "progreso": progreso,
            "total_tareas": t_total,
            "tareas_completadas": t_completas,
            "sprint_activo": p.sprints.filter(activo=True).first(),
            "total_reqs": p.requerimientos.count(),
        })

    notificaciones = Notification.objects.filter(usuario=request.user, leida=False)[:5]

    context = {
        "cliente": cliente,
        "proyectos_con_stats": proyectos_con_stats,
        "stats": stats,
        "notificaciones": notificaciones,
    }
    return render(request, "projects/cliente_dashboard.html", context)


@login_required
def proyecto_detail(request, pk):
    proyecto = get_object_or_404(
        Proyecto.objects.prefetch_related(
            "miembros__usuario", "sprints", "requerimientos",
            "tareas", "backlog_items", "columnas_kanban", "entornos", "versiones",
        ),
        pk=pk,
    )

    sprint_activo = proyecto.sprints.filter(activo=True).first()
    tareas = proyecto.tareas.select_related("usuario", "sprint", "columna")
    requerimientos = proyecto.requerimientos.select_related("creado_por").order_by("-created_at")

    t_total = tareas.count()
    t_completas = tareas.filter(estado="completada").count()
    progreso = round((t_completas / t_total) * 100) if t_total else 0

    context = {
        "proyecto": proyecto,
        "sprint_activo": sprint_activo,
        "tareas": tareas,
        "requerimientos": requerimientos,
        "progreso": progreso,
        "tareas_por_estado": {
            "pendiente": tareas.filter(estado="pendiente").count(),
            "en_progreso": tareas.filter(estado="en_progreso").count(),
            "revision": tareas.filter(estado="revision").count(),
            "completada": tareas.filter(estado="completada").count(),
        },
    }
    return render(request, "projects/proyecto_detail.html", context)
