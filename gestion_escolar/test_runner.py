# -*- coding: utf-8 -*-
"""
Script de pruebas completas del sistema de gestión escolar.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_escolar.settings')
sys.path.insert(0, '.')
django.setup()

from django.test import Client
from core.models import User, PropuestaActividad, Excursion, Seccion, Destino, Mensaje, Aviso, ActividadInstitucional, Evidencia

results = []

def test(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    msg = f"{status} - {name}" + (f" ({detail})" if detail else "")
    results.append(msg)
    print(msg)

c = Client()
c2 = Client()

# TEST 1: Login Director
r = c.post('/login/', {'username': 'director', 'password': 'admin1234'})
test("Login Director (director/admin1234)", r.status_code == 302, f"status={r.status_code}")

# TEST 2: Login Docente
r2 = c2.post('/login/', {'username': 'docente1', 'password': 'docente1234'})
test("Login Docente1 (docente1/docente1234)", r2.status_code == 302, f"status={r2.status_code}")

# TEST 3: Dashboard director
r3 = c.get('/dashboard/')
test("Dashboard Director carga OK", r3.status_code == 200, f"status={r3.status_code}")

# TEST 4: Dashboard docente
r4 = c2.get('/dashboard/')
test("Dashboard Docente carga OK", r4.status_code == 200, f"status={r4.status_code}")

# TEST 5: Actividades lista
r5 = c.get('/actividades/')
test("Actividades - Lista carga OK", r5.status_code == 200)

# TEST 6: Actividad detalle con formulario de evidencia
r6 = c.get('/actividades/1/')
has_ev_form = b'evidencia_subir_actividad' in r6.content
test("Actividad - Detalle con formulario de evidencia", r6.status_code == 200 and has_ev_form, f"form_evidencia={'OK' if has_ev_form else 'NO ENCONTRADO'}")

# TEST 7: Crear actividad como director
r7 = c.post('/actividades/nueva/', {
    'titulo': 'Actividad Automatica de Test',
    'descripcion': 'Creada por script de prueba automatica',
    'fecha': '2026-09-01',
    'lugar': 'Salon Principal',
    'estado': 'pendiente',
})
test("Actividad - Crear nueva (director)", r7.status_code == 302, f"status={r7.status_code}")

# TEST 8: Propuestas lista
r8 = c.get('/propuestas/')
test("Propuestas - Lista carga OK (director)", r8.status_code == 200)

# TEST 9: Crear propuesta como docente
r9 = c2.post('/propuestas/nueva/', {
    'titulo': 'Propuesta Automatica Test',
    'descripcion': 'Propuesta creada por script de prueba',
    'fecha_actividad_propuesta': '2026-09-15',
})
test("Propuesta - Crear nueva (docente)", r9.status_code == 302, f"status={r9.status_code}")

# TEST 10: Revisar propuesta
nueva_propuesta = PropuestaActividad.objects.filter(estado='pendiente').first()
if nueva_propuesta:
    r10 = c.post(f'/propuestas/{nueva_propuesta.pk}/revisar/', {
        'estado': 'aprobada',
        'observacion_admin': 'Aprobada durante test automatico',
    })
    test(f"Propuesta - Revisar/Aprobar #{nueva_propuesta.pk}", r10.status_code == 302, f"status={r10.status_code}")
    # Verificar que se envio mensaje de notificacion
    notif = Mensaje.objects.filter(asunto__icontains=nueva_propuesta.titulo).first()
    test("Propuesta - Notificacion de mensaje enviada al docente", notif is not None)
else:
    test("Propuesta - Revisar/Aprobar", False, "No hay propuestas pendientes para revisar")

# TEST 11: Excursiones lista
r11 = c.get('/excursiones/')
test("Excursiones - Lista carga OK", r11.status_code == 200)

# TEST 12: Crear excursion
seccion = Seccion.objects.first()
destino = Destino.objects.first()
if seccion and destino:
    r12 = c.post('/excursiones/nueva/', {
        'seccion': seccion.pk,
        'destino': destino.pk,
        'fecha': '2026-09-20',
        'num_estudiantes': '28',
        'descripcion': 'Excursion de prueba automatica',
        'estado': 'programada',
    })
    test("Excursion - Crear nueva", r12.status_code == 302, f"status={r12.status_code}")
else:
    test("Excursion - Crear nueva", False, "No hay secciones o destinos disponibles")

# TEST 13: Excursion detalle con evidencia
r13 = c.get('/excursiones/1/')
has_excursion_ev = b'evidencia_subir_excursion' in r13.content
test("Excursion - Detalle con formulario de evidencia", r13.status_code == 200 and has_excursion_ev, f"form={'OK' if has_excursion_ev else 'NO'}")

# TEST 14: Mensajes bandeja
r14 = c.get('/mensajes/')
test("Mensajes - Bandeja carga OK", r14.status_code == 200)

# TEST 15: Enviar mensaje
docente1 = User.objects.get(username='docente1')
r15 = c.post('/mensajes/nuevo/', {
    'para_usuario': docente1.pk,
    'asunto': 'Mensaje de Prueba Automatica',
    'mensaje': 'Este mensaje fue enviado por el script de prueba automatica del sistema',
})
test("Mensajes - Enviar nuevo mensaje", r15.status_code == 302, f"status={r15.status_code}")

# TEST 16: Usuarios lista
r16 = c.get('/usuarios/')
test("Usuarios - Lista carga OK", r16.status_code == 200)

# TEST 17: Crear usuario nuevo
import random
rand_num = random.randint(100, 999)
r17 = c.post('/usuarios/nuevo/', {
    'username': f'docente_auto_{rand_num}',
    'password': 'AutoTest123!',
    'first_name': 'Test',
    'last_name': 'Automatico',
    'email': f'auto_{rand_num}@escuela.edu',
    'role': 'docente',
})
test("Usuarios - Crear nuevo usuario", r17.status_code == 302, f"status={r17.status_code}")

# TEST 18: Calendario
r18 = c.get('/calendario/')
test("Calendario - Vista carga OK", r18.status_code == 200)

# TEST 19: Avisos lista
r19 = c.get('/avisos/')
test("Avisos - Lista carga OK", r19.status_code == 200)

# TEST 20: Crear aviso
r20 = c.post('/avisos/nuevo/', {
    'titulo': 'Aviso de Prueba Automatica',
    'mensaje': 'Este aviso fue creado por el script de prueba',
    'es_urgente': False,
    'activo': True,
})
test("Avisos - Crear nuevo aviso", r20.status_code == 302, f"status={r20.status_code}")

# TEST 21: Reportes panel
r21 = c.get('/reportes/')
test("Reportes - Panel carga OK", r21.status_code == 200)

# TEST 22: PDF reporte
r22 = c.get('/reportes/pdf/')
test("Reportes - PDF generado", r22.status_code == 200 and b'PDF' in r22.content[:10], f"content-type={r22.get('Content-Type','')}")

# TEST 23: PDF actividad individual
r23 = c.get('/actividades/1/pdf/')
test("Actividad - PDF individual generado", r23.status_code == 200 and b'PDF' in r23.content[:10])

# TEST 24: Perfil usuario
r24 = c.get('/perfil/')
test("Perfil - Vista carga OK", r24.status_code == 200)

# TEST 25: Secciones config
r25 = c.get('/config/secciones/')
test("Config - Secciones carga OK", r25.status_code == 200)

# TEST 26: Destinos config
r26 = c.get('/config/destinos/')
test("Config - Destinos carga OK", r26.status_code == 200)

# TEST 27: Docente no puede crear actividad (control de roles)
r27 = c2.get('/actividades/nueva/')
test("Seguridad - Docente NO puede crear actividad", r27.status_code in [302, 403], f"status={r27.status_code} (debe ser 302 redirect)")

# TEST 28: Docente no puede ver usuarios (control de roles)
r28 = c2.get('/usuarios/')
test("Seguridad - Docente NO puede ver usuarios", r28.status_code in [302, 403], f"status={r28.status_code}")

print("\n" + "="*60)
print("RESUMEN FINAL")
print("="*60)
passed = sum(1 for r in results if "PASS" in r)
failed = sum(1 for r in results if "FAIL" in r)
print(f"APROBADAS: {passed}/{len(results)}")
print(f"FALLIDAS:  {failed}/{len(results)}")
print("="*60)

print("\nESTADO DE LA BASE DE DATOS:")
print(f"  Usuarios:          {User.objects.count()}")
print(f"  Actividades:       {ActividadInstitucional.objects.count()}")
print(f"  Propuestas:        {PropuestaActividad.objects.count()}")
print(f"  Excursiones:       {Excursion.objects.count()}")
print(f"  Evidencias subidas:{Evidencia.objects.count()}")
print(f"  Mensajes:          {Mensaje.objects.count()}")
print(f"  Avisos activos:    {Aviso.objects.filter(activo=True).count()}")
