# 🏍️ Venta Motos API

Sistema backend para la gestión de una plataforma de venta de motos. Desarrollado con Django REST Framework y PostgreSQL, permite a los clientes registrarse, explorar el catálogo y realizar compras directamente desde la app, mientras el staff gestiona el inventario, ventas, financiamientos y posventa.

**Integrantes:**
- Alison Venegas
- Victoria Solórzano
- Victoria Chicaiza

---

## Tecnologías

- Python 3.11 / Django 5.x
- Django REST Framework
- PostgreSQL
- JWT (SimpleJWT)
- Gunicorn + Nginx (producción)

---

## Instalación local

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/venta_motos.git
cd venta_motos
```

### 2. Crear el entorno virtual

```bash
python -m venv .venv
```

Activar:

- Windows: `.venv\Scripts\activate`
- Mac/Linux: `source .venv/bin/activate`

### 3. Instalar dependencias

```bash
pip install uv
uv sync
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=venta_motos
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password
DEFAULT_FROM_EMAIL=Venta Motos <tu_correo@gmail.com>

FRONTEND_URL=http://localhost:3000
```

> Para `EMAIL_HOST_PASSWORD` usa una contraseña de aplicación de Google, no la contraseña normal.

### 5. Crear la base de datos

En pgAdmin o psql:

```sql
CREATE DATABASE venta_motos;
```

### 6. Ejecutar migraciones

```bash
python manage.py migrate
```

### 7. Crear superusuario

```bash
python manage.py shell
```

```python
from moto.models import Usuario
u = Usuario.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='Admin1234!',
    cedula='0000000000',
    first_name='Admin',
    last_name='Sistema'
)
exit()
```

### 8. Ejecutar el servidor

```bash
python manage.py runserver
```

La API estará disponible en `https://moto-store-api.uaeftt-ute.site/`

El panel de administración en `https://moto-store-api.uaeftt-ute.site/admin/`

---

## Despliegue en VPS

### Configuración del VPS

```bash
# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install python3-pip python3-venv postgresql nginx -y
```

