"""
Comando de gestión para limpiar propuestas antiguas.
Elimina automáticamente propuestas rechazadas o pendientes
que tengan más de 24 horas de antigüedad.

Uso manual:
    python manage.py limpiar_propuestas

Uso automático (Windows Task Scheduler) o cron:
    python manage.py limpiar_propuestas --horas 24
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import PropuestaActividad


class Command(BaseCommand):
    help = 'Elimina propuestas rechazadas o pendientes con más de 24 horas de antigüedad'

    def add_arguments(self, parser):
        parser.add_argument(
            '--horas',
            type=int,
            default=24,
            help='Número de horas tras las cuales se eliminan las propuestas (default: 24)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra cuántas propuestas se eliminarían sin eliminarlas realmente'
        )

    def handle(self, *args, **options):
        horas = options['horas']
        dry_run = options['dry_run']
        limite = timezone.now() - timedelta(hours=horas)

        # Solo eliminar rechazadas y pendientes (NUNCA aprobadas)
        propuestas_a_eliminar = PropuestaActividad.objects.filter(
            estado__in=['rechazada', 'pendiente'],
            fecha_propuesta__lte=limite
        )

        total = propuestas_a_eliminar.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS(
                f'✓ No hay propuestas para limpiar (antigüedad > {horas}h).'
            ))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'[DRY-RUN] Se eliminarían {total} propuestas con más de {horas}h:'
            ))
            for p in propuestas_a_eliminar:
                self.stdout.write(
                    f'  - [{p.estado.upper()}] "{p.titulo}" '
                    f'(por: {p.propuesta_por.username}, '
                    f'fecha: {p.fecha_propuesta.strftime("%d/%m/%Y %H:%M")})'
                )
        else:
            titulos = list(propuestas_a_eliminar.values_list('titulo', flat=True))
            propuestas_a_eliminar.delete()
            self.stdout.write(self.style.SUCCESS(
                f'✓ {total} propuesta(s) eliminadas (antigüedad > {horas}h):'
            ))
            for titulo in titulos:
                self.stdout.write(f'  - "{titulo}"')
