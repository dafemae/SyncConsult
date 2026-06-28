from django.contrib import admin
from .models import (
    Backlog, Cliente, ClienteUsuario, Environment, EnvironmentRequest,
    KanbanColumn, Notification, Proyecto, ProyectoMiembro, Requerimiento,
    RequerimientoArchivo, Sprint, Task, TaskAttachment, TaskComment,
    TaskHistory, Version,
)


class ClienteUsuarioInline(admin.TabularInline):
    model = ClienteUsuario
    extra = 1


class ProyectoInline(admin.TabularInline):
    model = Proyecto
    extra = 0
    fields = ["nombre", "estado", "fecha_inicio", "fecha_fin"]
    show_change_link = True


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["nombre", "rut", "telefono", "created_at"]
    search_fields = ["nombre", "rut"]
    inlines = [ClienteUsuarioInline, ProyectoInline]


class ProyectoMiembroInline(admin.TabularInline):
    model = ProyectoMiembro
    extra = 1


class SprintInline(admin.TabularInline):
    model = Sprint
    extra = 0
    fields = ["nombre", "fecha_inicio", "fecha_fin", "activo"]


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "cliente", "estado", "fecha_inicio", "fecha_fin", "created_at"]
    list_filter = ["estado", "cliente"]
    search_fields = ["nombre", "cliente__nombre"]
    inlines = [ProyectoMiembroInline, SprintInline]


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ["nombre", "proyecto", "fecha_inicio", "fecha_fin", "activo"]
    list_filter = ["activo", "proyecto"]


@admin.register(KanbanColumn)
class KanbanColumnAdmin(admin.ModelAdmin):
    list_display = ["nombre", "proyecto", "orden", "color"]
    list_filter = ["proyecto"]


@admin.register(Backlog)
class BacklogAdmin(admin.ModelAdmin):
    list_display = ["titulo", "proyecto", "sprint", "prioridad", "orden"]
    list_filter = ["prioridad", "proyecto"]


class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 0


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["titulo", "proyecto", "sprint", "usuario", "estado", "prioridad", "orden"]
    list_filter = ["estado", "prioridad", "sprint__proyecto"]
    search_fields = ["titulo"]
    inlines = [TaskAttachmentInline, TaskCommentInline]


@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ["tarea", "usuario", "campo", "created_at"]
    readonly_fields = ["tarea", "usuario", "campo", "valor_anterior", "valor_nuevo", "created_at"]


class RequerimientoArchivoInline(admin.TabularInline):
    model = RequerimientoArchivo
    extra = 0


@admin.register(Requerimiento)
class RequerimientoAdmin(admin.ModelAdmin):
    list_display = ["titulo", "proyecto", "creado_por", "prioridad", "estado", "created_at"]
    list_filter = ["estado", "prioridad", "proyecto"]
    search_fields = ["titulo"]
    inlines = [RequerimientoArchivoInline]


class EnvironmentRequestInline(admin.TabularInline):
    model = EnvironmentRequest
    extra = 0


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ["proyecto", "version", "url", "estado", "fecha_despliegue"]
    list_filter = ["estado", "proyecto"]
    inlines = [EnvironmentRequestInline]


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ["proyecto", "numero", "fecha_lanzamiento", "activa"]
    list_filter = ["activa", "proyecto"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["titulo", "usuario", "tipo", "leida", "created_at"]
    list_filter = ["tipo", "leida"]
    search_fields = ["titulo", "usuario__email"]
