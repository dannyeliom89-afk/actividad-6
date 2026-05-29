import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_escolar.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

print('\n=== CUENTAS DE USUARIO ===')
for u in User.objects.all():
    rol = getattr(u, 'rol', 'N/A')
    print(f'Rol: {rol} | Usuario: {u.username} | Email: {u.email} | Es Admin: {u.is_superuser}')
print('==========================\n')