### Configuración de PostgreSQL

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE venta_motos;
CREATE USER venta_motos_user WITH PASSWORD 'contraseña_segura';
GRANT ALL PRIVILEGES ON DATABASE venta_motos TO venta_motos_user;
\q
```

### Configuración de Gunicorn

Crear archivo de servicio `/etc/systemd/system/venta_motos.service`:

```ini
[Unit]
Description=Venta Motos Gunicorn
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/venta_motos
ExecStart=/home/ubuntu/venta_motos/.venv/bin/gunicorn config.wsgi:application --workers 3 --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable venta_motos
sudo systemctl start venta_motos
```

### Configuración de Nginx

Crear archivo `/etc/nginx/sites-available/venta_motos`:

```nginx
server {
    listen 80;
    server_name tu_dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /home/ubuntu/venta_motos/staticfiles/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/venta_motos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Uso de la API

### Obtener token JWT

**Registro de cliente:**

```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "juan123",
    "email": "juan@example.com",
    "password": "Pass1234!",
    "password2": "Pass1234!",
    "nombre": "Juan",
    "apellido": "Perez",
    "cedula": "1234567890",
    "telefono": "0999999999"
}
```

**Login:**

```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "juan123",
    "password": "Pass1234!"
}
```

Respuesta:

```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_id": 1,
    "username": "juan123",
    "email": "juan@example.com",
    "is_staff": false
}
```

### Usar endpoints protegidos

Incluye el token en el header de cada petición:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Ejemplos de peticiones

**Listar motos (sin autenticación):**

```http
GET /api/motos/
```

**Realizar una compra (cliente autenticado):**

```http
POST /api/ventas/comprar/
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "metodo_pago": "tarjeta",
    "items": [
        {"moto_id": 1, "cantidad": 1}
    ]
}
```

**Ver mis compras:**

```http
GET /api/ventas/mis-compras/
Authorization: Bearer {access_token}
```

**Registrar un vendedor (solo admin):**

```http
POST /api/auth/register-staff/
Authorization: Bearer {access_token_admin}
Content-Type: application/json

{
    "username": "vendedor1",
    "email": "vendedor1@example.com",
    "password": "Pass1234!",
    "nombre": "Carlos",
    "apellido": "Lopez",
    "cedula": "0987654321",
    "telefono": "0988888888",
    "rol": "vendedor"
}
```

---

## Credenciales de prueba

Para facilitar las pruebas de la API en drf-spectacular, se han creado los siguientes usuarios:
| Usuario | Contraseña |
|---------|------------|
| admin | Admin1234! |
| prueba | prueba123 |

> Estas credenciales son solo para entorno de desarrollo/pruebas.
## Endpoints

### Autenticación
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/register/` | Registro de cliente |
| POST | `/api/auth/register-staff/` | Registro de staff | 
| POST | `/api/auth/login/` | Login (obtener JWT) | 
| POST | `/api/auth/token/refresh/` | Renovar token | 
| POST | `/api/auth/token/verify/` | Verificar token | 
| POST | `/api/auth/logout/` | Cerrar sesión | 

### Usuarios
| Método | Ruta | Descripción | 
|--------|------|-------------|
| GET | `/api/users/` | Listar usuarios | 
| GET | `/api/users/profile/` | Ver mi perfil | 
| PATCH | `/api/users/profile/` | Editar mi perfil | 
| POST | `/api/users/change-password/` | Cambiar contraseña | 
| POST | `/api/users/{id}/toggle-active/` | Activar/desactivar usuario | 
| GET | `/api/users/stats/` | Estadísticas de usuarios | 

### Clientes
| Método | Ruta | Descripción | 
|--------|------|-------------|
| GET | `/api/clientes/` | Listar clientes | 
| POST | `/api/clientes/` | Crear cliente | 
| GET | `/api/clientes/{id}/` | Ver cliente |
| PATCH | `/api/clientes/{id}/` | Editar cliente | 
| DELETE | `/api/clientes/{id}/` | Eliminar cliente | 
| GET | `/api/clientes/{id}/ventas/` | Ventas de un cliente |
| GET | `/api/clientes/stats/` | Estadísticas | 

### Vendedores (Staff)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/vendedores/` | Listar vendedores | 
| POST | `/api/vendedores/` | Crear perfil staff | 
| GET | `/api/vendedores/{id}/` | Ver vendedor | 
| PATCH | `/api/vendedores/{id}/` | Editar vendedor | 
| DELETE | `/api/vendedores/{id}/` | Eliminar vendedor | 
| GET | `/api/vendedores/stats/` | Estadísticas | 

### Motos
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/motos/` | Listar motos | 
| POST | `/api/motos/` | Crear moto | 
| GET | `/api/motos/{id}/` | Ver moto | 
| PATCH | `/api/motos/{id}/` | Editar moto | 
| DELETE | `/api/motos/{id}/` | Eliminar moto |
| GET | `/api/motos/stats/` | Estadísticas |

### Marcas

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/marcas/` | Listar marcas |
| POST | `/api/marcas/` | Crear marca |
| GET | `/api/marcas/{id}/` | Ver marca |
| PATCH | `/api/marcas/{id}/` | Editar marca |
| DELETE | `/api/marcas/{id}/` | Eliminar marca |
| GET | `/api/marcas/stats/` | Estadísticas |

### Categorías

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/categorias/` | Listar categorías |
| POST | `/api/categorias/` | Crear categoría |
| GET | `/api/categorias/{id}/` | Ver categoría |
| PATCH | `/api/categorias/{id}/` | Editar categoría |
| DELETE | `/api/categorias/{id}/` | Eliminar categoría |
| GET | `/api/categorias/stats/` | Estadísticas |

### Repuestos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/repuestos/` | Listar repuestos |
| POST | `/api/repuestos/` | Crear repuesto |
| GET | `/api/repuestos/{id}/` | Ver repuesto |
| PATCH | `/api/repuestos/{id}/` | Editar repuesto |
| DELETE | `/api/repuestos/{id}/` | Eliminar repuesto |
| GET | `/api/repuestos/stats/` | Estadísticas |

### Sucursales

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/sucursales/` | Listar sucursales |
| POST | `/api/sucursales/` | Crear sucursal |
| GET | `/api/sucursales/{id}/` | Ver sucursal |
| PATCH | `/api/sucursales/{id}/` | Editar sucursal |
| DELETE | `/api/sucursales/{id}/` | Eliminar sucursal |
| GET | `/api/sucursales/stats/` | Estadísticas |

### Direcciones

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/direcciones/` | Listar direcciones |
| POST | `/api/direcciones/` | Crear dirección |
| GET | `/api/direcciones/{id}/` | Ver dirección |
| PATCH | `/api/direcciones/{id}/` | Editar dirección |
| DELETE | `/api/direcciones/{id}/` | Eliminar dirección |
| GET | `/api/direcciones/stats/` | Estadísticas |

### Inventario

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/inventario/` | Listar inventario |
| POST | `/api/inventario/` | Crear registro |
| GET | `/api/inventario/{id}/` | Ver registro |
| PATCH | `/api/inventario/{id}/` | Editar registro |
| DELETE | `/api/inventario/{id}/` | Eliminar registro |
| GET | `/api/inventario/stats/` | Estadísticas |

### Sucursal Staff

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/sucursal-staff/` | Listar asignaciones |
| POST | `/api/sucursal-staff/` | Asignar staff |
| GET | `/api/sucursal-staff/{id}/` | Ver asignación |
| DELETE | `/api/sucursal-staff/{id}/` | Eliminar asignación |
| GET | `/api/sucursal-staff/stats/` | Estadísticas |

### Proveedores

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/proveedores/` | Listar proveedores |
| POST | `/api/proveedores/` | Crear proveedor |
| GET | `/api/proveedores/{id}/` | Ver proveedor |
| PATCH | `/api/proveedores/{id}/` | Editar proveedor |
| DELETE | `/api/proveedores/{id}/` | Eliminar proveedor |
| GET | `/api/proveedores/stats/` | Estadísticas |

### Ventas

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/ventas/` | Listar ventas |
| POST | `/api/ventas/` | Crear venta |
| GET | `/api/ventas/{id}/` | Ver venta |
| PATCH | `/api/ventas/{id}/` | Editar venta |
| DELETE | `/api/ventas/{id}/` | Eliminar venta |
| POST | `/api/ventas/comprar/` | Comprar |
| GET | `/api/ventas/mis-compras/` | Mis compras |
| GET | `/api/ventas/stats/` | Estadísticas |

### Detalle Ventas

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/detalle-ventas/` | Listar detalles |
| POST | `/api/detalle-ventas/` | Crear detalle |
| GET | `/api/detalle-ventas/{id}/` | Ver detalle |
| DELETE | `/api/detalle-ventas/{id}/` | Eliminar detalle |
| GET | `/api/detalle-ventas/stats/` | Estadísticas |

### Compras

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/compras/` | Listar compras |
| POST | `/api/compras/` | Crear compra |
| GET | `/api/compras/{id}/` | Ver compra |
| PATCH | `/api/compras/{id}/` | Editar compra |
| DELETE | `/api/compras/{id}/` | Eliminar compra |
| GET | `/api/compras/stats/` | Estadísticas |

### Detalle Compras

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/detalle-compras/` | Listar detalles |
| POST | `/api/detalle-compras/` | Crear detalle |
| GET | `/api/detalle-compras/{id}/` | Ver detalle |
| DELETE | `/api/detalle-compras/{id}/` | Eliminar detalle |
| GET | `/api/detalle-compras/stats/` | Estadísticas |

### Garantías

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/garantias/` | Listar garantías |
| POST | `/api/garantias/` | Crear garantía |
| GET | `/api/garantias/{id}/` | Ver garantía |
| PATCH | `/api/garantias/{id}/` | Editar garantía |
| DELETE | `/api/garantias/{id}/` | Eliminar garantía |
| GET | `/api/garantias/stats/` | Estadísticas |

### Mantenimientos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/mantenimientos/` | Listar mantenimientos |
| POST | `/api/mantenimientos/` | Crear mantenimiento |
| GET | `/api/mantenimientos/{id}/` | Ver mantenimiento |
| PATCH | `/api/mantenimientos/{id}/` | Editar mantenimiento |
| DELETE | `/api/mantenimientos/{id}/` | Eliminar mantenimiento |
| GET | `/api/mantenimientos/stats/` | Estadísticas |

### Financiamientos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/financiamientos/` | Listar financiamientos |
| POST | `/api/financiamientos/` | Crear financiamiento |
| GET | `/api/financiamientos/{id}/` | Ver financiamiento |
| PATCH | `/api/financiamientos/{id}/` | Editar financiamiento |
| DELETE | `/api/financiamientos/{id}/` | Eliminar financiamiento |
| GET | `/api/financiamientos/stats/` | Estadísticas |

### Cuotas de Pago

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/cuotas-pago/` | Listar cuotas |
| POST | `/api/cuotas-pago/` | Crear cuota |
| GET | `/api/cuotas-pago/{id}/` | Ver cuota |
| PATCH | `/api/cuotas-pago/{id}/` | Editar cuota |
| DELETE | `/api/cuotas-pago/{id}/` | Eliminar cuota |
| GET | `/api/cuotas-pago/stats/` | Estadísticas |

### Historial de Precios

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/historial-precios/` | Listar historial |
| GET | `/api/historial-precios/{id}/` | Ver registro |
| DELETE | `/api/historial-precios/{id}/` | Eliminar registro |
| GET | `/api/historial-precios/stats/` | Estadísticas |

> El historial de precios se genera automáticamente cuando se actualiza el precio de una moto.

### Reseñas

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/resenas/` | Listar reseñas |
| POST | `/api/resenas/` | Crear reseña |
| GET | `/api/resenas/{id}/` | Ver reseña |
| PATCH | `/api/resenas/{id}/` | Editar reseña |
| DELETE | `/api/resenas/{id}/` | Eliminar reseña |
| GET | `/api/resenas/stats/` | Estadísticas |

### Logs de Actividad

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/logs-actividad/` | Listar logs |
| GET | `/api/logs-actividad/{id}/` | Ver log |
| GET | `/api/logs-actividad/stats/` | Estadísticas |

> Los logs se generan automáticamente en cada acción importante del sistema.

### Historial del Cliente

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/historial-cliente/` | Listar historial |
| GET | `/api/historial-cliente/{id}/` | Ver registro |
| GET | `/api/historial-cliente/mi-historial/` | Mi historial |
| GET | `/api/historial-cliente/stats/` | Estadísticas |

> El historial se genera automáticamente en compras, mantenimientos, garantías, financiamientos y reseñas.

### Notificaciones del Cliente

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/notificaciones-cliente/` | Listar notificaciones |
| POST | `/api/notificaciones-cliente/` | Crear notificación |
| GET | `/api/notificaciones-cliente/{id}/` | Ver notificación |
| PATCH | `/api/notificaciones-cliente/{id}/` | Editar notificación |
| DELETE | `/api/notificaciones-cliente/{id}/` | Eliminar notificación |
| PATCH | `/api/notificaciones-cliente/{id}/marcar-leida/` | Marcar como leída |
| GET | `/api/notificaciones-cliente/mis-notificaciones/` | Mis notificaciones |
| GET | `/api/notificaciones-cliente/stats/` | Estadísticas |

> El historial se genera automáticamente en compras, mantenimientos, garantías, financiamientos y reseñas.

### Notificaciones del Cliente
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/notificaciones-cliente/` | Listar notificaciones | Sí |
| POST | `/api/notificaciones-cliente/` | Crear notificación | Staff |
| GET | `/api/notificaciones-cliente/{id}/` | Ver notificación | Sí |
| PATCH | `/api/notificaciones-cliente/{id}/` | Editar notificación | Staff |
| DELETE | `/api/notificaciones-cliente/{id}/` | Eliminar notificación | Staff |
| PATCH | `/api/notificaciones-cliente/{id}/marcar-leida/` | Marcar como leída | Sí (cliente) |
| GET | `/api/notificaciones-cliente/mis-notificaciones/` | Mis notificaciones | Sí (cliente) |
| GET | `/api/notificaciones-cliente/stats/` | Estadísticas | Sí |

---

## Filtros disponibles

La mayoría de endpoints soportan filtros por query params. Ejemplos:

```
GET /api/motos/?marca=1&precio_min=5000&precio_max=10000
GET /api/motos/?search=honda
GET /api/ventas/?metodo_pago=efectivo
GET /api/clientes/?search=juan
GET /api/historial-precios/?moto=1
GET /api/resenas/?rating=5
```

---

## Funcionalidades automáticas

El sistema incluye las siguientes acciones automáticas sin intervención manual:

| Acción | Disparador |
|--------|-----------|
| Envío de factura por correo | Al crear una venta |
| Registro en historial del cliente | Al comprar, crear mantenimiento, garantía, financiamiento o reseña |
| Registro en historial de precios | Al actualizar el precio de una moto |
| Log de login | Al iniciar sesión |
| Log de actividad (CREATE/UPDATE/DELETE) | En tablas principales del sistema |