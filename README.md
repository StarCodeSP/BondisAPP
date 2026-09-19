# BondisAPP

Aplicación web colaborativa para consultar información del transporte público de Montevideo y compartir experiencias de viaje. El proyecto combina un backend REST con FastAPI, una base de datos PostgreSQL y un frontend HTML/JavaScript servido por la misma aplicación.

## Estado actual

La aplicación incluye:

- Páginas HTML para inicio, paradas, mapa, reportes, login, registro y perfil.
- API REST versionada bajo `/api/v1`.
- Consulta de paradas almacenadas en PostgreSQL.
- Consulta de experiencias y creación de reportes.
- Integración server-side con las APIs públicas de transporte de Montevideo.
- Registro e inicio de sesión con contraseñas protegidas mediante `bcrypt`.
- Emisión de tokens JWT con vencimiento configurable.
- Rate limiting por dirección IP mediante `slowapi`.
- Documentación OpenAPI disponible en `/docs` y `/redoc`.

Actualmente el proyecto **no incluye todavía**:

- Verificación del JWT en los endpoints que crean reportes o consultan datos privados.
- CORS configurado para orígenes externos.
- Service worker, manifest o funcionamiento offline de PWA.
- Rate limiting compartido entre múltiples instancias mediante Redis.
- Suite de tests automatizados en el repositorio.

El frontend y el backend se sirven desde FastAPI, por lo que las llamadas JavaScript usan rutas relativas como `/api/v1/login` y no necesitan CORS en ese despliegue.

## Tecnologías

- Python 3.10 o superior.
- FastAPI y Uvicorn.
- Pydantic.
- SQLAlchemy y PostgreSQL mediante `psycopg`.
- Alembic para migraciones.
- `bcrypt` para el hash de contraseñas.
- PyJWT para emitir tokens JWT.
- `slowapi` para limitar solicitudes.
- `httpx` para consultar servicios externos de transporte.
- Folium, GeoPandas, Pandas y PyProj para datos geográficos.
- HTML, JavaScript y Tailwind CSS mediante CDN.

## Estructura

```text
BondisAPP/
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/                 # Migraciones de la base de datos
├── backend/
│   ├── main.py                   # Aplicación FastAPI, páginas y endpoints
│   ├── database.py               # Engine, sesiones y dependencia get_db
│   ├── stmAPI.py                 # Clientes de APIs de transporte externas
│   ├── updateParadas.py          # Utilidades de actualización de paradas
│   ├── models/                   # Modelos ORM
│   ├── routes/                   # Reservado para rutas separadas
│   └── schemas/                  # Schemas Pydantic
├── frontend/
│   ├── inicio.html
│   ├── login.html
│   ├── signin.html               # Página de registro
│   ├── paradas.html
│   ├── mapa_paradas_montevideo.html
│   ├── reportar.html
│   ├── perfil.html
│   └── static/
│       ├── app.js
│       ├── login.js
│       ├── register.js
│       ├── reportar.js
│       └── styles.css
├── data/                         # Datos auxiliares
├── requirements.txt
└── README.md
```

## Requisitos previos

1. Python 3.10 o superior.
2. PostgreSQL accesible desde el entorno de ejecución.
3. Una base de datos creada para BondisAPP.
4. Credenciales de la API STM si el entorno las requiere.
5. Internet para las fuentes, Tailwind CDN y APIs externas usadas por algunas páginas.

## Instalación local

Desde la raíz del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

En Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

El módulo `backend.database` usa `python-dotenv` para cargar `.env`. Si no está disponible en el entorno, instalarlo con:

```bash
python -m pip install python-dotenv
```

Se recomienda agregarlo a `requirements.txt` si se usa `.env` de forma permanente.

## Configuración de entorno

Crea un archivo `.env` en la raíz del proyecto. No lo publiques ni subas credenciales reales.

### Variables obligatorias

```dotenv
DATABASE_URL=postgresql+psycopg://usuario:contraseña@localhost:5432/bondisapp
JWT_SECRET_KEY=una-clave-larga-y-aleatoria
```

`DATABASE_URL` debe usar el formato de SQLAlchemy. `JWT_SECRET_KEY` se usa para firmar los tokens con HS256 y debe ser distinta entre desarrollo y producción.

### Variables opcionales

```dotenv
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# API STM con token ya obtenido
STM_ACCESS_TOKEN=...

# Alternativa OAuth2 para que el backend obtenga el token
STM_CLIENT_ID=...
STM_CLIENT_SECRET=...
STM_TOKEN_URL=https://mvdapi-auth.montevideo.gub.uy/token
STM_API_BASE_URL=https://api.montevideo.gub.uy/api/transportepublico

# API de arribos
TRANSPORTERESTCLIENT_BASE_URL=https://api.montevideo.gub.uy/transporteRest
```

El cliente STM usa `STM_ACCESS_TOKEN` si existe. Si no existe, intenta OAuth2 con `STM_CLIENT_ID` y `STM_CLIENT_SECRET`.

## Base de datos y migraciones

Las tablas se administran con Alembic. El backend no ejecuta `Base.metadata.create_all`.

