"""
Modelos del sistema de Gestión de Actividades Escolares.
I.E. 1122 María Auxiliadora - Puno
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Usuario del sistema con roles director/docente."""
    ROLE_CHOICES = [
        ('director', 'Director'),
        ('docente', 'Docente'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='docente', verbose_name='Rol')
    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    telefono = models.CharField(max_length=15, blank=True, verbose_name='Teléfono')
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de nacimiento')
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True, verbose_name='Foto de perfil')
    seccion_asignada = models.CharField(max_length=50, blank=True, verbose_name='Sección / Grado asignado', help_text='Ej: 3B, 5A, ED.FISICA')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_director(self):
        return self.role == 'director'

    @property
    def is_docente(self):
        return self.role == 'docente'


class Seccion(models.Model):
    """Sección o grado escolar."""
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    nivel = models.CharField(max_length=50, blank=True, verbose_name='Nivel')
    turno = models.CharField(
        max_length=20,
        choices=[('mañana', 'Mañana'), ('tarde', 'Tarde'), ('noche', 'Noche')],
        default='mañana',
        verbose_name='Turno'
    )

    class Meta:
        verbose_name = 'Sección'
        verbose_name_plural = 'Secciones'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Destino(models.Model):
    """Destino para excursiones."""
    nombre = models.CharField(max_length=200, verbose_name='Nombre del lugar')
    ubicacion = models.CharField(max_length=300, verbose_name='Ubicación/Dirección')
    distancia_km = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Distancia (km)'
    )
    docente_referencia = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='destinos_referencia', verbose_name='Docente de referencia'
    )

    class Meta:
        verbose_name = 'Destino'
        verbose_name_plural = 'Destinos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class ActividadInstitucional(models.Model):
    """Actividad institucional creada por el director."""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]

    titulo = models.CharField(max_length=300, verbose_name='Título')
    descripcion = models.TextField(verbose_name='Descripción')
    fecha = models.DateField(verbose_name='Fecha de actividad')
    responsables = models.ManyToManyField(
        User,
        related_name='actividades_asignadas',
        verbose_name='Responsables',
        limit_choices_to={'role': 'docente'}
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='actividades_creadas',
        verbose_name='Creado por'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    lugar = models.CharField(max_length=200, blank=True, verbose_name='Lugar')
    presupuesto = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Presupuesto (S/)'
    )
    imagen = models.ImageField(upload_to='actividades/', null=True, blank=True, verbose_name='Imagen principal')


    class Meta:
        verbose_name = 'Actividad Institucional'
        verbose_name_plural = 'Actividades Institucionales'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.titulo} ({self.fecha})"

    def get_estado_badge(self):
        badges = {
            'pendiente': 'warning',
            'en_proceso': 'primary',
            'finalizada': 'success',
            'cancelada': 'danger',
        }
        return badges.get(self.estado, 'secondary')


class PropuestaActividad(models.Model):
    """Propuesta de actividad hecha por un docente."""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    titulo = models.CharField(max_length=300, verbose_name='Título de la propuesta')
    descripcion = models.TextField(verbose_name='Descripción')
    propuesta_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='propuestas',
        verbose_name='Propuesto por'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado'
    )
    observacion_admin = models.TextField(
        blank=True,
        verbose_name='Observación del director',
        help_text='Comentario del director al aprobar o rechazar'
    )
    fecha_propuesta = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)
    fecha_actividad_propuesta = models.DateField(null=True, blank=True, verbose_name='Fecha propuesta para la actividad')
    revisado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='propuestas_revisadas',
        verbose_name='Revisado por'
    )

    class Meta:
        verbose_name = 'Propuesta de Actividad'
        verbose_name_plural = 'Propuestas de Actividades'
        ordering = ['-fecha_propuesta']

    def __str__(self):
        return f"{self.titulo} - {self.propuesta_por.get_full_name()}"

    def get_estado_badge(self):
        badges = {
            'pendiente': 'warning',
            'aprobada': 'success',
            'rechazada': 'danger',
        }
        return badges.get(self.estado, 'secondary')


