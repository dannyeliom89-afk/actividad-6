"""
Comando de gestión para limpiar propuestas rechazadas antiguas.
Elimina automáticamente propuestas RECHAZADAS que tengan más de 7 días (1 semana).
Las propuestas PENDIENTES y APROBADAS NUNCA se eliminan automáticamente.

Uso manual:
    python manage.py limpiar_propuestas

Opciones:
    --dias N        Número de días para considerar expirada (por defecto: 7)
    --dry-run       Solo muestra cuántas se eliminarían sin borrarlas

Programar en Windows Task Scheduler:
    python manage.py limpiar_propuestas --dias 7
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import PropuestaActividad


class Command(BaseCommand):
    help = 'Elimina propuestas RECHAZADAS con más de 7 días de antigüedad'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=7,
            help='Número de días tras los cuales se eliminan las propuestas rechazadas (default: 7)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra cuántas propuestas se eliminarían sin eliminarlas realmente'
        )

    def handle(self, *args, **options):
        dias = options['dias']
        dry_run = options['dry_run']
        limite = timezone.now() - timedelta(days=dias)

        # SOLO eliminar RECHAZADAS (NUNCA pendientes ni aprobadas)
        propuestas_a_eliminar = PropuestaActividad.objects.filter(
            estado='rechazada',
            fecha_propuesta__lte=limite
        )

        total = propuestas_a_eliminar.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS(
                f'✓ No hay propuestas rechazadas para limpiar (antigüedad > {dias} días).'
            ))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'[DRY-RUN] Se eliminarían {total} propuestas rechazadas con más de {dias} días:'
            ))
            for p in propuestas_a_eliminar:
                self.stdout.write(
                    f'  - [RECHAZADA] "{p.titulo}" '
                    f'(por: {p.propuesta_por.username}, '
                    f'fecha: {p.fecha_propuesta.strftime("%d/%m/%Y %H:%M")})'
                )
        else:
            titulos = list(propuestas_a_eliminar.values_list('titulo', flat=True))
            propuestas_a_eliminar.delete()
            self.stdout.write(self.style.SUCCESS(
                f'✓ {total} propuesta(s) rechazadas eliminadas (antigüedad > {dias} días):'
            ))
            for titulo in titulos:
                self.stdout.write(f'  - "{titulo}"')
