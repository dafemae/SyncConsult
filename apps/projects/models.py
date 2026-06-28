from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

PRIORIDAD_CHOICES = [
    ("baja", "Baja"),
    ("media", "Media"),
    ("alta", "Alta"),
    ("critica", "Crítica"),
]


class Cliente(models.Model):
    nombre = models.CharField(max_length=150)
    rut = models.CharField(max_length=20, unique=True, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    usuarios = models.ManyToManyField(
        User, through="ClienteUsuario", related_name="clientes", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def proyectos_activos_count(self):
        return self.proyectos.filter(estado="activo").count()


class ClienteUsuario(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="asignaciones")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="clientes_asignados")

    class Meta:
        unique_together = ["cliente", "usuario"]
        verbose_name = "Asignación Cliente-Usuario"
        verbose_name_plural = "Asignaciones Cliente-Usuario"

    def __str__(self):
        return f"{self.cliente} – {self.usuario}"


class Proyecto(models.Model):
    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("pausado", "Pausado"),
        ("completado", "Completado"),
        ("cancelado", "Cancelado"),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="proyectos")
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default="activo")
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nombre} ({self.cliente})"

    def progreso_tareas(self):
        total = self.tareas.count()
        if total == 0:
            return 0
        completadas = self.tareas.filter(estado="completada").count()
        return round((completadas / total) * 100)


class ProyectoMiembro(models.Model):
    ROL_CHOICES = [
        ("lider", "Líder de proyecto"),
        ("desarrollador", "Desarrollador"),
        ("tester", "Tester"),
        ("analista", "Analista"),
        ("observador", "Observador"),
    ]
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="miembros")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="proyectos_como_miembro")
    rol = models.CharField(max_length=50, choices=ROL_CHOICES, default="desarrollador")

    class Meta:
        unique_together = ["proyecto", "usuario"]
        verbose_name = "Miembro del Proyecto"
        verbose_name_plural = "Miembros del Proyecto"

    def __str__(self):
        return f"{self.usuario} – {self.get_rol_display()} en {self.proyecto}"


class Sprint(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="sprints")
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Sprint"
        verbose_name_plural = "Sprints"
        ordering = ["fecha_inicio"]

    def __str__(self):
        return f"{self.nombre} – {self.proyecto}"


class KanbanColumn(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="columnas_kanban")
    nombre = models.CharField(max_length=100)
    orden = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=7, default="#0d6efd")

    class Meta:
        verbose_name = "Columna Kanban"
        verbose_name_plural = "Columnas Kanban"
        ordering = ["orden"]

    def __str__(self):
        return f"{self.nombre} ({self.proyecto})"


class Backlog(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="backlog_items")
    sprint = models.ForeignKey(
        Sprint, null=True, blank=True, on_delete=models.SET_NULL, related_name="backlog_items"
    )
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    prioridad = models.CharField(max_length=30, choices=PRIORIDAD_CHOICES, default="media")
    orden = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Backlog"
        verbose_name_plural = "Backlog Items"
        ordering = ["orden", "-created_at"]

    def __str__(self):
        return self.titulo


class Task(models.Model):
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("en_progreso", "En progreso"),
        ("revision", "En revisión"),
        ("completada", "Completada"),
        ("cancelada", "Cancelada"),
    ]
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name="tareas", null=True, blank=True
    )
    sprint = models.ForeignKey(
        Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name="tareas"
    )
    columna = models.ForeignKey(
        KanbanColumn, on_delete=models.SET_NULL, null=True, blank=True, related_name="tareas"
    )
    usuario = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tareas_asignadas"
    )
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default="pendiente")
    prioridad = models.CharField(max_length=30, choices=PRIORIDAD_CHOICES, default="media")
    orden = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"
        ordering = ["orden", "-created_at"]

    def __str__(self):
        return self.titulo


class TaskAttachment(models.Model):
    tarea = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="archivos")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="archivos_tarea")
    nombre_archivo = models.CharField(max_length=255)
    archivo = models.FileField(upload_to="tareas/archivos/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Archivo de Tarea"
        verbose_name_plural = "Archivos de Tarea"

    def __str__(self):
        return self.nombre_archivo


class TaskComment(models.Model):
    tarea = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comentarios")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="comentarios_tarea")
    contenido = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Comentario de Tarea"
        verbose_name_plural = "Comentarios de Tarea"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comentario de {self.usuario} en {self.tarea}"


class TaskHistory(models.Model):
    tarea = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="historial")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="historial_tareas")
    campo = models.CharField(max_length=100)
    valor_anterior = models.TextField(blank=True)
    valor_nuevo = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historial de Tarea"
        verbose_name_plural = "Historial de Tareas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Cambio en '{self.campo}' de {self.tarea}"


class Requerimiento(models.Model):
    ESTADO_CHOICES = [
        ("nuevo", "Nuevo"),
        ("analisis", "En análisis"),
        ("aprobado", "Aprobado"),
        ("rechazado", "Rechazado"),
        ("implementado", "Implementado"),
    ]
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="requerimientos")
    creado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="requerimientos_creados"
    )
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    prioridad = models.CharField(max_length=30, choices=PRIORIDAD_CHOICES, default="media")
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default="nuevo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Requerimiento"
        verbose_name_plural = "Requerimientos"
        ordering = ["-created_at"]

    def __str__(self):
        return self.titulo


class RequerimientoArchivo(models.Model):
    requerimiento = models.ForeignKey(Requerimiento, on_delete=models.CASCADE, related_name="archivos")
    usuario = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="archivos_requerimiento"
    )
    nombre_archivo = models.CharField(max_length=255)
    archivo = models.FileField(upload_to="requerimientos/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Archivo de Requerimiento"
        verbose_name_plural = "Archivos de Requerimiento"

    def __str__(self):
        return self.nombre_archivo


class Environment(models.Model):
    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
        ("mantenimiento", "En mantenimiento"),
    ]
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="entornos")
    version = models.CharField(max_length=50)
    url = models.URLField(blank=True)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default="activo")
    fecha_despliegue = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Entorno"
        verbose_name_plural = "Entornos"

    def __str__(self):
        return f"{self.proyecto} v{self.version}"


class EnvironmentRequest(models.Model):
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("aprobado", "Aprobado"),
        ("rechazado", "Rechazado"),
        ("desplegado", "Desplegado"),
    ]
    entorno = models.ForeignKey(Environment, on_delete=models.CASCADE, related_name="solicitudes")
    usuario = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="solicitudes_entorno"
    )
    descripcion = models.TextField()
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default="pendiente")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Solicitud de Entorno"
        verbose_name_plural = "Solicitudes de Entorno"

    def __str__(self):
        return f"Solicitud para {self.entorno} ({self.get_estado_display()})"


class Version(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="versiones")
    numero = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    fecha_lanzamiento = models.DateField(null=True, blank=True)
    activa = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Versión"
        verbose_name_plural = "Versiones"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.proyecto} v{self.numero}"


class Notification(models.Model):
    TIPO_CHOICES = [
        ("info", "Información"),
        ("exito", "Éxito"),
        ("advertencia", "Advertencia"),
        ("error", "Error"),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificaciones")
    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="info")
    leida = models.BooleanField(default=False)
    url = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.titulo} → {self.usuario}"
