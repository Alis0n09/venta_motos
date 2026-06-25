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

La API estará disponible en `http://localhost:8000/api/`

El panel de administración en `http://localhost:8000/admin/`

---

## Despliegue en VPS

> Esta sección será completada al finalizar el despliegue en producción.

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
| GET | `/api/marcas/` | Listar marcas | Sí |
| POST | `/api/marcas/` | Crear marca | Staff |
| GET | `/api/marcas/{id}/` | Ver marca | Sí |
| PATCH | `/api/marcas/{id}/` | Editar marca | Staff |
| DELETE | `/api/marcas/{id}/` | Eliminar marca | Staff |
| GET | `/api/marcas/stats/` | Estadísticas | Sí |

### Categorías
| Método | Ruta | Descripción |
|--------|------|-------------|------|
| GET | `/api/categorias/` | Listar categorías | Sí |
| POST | `/api/categorias/` | Crear categoría | Staff |
| GET | `/api/categorias/{id}/` | Ver categoría | Sí |
| PATCH | `/api/categorias/{id}/` | Editar categoría | Staff |
| DELETE | `/api/categorias/{id}/` | Eliminar categoría | Staff |
| GET | `/api/categorias/stats/` | Estadísticas | Sí |

### Repuestos
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/repuestos/` | Listar repuestos | Sí |
| POST | `/api/repuestos/` | Crear repuesto | Staff |
| GET | `/api/repuestos/{id}/` | Ver repuesto | Sí |
| PATCH | `/api/repuestos/{id}/` | Editar repuesto | Staff |
| DELETE | `/api/repuestos/{id}/` | Eliminar repuesto | Staff |
| GET | `/api/repuestos/stats/` | Estadísticas | Sí |

### Sucursales
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/sucursales/` | Listar sucursales | Sí |
| POST | `/api/sucursales/` | Crear sucursal | Staff |
| GET | `/api/sucursales/{id}/` | Ver sucursal | Sí |
| PATCH | `/api/sucursales/{id}/` | Editar sucursal | Staff |
| DELETE | `/api/sucursales/{id}/` | Eliminar sucursal | Staff |
| GET | `/api/sucursales/stats/` | Estadísticas | Sí |

### Direcciones
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/direcciones/` | Listar direcciones | Sí |
| POST | `/api/direcciones/` | Crear dirección | Staff |
| GET | `/api/direcciones/{id}/` | Ver dirección | Sí |
| PATCH | `/api/direcciones/{id}/` | Editar dirección | Staff |
| DELETE | `/api/direcciones/{id}/` | Eliminar dirección | Staff |
| GET | `/api/direcciones/stats/` | Estadísticas | Sí |

### Inventario
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/inventario/` | Listar inventario | Sí |
| POST | `/api/inventario/` | Crear registro | Staff |
| GET | `/api/inventario/{id}/` | Ver registro | Sí |
| PATCH | `/api/inventario/{id}/` | Editar registro | Staff |
| DELETE | `/api/inventario/{id}/` | Eliminar registro | Staff |
| GET | `/api/inventario/stats/` | Estadísticas | Sí |

### Sucursal Staff
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/sucursal-staff/` | Listar asignaciones | Sí |
| POST | `/api/sucursal-staff/` | Asignar staff | Staff |
| GET | `/api/sucursal-staff/{id}/` | Ver asignación | Sí |
| DELETE | `/api/sucursal-staff/{id}/` | Eliminar asignación | Staff |
| GET | `/api/sucursal-staff/stats/` | Estadísticas | Sí |

### Proveedores
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/proveedores/` | Listar proveedores | Sí |
| POST | `/api/proveedores/` | Crear proveedor | Staff |
| GET | `/api/proveedores/{id}/` | Ver proveedor | Sí |
| PATCH | `/api/proveedores/{id}/` | Editar proveedor | Staff |
| DELETE | `/api/proveedores/{id}/` | Eliminar proveedor | Staff |
| GET | `/api/proveedores/stats/` | Estadísticas | Sí |

### Ventas
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/ventas/` | Listar ventas | Sí |
| POST | `/api/ventas/` | Crear venta (staff) | Staff |
| GET | `/api/ventas/{id}/` | Ver venta | Sí |
| PATCH | `/api/ventas/{id}/` | Editar venta | Staff |
| DELETE | `/api/ventas/{id}/` | Eliminar venta | Staff |
| POST | `/api/ventas/comprar/` | Comprar (cliente) | Sí |
| GET | `/api/ventas/mis-compras/` | Mis compras | Sí |
| GET | `/api/ventas/stats/` | Estadísticas | Sí |

### Detalle Ventas
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/detalle-ventas/` | Listar detalles | Sí |
| POST | `/api/detalle-ventas/` | Crear detalle | Staff |
| GET | `/api/detalle-ventas/{id}/` | Ver detalle | Sí |
| DELETE | `/api/detalle-ventas/{id}/` | Eliminar detalle | Staff |
| GET | `/api/detalle-ventas/stats/` | Estadísticas | Sí |

