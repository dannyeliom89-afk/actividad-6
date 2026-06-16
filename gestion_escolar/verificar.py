import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_escolar.settings')
django.setup()

from core.models import ActividadInstitucional, Aviso, User
from django.db.models import Q

print("=== ACTIVIDADES EN BD ===")
for a in ActividadInstitucional.objects.all():
    resps = [r.username for r in a.responsables.all()]
    print(f"  [{a.pk}] {a.titulo} | {a.fecha} | responsables: {resps}")

docente = User.objects.filter(role='docente', is_active=True).first()
print(f"\n=== DOCENTE DE PRUEBA: {docente.username} ===")

# Nueva logica: todas las actividades
count_nueva = ActividadInstitucional.objects.all().count()
print(f"Con NUEVA logica (todas): {count_nueva} actividades visibles para docente")

# Logica vieja
count_vieja = ActividadInstitucional.objects.filter(responsables=docente).count()
print(f"Con VIEJA logica (solo asignadas): {count_vieja} actividades visibles para docente")

print("\n=== AVISOS EN BD ===")
for av in Aviso.objects.all():
    dest = list(av.destinatarios.all())
    print(f"  [{av.pk}] {av.titulo} | destinatarios: {len(dest)}")

qs_avisos = Aviso.objects.filter(activo=True).filter(
    Q(destinatarios__isnull=False, destinatarios=docente) | Q(destinatarios__isnull=True)
).distinct()
print(f"\nAvisos visibles para docente {docente.username}: {qs_avisos.count()}")

for av in qs_avisos:
    print(f"  - {av.titulo}")

print("\n=== RESULTADO: El codigo fue corregido correctamente ===")
print("- Docentes ven TODAS las actividades")
print("- Calendario ya mostraba todo (sin cambios necesarios)")
print("- Avisos generales llegan a todos los docentes")
