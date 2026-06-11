Venta Motos API
API REST para la gestión de ventas de una concesionaria de motocicletas. Permite administrar el inventario de motos, clientes, vendedores y el proceso completo de ventas con sus detalles.
Stack: Django 5.2 · Django REST Framework · SimpleJWT · PostgreSQL · Python 3.11
---URLs de despliegue
Entorno	URL
Producción	https://chicaiza-motos.uaeftt-ute.site
API base	https://chicaiza-motos.uaeftt-ute.site/api
Admin	https://chicaiza-motos.uaeftt-ute.site/admin
IP directa	http://20.172.64.205/api
---
📋 Tabla de contenidos
Instalación y ejecución
Variables de entorno
Listado de endpoints
Autenticación
Ejemplos de uso con token
Filtros y búsqueda
Paginación
Permisos
Tests
Colección Postman / Thunder Client
---
⚙️ Instalación y ejecución
Prerrequisitos
Python 3.11+
PostgreSQL 14+
`uv` (gestor de dependencias recomendado)
1 · Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd venta-motos
```
2 · Instalar dependencias
```bash
# Con uv (recomendado)
uv sync

# Con pip clásico
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows
pip install -r requirements.txt
```
Dependencias principales:
Paquete	Versión
django	≥ 5.2
djangorestframework	≥ 3.17
djangorestframework-simplejwt	incluido
django-filter	incluido
psycopg2-binary	≥ 2.9
python-decouple	≥ 3.8
gunicorn	≥ 26.0
3 · Configurar variables de entorno
Copia el ejemplo y edita los valores (ver sección siguiente):
```bash
cp .env.example .env
```
4 · Crear la base de datos en PostgreSQL
```sql
CREATE DATABASE venta_motos;
```
5 · Aplicar migraciones
```bash
uv run python manage.py migrate
```
6 · Crear superusuario (opcional)
```bash
uv run python manage.py createsuperuser
```
7 · Ejecutar el servidor
```bash
# Desarrollo
uv run python manage.py runserver