class Excursion(models.Model):
    """Excursión organizada por un docente para una sección."""
    # Campos de texto libre (el docente escribe directamente)
    seccion_nombre = models.CharField(max_length=100, blank=True, verbose_name='Sección', help_text='Ej: 3°A, 5°B')
    grado = models.CharField(max_length=100, blank=True, verbose_name='Grado', help_text='Ej: 3er Grado, 5to Primaria')
    grado_seccion = models.CharField(max_length=200, blank=True, verbose_name='Grado y Sección', help_text='Ej: 3er Grado "A", 5to Primaria "B"')
    destino_nombre = models.CharField(max_length=200, blank=True, verbose_name='Destino', help_text='Ej: Parque, Museo, Lago Titicaca')

    # FKs opcionales (compatibilidad con datos anteriores)
    seccion = models.ForeignKey(
        Seccion,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Sección (referencia)',
        related_name='excursiones'
    )
    destino = models.ForeignKey(
        Destino,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Destino (referencia)',
        related_name='excursiones'
    )

    fecha = models.DateField(verbose_name='Fecha de excursión')
    responsable = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='excursiones_responsable',
        verbose_name='Docente responsable'
    )
    aula = models.CharField(max_length=50, blank=True, verbose_name='Aula', help_text='Ej: 3°A, Aula 5, Primaria 2')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    num_estudiantes = models.IntegerField(default=0, verbose_name='N° de estudiantes')
    estado = models.CharField(
        max_length=20,
        choices=[('programada', 'Programada'), ('realizada', 'Realizada'), ('cancelada', 'Cancelada')],
        default='programada',
        verbose_name='Estado'
    )
    imagen = models.ImageField(upload_to='excursiones/', null=True, blank=True, verbose_name='Imagen principal')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Excursión'
        verbose_name_plural = 'Excursiones'
        ordering = ['-fecha']

    def get_seccion_display_name(self):
        return self.seccion_nombre or (self.seccion.nombre if self.seccion else '—')

    def get_destino_display_name(self):
        return self.destino_nombre or (self.destino.nombre if self.destino else '—')

    def __str__(self):
        destino = self.get_destino_display_name()
        seccion = self.get_seccion_display_name()
        return f"Excursión a {destino} - {seccion} ({self.fecha})"


class Evidencia(models.Model):
    """Evidencia fotográfica de actividades o excursiones."""
    actividad = models.ForeignKey(
        ActividadInstitucional,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='evidencias',
        verbose_name='Actividad'
    )
    excursion = models.ForeignKey(
        Excursion,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='evidencias',
        verbose_name='Excursión'
    )
    subido_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='evidencias_subidas',
        verbose_name='Subido por'
    )
    imagen = models.ImageField(
        upload_to='evidencias/%Y/%m/',
        verbose_name='Imagen'
    )
    descripcion = models.CharField(max_length=500, blank=True, verbose_name='Descripción')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Evidencia'
        verbose_name_plural = 'Evidencias'
        ordering = ['-fecha_subida']

    def __str__(self):
        evento = self.actividad or self.excursion
        return f"Evidencia de {evento} - {self.subido_por.username}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.actividad and not self.excursion:
            raise ValidationError('Debe seleccionar una actividad o excursión.')
        if self.actividad and self.excursion:
            raise ValidationError('No puede seleccionar ambos: actividad y excursión.')


class Aviso(models.Model):
    """Aviso/comunicado del director."""
    titulo = models.CharField(max_length=300, verbose_name='Título')
    mensaje = models.TextField(verbose_name='Mensaje')
    creado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='avisos_creados',
        verbose_name='Creado por'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    destinatarios = models.ManyToManyField(
        User,
        related_name='avisos_recibidos',
        blank=True,
        verbose_name='Destinatarios específicos',
        help_text='Si está vacío, el aviso es para todos.'
    )
    es_urgente = models.BooleanField(default=False, verbose_name='¿Es urgente?')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Aviso'
        verbose_name_plural = 'Avisos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.titulo


class Mensaje(models.Model):
    """Sistema de mensajería interna entre usuarios."""
    de_usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mensajes_enviados',
        verbose_name='De'
    )
    para_usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mensajes_recibidos',
        verbose_name='Para'
    )
    asunto = models.CharField(max_length=300, verbose_name='Asunto')
    mensaje = models.TextField(verbose_name='Mensaje')
    leido = models.BooleanField(default=False, verbose_name='Leído')
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"De {self.de_usuario} para {self.para_usuario}: {self.asunto}"

    def marcar_leido(self):
        if not self.leido:
            self.leido = True
            self.fecha_lectura = timezone.now()
            self.save()
