# setup_admin.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from moto.models import Usuario, Staff

# Crear superusuario admin
if not Usuario.objects.filter(username='admin').exists():
    u = Usuario.objects.create_superuser(
        username='admin',
        email='admin@ventamotos.com',
        password='Admin1234!',
        cedula='0000000000',
        first_name='Admin',
        last_name='Sistema'
    )
    print(f'✅ Superusuario creado: {u.username}')
else:
    print('ℹ️ Superusuario ya existe')

# Crear usuario vendedor de prueba
if not Usuario.objects.filter(username='vendedor1').exists():
    u_vendedor = Usuario.objects.create_user(
        username='vendedor1',
        email='vendedor1@ventamotos.com',
        password='Pass1234!',
        cedula='0000000001',
        first_name='Carlos',
        last_name='Lopez',
        is_staff=True,
    )
    Staff.objects.create(usuario=u_vendedor, rol='vendedor')
    print(f'✅ Vendedor creado: {u_vendedor.username}')
else:
    print('ℹ️ Vendedor ya existe')

# Crear usuario bodeguero de prueba
if not Usuario.objects.filter(username='bodeguero1').exists():
    u_bodeguero = Usuario.objects.create_user(
        username='bodeguero1',
        email='bodeguero1@ventamotos.com',
        password='Pass1234!',
        cedula='0000000002',
        first_name='Maria',
        last_name='Garcia',
        is_staff=True,
    )
    Staff.objects.create(usuario=u_bodeguero, rol='bodeguero')
    print(f'✅ Bodeguero creado: {u_bodeguero.username}')
else:
    print('ℹ️ Bodeguero ya existe')

print('\n=== Usuarios de prueba ===')
print('Admin:     admin / Admin1234!')
print('Vendedor:  vendedor1 / Pass1234!')
print('Bodeguero: bodeguero1 / Pass1234!')