# Producción con Gunicorn
uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```
La API queda disponible en `http://localhost:8000/api/`.
---
🔑 Variables de entorno
Crea el archivo `.env` en la raíz del proyecto:
```env
# Base de datos PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=venta_motos
DB_USER=postgres
DB_PASSWORD=tu_contraseña_segura

# Base de datos de pruebas (opcional, por defecto: chicaiza_motos_test_db)
TEST_DB_NAME=venta_motos_test

# Django
SECRET_KEY=cambia_esto_por_una_clave_larga_y_aleatoria
```
> ⚠️ Nunca subas el `.env` real al repositorio. El `SECRET_KEY` de `settings.py` es solo para desarrollo local.
---
📌 Listado de endpoints
Todos los endpoints se montan bajo el prefijo `/api/`.
Autenticación
Método	Endpoint	Descripción	Auth
`POST`	`/api/auth/register/`	Registro de usuario	No
`POST`	`/api/auth/login/`	Login → devuelve `access` + `refresh`	No
`POST`	`/api/auth/token/refresh/`	Renovar access token	No
`POST`	`/api/auth/token/verify/`	Verificar validez de un token	No
`POST`	`/api/auth/logout/`	Logout (invalida el refresh token)	✅
Usuarios
Método	Endpoint	Descripción	Auth
`GET`	`/api/users/`	Listar usuarios	✅
`GET`	`/api/users/{id}/`	Obtener usuario	✅
`PUT`	`/api/users/{id}/`	Actualizar usuario completo	✅ Staff
`PATCH`	`/api/users/{id}/`	Actualizar usuario parcial	✅ Staff
`DELETE`	`/api/users/{id}/`	Eliminar usuario	✅ Staff
Clientes
Método	Endpoint	Descripción	Auth
`GET`	`/api/clientes/`	Listar clientes	✅
`POST`	`/api/clientes/`	Crear cliente	✅ Staff
`GET`	`/api/clientes/{id}/`	Obtener cliente	✅
`PUT`	`/api/clientes/{id}/`	Actualizar cliente	✅ Staff
`PATCH`	`/api/clientes/{id}/`	Actualizar parcial	✅ Staff
`DELETE`	`/api/clientes/{id}/`	Eliminar cliente	✅ Staff
`GET`	`/api/clientes/{id}/ventas/`	Ventas del cliente	✅
`GET`	`/api/clientes/stats/`	Estadísticas de clientes	✅
Vendedores
Método	Endpoint	Descripción	Auth
`GET`	`/api/vendedores/`	Listar vendedores	✅
`POST`	`/api/vendedores/`	Crear vendedor	✅ Staff
`GET`	`/api/vendedores/{id}/`	Obtener vendedor	✅
`PUT`	`/api/vendedores/{id}/`	Actualizar vendedor	✅ Staff
`PATCH`	`/api/vendedores/{id}/`	Actualizar parcial	✅ Staff
`DELETE`	`/api/vendedores/{id}/`	Eliminar vendedor	✅ Staff
`GET`	`/api/vendedores/stats/`	Estadísticas de vendedores	✅
Motos
Método	Endpoint	Descripción	Auth
`GET`	`/api/motos/`	Listar motos	✅
`POST`	`/api/motos/`	Crear moto	✅ Staff
`GET`	`/api/motos/{id}/`	Obtener moto	✅
`PUT`	`/api/motos/{id}/`	Actualizar moto	✅ Staff
`PATCH`	`/api/motos/{id}/`	Actualizar parcial	✅ Staff
`DELETE`	`/api/motos/{id}/`	Eliminar moto	✅ Staff
`GET`	`/api/motos/stats/`	Estadísticas de motos	✅
Ventas
Método	Endpoint	Descripción	Auth
`GET`	`/api/ventas/`	Listar ventas	✅
`POST`	`/api/ventas/`	Crear venta	✅ Staff
`GET`	`/api/ventas/{id}/`	Obtener venta	✅
`PUT`	`/api/ventas/{id}/`	Actualizar venta	✅ Staff
`PATCH`	`/api/ventas/{id}/`	Actualizar parcial	✅ Staff
`DELETE`	`/api/ventas/{id}/`	Eliminar venta	✅ Staff
`GET`	`/api/ventas/stats/`	Estadísticas de ventas	✅
Detalle Ventas
Método	Endpoint	Descripción	Auth
`GET`	`/api/detalle-ventas/`	Listar detalles	✅
`POST`	`/api/detalle-ventas/`	Crear detalle	✅ Staff
`GET`	`/api/detalle-ventas/{id}/`	Obtener detalle	✅
`PUT`	`/api/detalle-ventas/{id}/`	Actualizar detalle	✅ Staff
`PATCH`	`/api/detalle-ventas/{id}/`	Actualizar parcial	✅ Staff
`DELETE`	`/api/detalle-ventas/{id}/`	Eliminar detalle	✅ Staff
`GET`	`/api/detalle-ventas/stats/`	Estadísticas	✅
Utilidades
Método	Endpoint	Descripción	Auth
`GET`	`/api/health/`	Estado del servidor	No
`GET`	`/api/testing-cicd/`	Endpoint de prueba CI	No
---
🔐 Autenticación
La API usa JWT (JSON Web Tokens) con `rest_framework_simplejwt`. Cada token incluye los campos `username`, `email` e `is_staff`.
Flujo completo
```
1. POST /api/auth/register/   → obtener access + refresh
2. POST /api/auth/login/      → obtener access + refresh
3. Usar access en el header   → Authorization: Bearer <access_token>
4. POST /api/auth/token/refresh/  → renovar cuando expire
5. POST /api/auth/logout/     → invalidar refresh (blacklist)
```
---
🧪 Ejemplos de uso con token
> Reemplaza `<TOKEN>` con el `access` obtenido en login.  
> Base URL de producción: `https://chicaiza-motos.uaeftt-ute.site/api`
---
Registro
```bash
curl -X POST https://chicaiza-motos.uaeftt-ute.site/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan_vendedor",
    "email": "juan@example.com",
    "password": "Pass1234!",
    "password2": "Pass1234!"
  }'
```
Respuesta `201`:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 1,
  "username": "juan_vendedor",
  "email": "juan@example.com",
  "is_staff": false
}
```
---
Login
```bash
curl -X POST https://chicaiza-motos.uaeftt-ute.site/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "juan_vendedor", "password": "Pass1234!"}'
```
Respuesta `200`:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 1,
  "username": "juan_vendedor",
  "email": "juan@example.com",
  "is_staff": false
}
```
---
Crear un cliente
```bash
curl -X POST https://chicaiza-motos.uaeftt-ute.site/api/clientes/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "María",
    "apellido": "Gómez",
    "cedula": "1712345678",
    "telefono": "0991234567",
    "correo": "maria@example.com",
    "direccion": "Av. 6 de Diciembre N33-100, Quito"
  }'
```
Respuesta `201`:
```json
{
  "id": 1,
  "nombre": "María",
  "apellido": "Gómez",
  "cedula": "1712345678",
  "telefono": "0991234567",
  "correo": "maria@example.com",
  "direccion": "Av. 6 de Diciembre N33-100, Quito"
}
```
---
Listar clientes
```bash
curl https://chicaiza-motos.uaeftt-ute.site/api/clientes/ \
  -H "Authorization: Bearer <TOKEN>"
```
Respuesta `200`:
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "nombre": "María",
      "apellido": "Gómez",
      "cedula": "1712345678",
      "telefono": "0991234567",
      "correo": "maria@example.com",
      "direccion": "Av. 6 de Diciembre N33-100, Quito"
    }
  ]
}
```
---
Crear una moto
```bash
curl -X POST https://chicaiza-motos.uaeftt-ute.site/api/motos/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "marca": "Yamaha",
    "modelo": "FZ 150",
    "anio": 2024,
    "cilindraje": 150,
    "color": "Rojo",
    "precio": "3200.00",
    "stock": 5,
    "estado": "disponible"
  }'