Para aplicar las migraciones:

```bash
alembic upgrade head
```

Para crear una migración después de modificar los modelos:

```bash
alembic revision -m "descripcion del cambio"
```

Luego edita la migración y aplícala con `alembic upgrade head`.

La dependencia `get_db` abre una sesión SQLAlchemy por solicitud y la cierra al terminar:

```python
db: Session = Depends(get_db)
```

## Ejecución

Ejecuta Uvicorn desde la raíz, con el entorno virtual activado:

```bash
uvicorn backend.main:app --reload
```

También puedes usar:

```bash
python -m uvicorn backend.main:app --reload
```

URLs locales:

- Aplicación: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

La variable `JWT_SECRET_KEY` debe existir antes de importar `backend.main`; de lo contrario la aplicación se detiene intencionalmente.

## Páginas web

| Método | Ruta | Archivo servido |
| --- | --- | --- |
| `GET` | `/` | `frontend/inicio.html` |
| `GET` | `/paradas` | `frontend/paradas.html` |
| `GET` | `/perfil` | `frontend/perfil.html` |
| `GET` | `/reportar` | `frontend/reportar.html` |
| `GET` | `/login` | `frontend/login.html` |
| `GET` | `/register` | `frontend/signin.html` |
| `GET` | `/mapa_paradas_montevideo` | `frontend/mapa_paradas_montevideo.html` |
| `GET` | `/mapa_paradas_montevideo.html` | Alias del mapa |

Los archivos de `frontend/static` se sirven bajo `/static`. Por ejemplo, el registro carga `/static/register.js` y el login carga `/static/login.js`.

## API REST

Todas las rutas de API usan el prefijo `/api/v1`.

### Paradas

| Método | Ruta | Límite actual | Descripción |
| --- | --- | --- | --- |
| `GET` | `/api/v1/paradas` | 60/minuto/IP | Devuelve todas las paradas locales. |
| `GET` | `/api/v1/paradas/cercanas?lat=...&lon=...&radius=300` | 60/minuto/IP | Busca paradas dentro del radio indicado en metros. |
| `GET` | `/api/v1/paradas/{parada_id}` | 60/minuto/IP | Devuelve una parada por ID. |

Ejemplo de respuesta:

```json
{
  "id": 1,
  "calle_principal": "Av. 18 de Julio",
  "esquina": "Ejemplo",
  "latitud": -34.9011,
  "longitud": -56.1645,
  "activa": true
}
```

### Experiencias

| Método | Ruta | Límite actual | Descripción |
| --- | --- | --- | --- |
| `GET` | `/api/v1/experiencias` | 60/minuto/IP | Devuelve todas las experiencias. |
| `GET` | `/api/v1/experiencias/{num_coche}` | 60/minuto/IP | Busca una experiencia por número de coche. |
| `POST` | `/api/v1/reportar_experiencia` | 30/minuto/IP | Crea una experiencia. |

Formato de creación:

```json
{
  "usuario_id": "00000000-0000-0000-0000-000000000000",
  "comentario": "El viaje fue tranquilo.",
  "calificacion_general": 4,
  "calificacion_limpieza": 5,
  "calificacion_lleno": "moderate",
  "num_coche": 42
}
```

Las calificaciones deben estar entre 1 y 5. `num_coche` debe estar entre 1 y 999. `usuario_id` debe corresponder a un usuario existente.

### Autenticación

| Método | Ruta | Límite actual | Descripción |
| --- | --- | --- | --- |
| `POST` | `/api/v1/register` | 5/minuto/IP | Crea un usuario y devuelve un JWT. |
| `POST` | `/api/v1/login` | 10/minuto/IP | Valida email y contraseña y devuelve un JWT. |

Registro:

```json
{
  "nombre": "Ana Pérez",
  "email": "ana@example.com",
  "password": "una-clave-segura"
}
```

Login:

```json
{
  "email": "ana@example.com",
  "password": "una-clave-segura"
}
```

La respuesta exitosa contiene:

```json
{
  "access_token": "jwt...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "nombre": "Ana Pérez",
    "email": "ana@example.com",
    "fecha_registro": "...",
    "level": 1,
    "exp": 0
  }
}
```

El frontend guarda el token bajo `access_token` y el usuario serializado bajo `user`. Login usa `localStorage` o `sessionStorage` según la opción de mantener la sesión. Registro guarda actualmente la sesión en `localStorage` y redirige a `/perfil`.

El JWT se firma con HS256, incluye el UUID en `sub`, el email y una fecha de expiración. **Emitir el token no equivale todavía a proteger un endpoint:** la verificación de `Authorization: Bearer ...` debe agregarse antes de considerar privados los endpoints de reportes o perfil.

### Transporte externo

Estas rutas funcionan como proxy server-side para no exponer las credenciales del STM al navegador:

| Método | Ruta | Límite actual | Servicio |
| --- | --- | --- | --- |
| `GET` | `/api/v1/transport/montevideo/paradas` | 60/minuto/IP | STM |
| `GET` | `/api/v1/transport/montevideo/arribos/{stop_id}` | 300/minuto/IP | TransporteRest |
| `GET` | `/api/v1/transport/montevideo/buses` | 60/minuto/IP | STM |
| `GET` | `/api/v1/transport/montevideo/busstops` | 60/minuto/IP | STM |

