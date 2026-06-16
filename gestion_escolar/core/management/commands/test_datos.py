"""
Script de prueba: crea actividades, excursion, aviso y mensaje de prueba.
Uso: python manage.py test_datos
"""
import sys
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea datos de prueba: actividades, excursion, aviso y mensaje'

    def handle(self, *args, **kwargs):
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')

        from core.models import (
            Seccion, Destino, ActividadInstitucional,
            Excursion, Aviso, Mensaje
        )

        director = User.objects.get(username='director')
        docente = User.objects.filter(role='docente').first()

        self.stdout.write(self.style.MIGRATE_HEADING('Creando datos de prueba...'))

        # ── Secciones ────────────────────────────────────────────────────────
        secs_data = [
            ('1A', 'Primaria', 'manana'),
            ('3B', 'Primaria', 'manana'),
            ('5E', 'Primaria', 'tarde'),
        ]
        secciones = []
        for nombre, nivel, turno in secs_data:
            s, created = Seccion.objects.get_or_create(
                nombre=nombre,
                defaults={'nivel': nivel, 'turno': 'manana'}
            )
            secciones.append(s)
            estado = 'creada' if created else 'ya existia'
            self.stdout.write(f'  Seccion {nombre}: {estado}')

        # ── Destinos ─────────────────────────────────────────────────────────
        dests_data = [
            ('Isla de los Uros', 'Lago Titicaca, Puno', 8.5),
            ('Museo Carlos Dreyer', 'Jr. Conde de Lemos 289, Puno', 1.2),
        ]
        destinos = []
        for nombre, ubic, dist in dests_data:
            d, created = Destino.objects.get_or_create(
                nombre=nombre,
                defaults={'ubicacion': ubic, 'distancia_km': dist}
            )
            destinos.append(d)
            estado = 'creado' if created else 'ya existia'
            self.stdout.write(f'  Destino "{nombre}": {estado}')

        # ── Actividades ──────────────────────────────────────────────────────
        acts_data = [
            ('Dia del Logro Escolar 2026',
             'Presentacion de logros academicos de los estudiantes ante la comunidad educativa.',
             date(2026, 7, 15), 'Patio principal', 'pendiente'),
            ('Simulacro de Evacuacion',
             'Simulacro de sismo coordinado con Defensa Civil.',
             date(2026, 6, 25), 'Toda la institucion', 'en_proceso'),
            ('Feria Cientifica 2026',
             'Exposicion de proyectos cientificos de estudiantes de 4to a 6to grado.',
             date(2026, 8, 10), 'Patio central', 'pendiente'),
        ]
        actividades = []
        for titulo, desc, fecha, lugar, estado in acts_data:
            if not ActividadInstitucional.objects.filter(titulo=titulo).exists():
                act = ActividadInstitucional.objects.create(
                    titulo=titulo,
                    descripcion=desc,
                    fecha=fecha,
                    lugar=lugar,
                    estado=estado,
                    created_by=director,
                )
                actividades.append(act)
                self.stdout.write(self.style.SUCCESS(f'  [OK] Actividad creada: "{titulo}"'))
            else:
                self.stdout.write(f'  Actividad ya existia: "{titulo}"')

        # ── Excursion ────────────────────────────────────────────────────────
        if secciones and destinos:
            if not Excursion.objects.filter(seccion=secciones[0], destino=destinos[0]).exists():
                Excursion.objects.create(
                    seccion=secciones[0],
                    destino=destinos[0],
                    fecha=date(2026, 7, 20),
                    responsable=docente,
                    num_estudiantes=30,
                    estado='programada',
                    descripcion='Visita educativa a las islas flotantes de los Uros.',
                )
                self.stdout.write(self.style.SUCCESS(
                    f'  [OK] Excursion creada: {secciones[0]} -> {destinos[0]} '
                    f'(responsable: {docente.get_full_name()})'
                ))
            else:
                self.stdout.write('  Excursion ya existia')

        # ── Aviso ────────────────────────────────────────────────────────────
        titulo_aviso = 'Reunion de docentes - Viernes 3pm'
        if not Aviso.objects.filter(titulo=titulo_aviso).exists():
            Aviso.objects.create(
                titulo=titulo_aviso,
                mensaje='Se convoca a todos los docentes a reunion el proximo viernes a las 3pm en sala de profesores. Asistencia obligatoria.',
                creado_por=director,
                es_urgente=True,
            )
            self.stdout.write(self.style.SUCCESS(f'  [OK] Aviso creado: "{titulo_aviso}"'))
        else:
            self.stdout.write(f'  Aviso ya existia')

        # ── Mensaje interno ──────────────────────────────────────────────────
        asunto_msg = 'Coordinacion Dia del Logro'
        if not Mensaje.objects.filter(asunto=asunto_msg).exists():
            Mensaje.objects.create(
                de_usuario=director,
                para_usuario=docente,
                asunto=asunto_msg,
                mensaje=f'Estimado/a {docente.get_full_name()}, le pido coordinar la presentacion de su seccion para el Dia del Logro el 15 de julio. Por favor confirme su participacion.',
            )
            self.stdout.write(self.style.SUCCESS(
                f'  [OK] Mensaje enviado a: {docente.get_full_name()} ({docente.username})'
            ))
        else:
            self.stdout.write(f'  Mensaje ya existia')

        # ── Resumen ──────────────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('RESUMEN DE LA BASE DE DATOS:'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'  Usuarios:     {User.objects.count()} ({User.objects.filter(role="director").count()} director, {User.objects.filter(role="docente").count()} docentes)')
        self.stdout.write(f'  Secciones:    {Seccion.objects.count()}')
        self.stdout.write(f'  Destinos:     {Destino.objects.count()}')
        self.stdout.write(f'  Actividades:  {ActividadInstitucional.objects.count()}')
        self.stdout.write(f'  Excursiones:  {Excursion.objects.count()}')
        self.stdout.write(f'  Avisos:       {Aviso.objects.count()}')
        self.stdout.write(f'  Mensajes:     {Mensaje.objects.count()}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Prueba el sistema en: http://127.0.0.1:8000'))
        self.stdout.write('  Director -> usuario: director | pass: director2026')
        self.stdout.write('  Docente  -> usuario: hulmer_1a | pass: Loayza123')
        self.stdout.write('')