```
Respuesta `201`:
```json
{
  "id": 1,
  "marca": "Yamaha",
  "modelo": "FZ 150",
  "anio": 2024,
  "cilindraje": 150,
  "color": "Rojo",
  "precio": "3200.00",
  "stock": 5,
  "estado": "disponible"
}
```
---
Crear una venta
```bash
curl -X POST https://chicaiza-motos.uaeftt-ute.site/api/ventas/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": 1,
    "vendedor": 1,
    "metodo_pago": "efectivo",
    "total": "3200.00"
  }'
```
Respuesta `201`:
```json
{
  "id": 1,
  "cliente": 1,
  "vendedor": 1,
  "fecha_venta": "2026-06-03T10:30:00Z",
  "metodo_pago": "efectivo",
  "total": "3200.00",
  "cliente_nombre": "María Gómez",
  "vendedor_nombre": "Carlos Pérez"
}
```
---
Crear un detalle de venta
```bash
curl -X POST https://chicaiza-motos.uaeftt-ute.site/api/detalle-ventas/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "venta": 1,
    "moto": 1,
    "cantidad": 1,
    "precio_unitario": "3200.00"
  }'
```
Respuesta `201`:
```json
{
  "id": 1,
  "venta": 1,
  "moto": 1,
  "cantidad": 1,
  "precio_unitario": "3200.00",
  "subtotal": "3200.00",
  "moto_nombre": "Yamaha FZ 150"
}
```
---
Renovar token
```bash
curl -X POST https://chicaiza-motos.uaeftt-ute.site/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<REFRESH_TOKEN>"}'
```
Respuesta `200`:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```
---
Logout
```bash
curl -X POST https://chicaiza-motos.uaeftt-ute.site/api/auth/logout/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<REFRESH_TOKEN>"}'
```
Respuesta `200`:
```json
{
  "message": "Session closed successfully."
}
```
---
🔍 Filtros y búsqueda
Todos los listados soportan búsqueda (`?search=`), ordenamiento (`?ordering=`) y filtros específicos por campo.
Motos
Parámetro	Ejemplo	Descripción
`search`	`?search=Yamaha`	Busca en marca, modelo, color, estado
`marca`	`?marca=Honda`	Filtro exacto (insensible a mayúsculas)
`modelo`	`?modelo=FZ`	Filtro parcial
`precio_min`	`?precio_min=2000`	Precio mayor o igual
`precio_max`	`?precio_max=5000`	Precio menor o igual
`anio_min`	`?anio_min=2022`	Año mayor o igual
`anio_max`	`?anio_max=2024`	Año menor o igual
`stock_min`	`?stock_min=1`	Stock mayor o igual
`estado`	`?estado=disponible`	`disponible` · `vendida` · `reservada`
`ordering`	`?ordering=-precio`	Ordenar (- para descendente)
Clientes
Parámetro	Ejemplo
`search`	`?search=María`
`nombre`	`?nombre=María`
`cedula`	`?cedula=1712345678`
Ventas
Parámetro	Ejemplo
`metodo_pago`	`?metodo_pago=efectivo`
`cliente`	`?cliente=1`
`vendedor`	`?vendedor=1`
`fecha_venta`	`?fecha_venta=2026-06-03`
`ordering`	`?ordering=-fecha_venta`
Detalle Ventas
Parámetro	Ejemplo
`moto_marca`	`?moto_marca=Yamaha`
`moto_modelo`	`?moto_modelo=FZ`
`venta`	`?venta=1`
`precio_unitario_min`	`?precio_unitario_min=2000`
---
📄 Paginación
Todos los listados están paginados.
Parámetro	Descripción	Default
`page`	Número de página	`1`
`page_size`	Elementos por página (máx. 100)	`10`
Ejemplo: `GET /api/motos/?page=2&page_size=20`
Estructura de respuesta:
```json
{
  "count": 45,
  "next": "https://chicaiza-motos.uaeftt-ute.site/api/motos/?page=3",
  "previous": "https://chicaiza-motos.uaeftt-ute.site/api/motos/?page=1",
  "results": [ ... ]
}
```
---
🛡️ Permisos
Permiso	Aplica a	Regla
`IsStaffOrReadOnly`	Todos los ViewSets	Autenticados pueden leer (`GET`). Solo `is_staff=true` puede crear, editar o eliminar.
`IsOwnerOrStaff`	Objetos específicos	Staff accede a todo. Usuarios comunes solo a sus propios objetos.
---
🧪 Tests
```bash
# Todos los tests
uv run python manage.py test moto.tests

# Módulo específico
uv run python manage.py test moto.tests.test_ventas
uv run python manage.py test moto.tests.test_motos
```
Archivo	Módulo cubierto
`test_auth.py`	Registro, login, logout, tokens
`test_users.py`	CRUD de usuarios
`test_clientes.py`	CRUD de clientes
`test_vendedores.py`	CRUD de vendedores
`test_motos.py`	CRUD de motos
`test_ventas.py`	CRUD de ventas
`test_detalle_ventas.py`	CRUD de detalles de venta
---
📮 Colección Postman / Thunder Client
El archivo `venta-motos.postman_collection.json` incluido en este repositorio contiene todas las peticiones organizadas por módulo, con:
Variables de colección (`base_url`, `access_token`, `refresh_token`)
Script automático en Login y Token Refresh que guarda los tokens en las variables
Cuerpos JSON de ejemplo para cada endpoint
Importar en Postman
Abre Postman → Import
Selecciona el archivo `venta-motos.postman_collection.json`
Ve a la carpeta 🔐 Auth → Login, ejecuta la petición
Los tokens quedan guardados automáticamente en las variables de colección
El resto de peticiones los usan con `Bearer {{access_token}}`
Importar en Thunder Client (VS Code)
Abre Thunder Client → pestaña Collections → Import
Selecciona `venta-motos.postman_collection.json`  
(Thunder Client importa colecciones en formato Postman v2.1)
Variable de entorno rápida en Postman
Variable	Valor inicial
`base_url`	`https://chicaiza-motos.uaeftt-ute.site/api`
`access_token`	(se llena automáticamente al hacer Login)
`refresh_token`	(se llena automáticamente al hacer Login)
"# venta_motos" 
