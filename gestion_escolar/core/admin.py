"""
Admin configuration for the school management system.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User, Seccion, Destino, ActividadInstitucional,
    PropuestaActividad, Excursion, Evidencia, Aviso, Mensaje
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'get_full_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('role', 'telefono', 'foto_perfil')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('email', 'first_name', 'last_name', 'role', 'telefono')
        }),
    )


@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel', 'turno')
    list_filter = ('turno', 'nivel')
    search_fields = ('nombre',)


@admin.register(Destino)
class DestinoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ubicacion', 'distancia_km')
    search_fields = ('nombre', 'ubicacion')


@admin.register(ActividadInstitucional)
class ActividadInstitucionalAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha', 'estado', 'created_by')
    list_filter = ('estado', 'fecha')
    search_fields = ('titulo', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    date_hierarchy = 'fecha'


@admin.register(PropuestaActividad)
class PropuestaActividadAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'propuesta_por', 'estado', 'fecha_propuesta', 'revisado_por')
    list_filter = ('estado', 'fecha_propuesta')
    search_fields = ('titulo', 'descripcion')
    readonly_fields = ('fecha_propuesta', 'fecha_revision')
    actions = ['aprobar_propuestas', 'rechazar_propuestas']

    def aprobar_propuestas(self, request, queryset):
        updated = queryset.filter(estado='pendiente').update(estado='aprobada')
        self.message_user(request, f'{updated} propuesta(s) aprobada(s).')
    aprobar_propuestas.short_description = 'Aprobar propuestas seleccionadas'

    def rechazar_propuestas(self, request, queryset):
        updated = queryset.filter(estado='pendiente').update(estado='rechazada')
        self.message_user(request, f'{updated} propuesta(s) rechazada(s).')
    rechazar_propuestas.short_description = 'Rechazar propuestas seleccionadas'


@admin.register(Excursion)
class ExcursionAdmin(admin.ModelAdmin):
    list_display = ('get_titulo', 'seccion', 'destino', 'fecha', 'responsable', 'estado')
    list_filter = ('estado', 'seccion', 'fecha')
    search_fields = ('destino__nombre', 'seccion__nombre', 'responsable__username')
    date_hierarchy = 'fecha'

    def get_titulo(self, obj):
        return str(obj)
    get_titulo.short_description = 'Excursión'


class EvidenciaInline(admin.TabularInline):
    model = Evidencia
    extra = 1
    fields = ('imagen', 'descripcion', 'subido_por')
    readonly_fields = ('fecha_subida',)


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ('get_titulo', 'subido_por', 'fecha_subida', 'get_imagen_preview')
    list_filter = ('fecha_subida',)
    search_fields = ('descripcion', 'subido_por__username')
    readonly_fields = ('fecha_subida', 'get_imagen_preview')

    def get_titulo(self, obj):
        return str(obj)
    get_titulo.short_description = 'Evidencia'

    def get_imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-height:80px;"/>', obj.imagen.url)
        return '(sin imagen)'
    get_imagen_preview.short_description = 'Vista previa'


@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'creado_por', 'fecha_creacion', 'es_urgente', 'activo')
    list_filter = ('es_urgente', 'activo', 'fecha_creacion')
    search_fields = ('titulo', 'mensaje')
    filter_horizontal = ('destinatarios',)
    readonly_fields = ('fecha_creacion',)


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('asunto', 'de_usuario', 'para_usuario', 'leido', 'fecha_envio')
    list_filter = ('leido', 'fecha_envio')
    search_fields = ('asunto', 'mensaje', 'de_usuario__username', 'para_usuario__username')
    readonly_fields = ('fecha_envio', 'fecha_lectura')


# Customize admin site
admin.site.site_header = 'I.E. 1122 María Auxiliadora — Administración'
admin.site.site_title = 'Gestión Escolar Admin'
admin.site.index_title = 'Panel de Administración'