Los errores de los servicios externos se convierten en respuestas `502`.

## Rate limiting

`slowapi` identifica al cliente mediante `get_remote_address` y mantiene los contadores en memoria del proceso actual.

Límites configurados:

```text
Registro                         5/minuto por IP
Login                           10/minuto por IP
Reportar experiencia            30/minuto por IP
Consultas locales y STM         60/minuto por IP
Arribos                         300/minuto por IP
```

Cuando se supera un límite, la API responde con HTTP `429 Too Many Requests`.

Prueba rápida local para login:

```bash
for i in {1..12}; do
  curl -s -o /dev/null -w "Intento $i: %{http_code}\\n" \\
    -X POST http://127.0.0.1:8000/api/v1/login \\
    -H "Content-Type: application/json" \\
    -d '{"email":"prueba@example.com","password":"incorrecta"}'
done
```

Las primeras solicitudes pueden responder `404` o `401` según el usuario; después del límite deben responder `429`.

Este almacenamiento no es compartido entre workers ni instancias de Render. Para producción distribuida se debe configurar un backend compartido, normalmente Redis, y revisar la configuración del proxy para obtener correctamente la IP real.

## Seguridad

- No subir `.env`, contraseñas, tokens, claves del STM ni dumps de la base de datos.
- Mantener `JWT_SECRET_KEY` como secreto de Render y usar una clave larga y aleatoria.
- Las contraseñas se almacenan hasheadas con `bcrypt`, nunca en texto plano.
- Las credenciales de servicios externos se usan únicamente en el backend.
- CORS no vuelve privada una API. Solo controla solicitudes de navegadores desde otros orígenes.
- Una aplicación web pública no puede impedir que alguien replique sus solicitudes HTTP. La protección real debe estar en autenticación, autorización, validación y rate limiting del backend.
- Antes de producción, agregar verificación JWT a los endpoints que escriben datos y asociar el usuario del reporte con el `sub` del token en lugar de confiar en un `usuario_id` enviado por el cliente.

## Despliegue en Render

Configura un Web Service conectado al repositorio.

Build command recomendado:

```bash
pip install -r requirements.txt
```

Start command recomendado:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Variables de entorno mínimas en Render:

```text
DATABASE_URL
JWT_SECRET_KEY
JWT_ACCESS_TOKEN_EXPIRE_MINUTES
```

También agrega las variables STM si las rutas de transporte van a estar habilitadas. Render proporciona HTTPS, requisito necesario para una futura PWA y para proteger las credenciales durante el transporte.

Antes de iniciar el servicio, ejecuta las migraciones como parte del proceso de despliegue o desde un shell del servicio:

```bash
alembic upgrade head
```

No uses `--reload` en producción.

## PWA

La aplicación puede convertirse en PWA porque Render sirve el sitio por HTTPS, pero todavía faltan estos archivos y pasos:

1. Crear un `manifest.json` con nombre, iconos, `start_url` y `display: standalone`.
2. Crear iconos de al menos `192x192` y `512x512`.
3. Crear un service worker y servirlo desde la raíz como `/sw.js` para que tenga alcance sobre toda la aplicación.
4. Agregar `<link rel="manifest" href="/static/manifest.json">` a las páginas.
5. Registrar el service worker desde JavaScript.
6. Diseñar una estrategia de caché que no guarde respuestas privadas, tokens ni formularios de autenticación.

## Pruebas manuales

Comprobar que la aplicación arranca:

```bash
python -m compileall backend
```

Comprobar la API:

```bash
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/docs
curl -i http://127.0.0.1:8000/api/v1/paradas
```

Comprobar registro:

```bash
curl -i -X POST http://127.0.0.1:8000/api/v1/register \\
  -H "Content-Type: application/json" \\
  -d '{"nombre":"Ana Pérez","email":"ana@example.com","password":"una-clave-segura"}'
```

Comprobar el rate limiter usando el bucle de la sección correspondiente y buscar respuestas `429`.

## Desarrollo futuro

- Implementar dependencia de autenticación JWT y autorización por usuario.
- Asociar reportes al usuario autenticado en el backend.
- Configurar CORS únicamente si frontend y backend se despliegan en orígenes diferentes.
- Mover el rate limiting a Redis cuando haya más de un worker o instancia.
- Agregar tests con `pytest` y un entorno de base de datos aislado.
- Implementar manifest, service worker e instalación PWA.
- Añadir manejo uniforme de errores y logging estructurado.
- Separar las rutas en módulos dentro de `backend/routes`.
- Mejorar la carga y actualización de datos de paradas.

## Contribución

Antes de abrir un pull request:

1. Ejecuta `python -m compileall backend`.
2. Verifica que `alembic upgrade head` funcione contra una base de datos de prueba.
3. Prueba los endpoints modificados en `/docs`.
4. Comprueba que no se hayan agregado secretos o archivos generados.
5. Actualiza este README si cambian rutas, variables de entorno o límites.