### Compras
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/compras/` | Listar compras | Staff |
| POST | `/api/compras/` | Crear compra | Staff |
| GET | `/api/compras/{id}/` | Ver compra | Staff |
| PATCH | `/api/compras/{id}/` | Editar compra | Staff |
| DELETE | `/api/compras/{id}/` | Eliminar compra | Staff |
| GET | `/api/compras/stats/` | Estadísticas | Staff |

### Detalle Compras
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/detalle-compras/` | Listar detalles | Staff |
| POST | `/api/detalle-compras/` | Crear detalle | Staff |
| GET | `/api/detalle-compras/{id}/` | Ver detalle | Staff |
| DELETE | `/api/detalle-compras/{id}/` | Eliminar detalle | Staff |
| GET | `/api/detalle-compras/stats/` | Estadísticas | Staff |

### Garantías
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/garantias/` | Listar garantías | Sí |
| POST | `/api/garantias/` | Crear garantía | Staff |
| GET | `/api/garantias/{id}/` | Ver garantía | Sí |
| PATCH | `/api/garantias/{id}/` | Editar garantía | Staff |
| DELETE | `/api/garantias/{id}/` | Eliminar garantía | Staff |
| GET | `/api/garantias/stats/` | Estadísticas | Sí |

### Mantenimientos
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/mantenimientos/` | Listar mantenimientos | Sí |
| POST | `/api/mantenimientos/` | Crear mantenimiento | Staff |
| GET | `/api/mantenimientos/{id}/` | Ver mantenimiento | Sí |
| PATCH | `/api/mantenimientos/{id}/` | Editar mantenimiento | Staff |
| DELETE | `/api/mantenimientos/{id}/` | Eliminar mantenimiento | Staff |
| GET | `/api/mantenimientos/stats/` | Estadísticas | Sí |

### Financiamientos
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/financiamientos/` | Listar financiamientos | Staff |
| POST | `/api/financiamientos/` | Crear financiamiento | Staff |
| GET | `/api/financiamientos/{id}/` | Ver financiamiento | Staff |
| PATCH | `/api/financiamientos/{id}/` | Editar financiamiento | Staff |
| DELETE | `/api/financiamientos/{id}/` | Eliminar financiamiento | Staff |
| GET | `/api/financiamientos/stats/` | Estadísticas | Staff |

### Cuotas de Pago
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/cuotas-pago/` | Listar cuotas | Staff |
| POST | `/api/cuotas-pago/` | Crear cuota | Staff |
| GET | `/api/cuotas-pago/{id}/` | Ver cuota | Staff |
| PATCH | `/api/cuotas-pago/{id}/` | Editar cuota | Staff |
| DELETE | `/api/cuotas-pago/{id}/` | Eliminar cuota | Staff |
| GET | `/api/cuotas-pago/stats/` | Estadísticas | Staff |

### Historial de Precios
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/historial-precios/` | Listar historial | Sí |
| GET | `/api/historial-precios/{id}/` | Ver registro | Sí |
| DELETE | `/api/historial-precios/{id}/` | Eliminar registro | Staff |
| GET | `/api/historial-precios/stats/` | Estadísticas | Sí |

> El historial de precios se genera automáticamente cuando se actualiza el precio de una moto.

### Reseñas
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/resenas/` | Listar reseñas | Sí |
| POST | `/api/resenas/` | Crear reseña | Sí (cliente) |
| GET | `/api/resenas/{id}/` | Ver reseña | Sí |
| PATCH | `/api/resenas/{id}/` | Editar reseña | Staff |
| DELETE | `/api/resenas/{id}/` | Eliminar reseña | Staff |
| GET | `/api/resenas/stats/` | Estadísticas | Sí |

### Logs de Actividad
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/logs-actividad/` | Listar logs | Staff |
| GET | `/api/logs-actividad/{id}/` | Ver log | Staff |
| GET | `/api/logs-actividad/stats/` | Estadísticas | Staff |

> Los logs se generan automáticamente en cada acción importante del sistema.

### Historial del Cliente
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/historial-cliente/` | Listar historial | Sí |
| GET | `/api/historial-cliente/{id}/` | Ver registro | Sí |
| GET | `/api/historial-cliente/mi-historial/` | Mi historial | Sí (cliente) |
| GET | `/api/historial-cliente/stats/` | Estadísticas | Sí |

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