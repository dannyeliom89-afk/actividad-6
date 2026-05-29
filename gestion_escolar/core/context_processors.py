"""
Context processors for global template variables.
"""
from .models import Mensaje, PropuestaActividad


def global_context(request):
    """Inject unread message count and pending proposals into every template."""
    if request.user.is_authenticated:
        mensajes_no_leidos = Mensaje.objects.filter(
            para_usuario=request.user, leido=False
        ).count()
        pendientes_count = 0
        if request.user.is_director:
            pendientes_count = PropuestaActividad.objects.filter(estado='pendiente').count()
        return {
            'mensajes_no_leidos': mensajes_no_leidos,
            'pendientes_count': pendientes_count,
        }
    return {}
