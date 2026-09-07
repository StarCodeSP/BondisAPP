# BondisAPP

Aplicación web colaborativa para consultar paradas de ómnibus en Montevideo y compartir experiencias de viaje. El proyecto combina una API REST construida con FastAPI, persistencia mediante SQLAlchemy/PostgreSQL y una interfaz HTML estática.

> TODO: Actualizar README, no demuestra el estado actual de la aplicación 

## Funcionalidades

- Visualización del mapa de paradas de Montevideo mediante `mapa_paradas_montevideo.html`.
- Consulta de todas las paradas o de una parada concreta.
- Consulta de experiencias reportadas o de una experiencia por número de coche.
- Registro de usuarios con contraseña almacenada mediante `bcrypt`.
- Inicio de sesión con email y contraseña.
- Creación de reportes de experiencia con calificaciones de 1 a 5.
- Pantallas HTML para inicio, paradas, reportes y perfil.

## Tecnologías

- Python 3.10 o superior
- FastAPI y Uvicorn
- Pydantic
- SQLAlchemy
- PostgreSQL mediante `psycopg`
- `bcrypt` para el hash de contraseñas
- Folium, GeoPandas, Pandas y PyProj para trabajar con datos geográficos
- HTML, JavaScript y Tailwind CSS mediante CDN en el frontend

## Estructura del proyecto

```text
BondisAPP/
├── backend/
│   ├── main.py                 # Aplicación FastAPI y endpoints
│   ├── database.py             # Conexión, sesión y Base de SQLAlchemy
│   ├── stmAPI.py               # Integración relacionada con datos STM
│   ├── models/                 # Modelos ORM: users, paradas y reportes
│   └── schemas/                # Modelos Pydantic de entrada y salida
├── frontend/
│   ├── inicio.html             # Página principal
│   ├── paradas.html            # Paradas y mapa embebido
│   ├── mapa_paradas_montevideo.html
│   ├── reportar.html            # Formulario visual de reportes
│   ├── perfil.html
│   └── static/                 # Archivos estáticos reservados
├── v_uptu_paradas.dbf         # Fuente de datos de paradas
├── requirements.txt
└── README.md
```

## Requisitos previos

1. Python 3.10 o superior.
2. PostgreSQL accesible desde el entorno donde se ejecuta la aplicación.
3. Una base de datos creada para BondisAPP.
4. Conexión a Internet para cargar Tailwind CSS y las fuentes usadas por algunas páginas.

El backend importa `python-dotenv` para leer el archivo `.env`. Esta dependencia no aparece actualmente en `requirements.txt`, por lo que debe instalarse explícitamente hasta que se agregue a ese archivo.

## Instalación

Desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install python-dotenv
```

En Windows, la activación del entorno virtual es:

```powershell
.venv\Scripts\Activate.ps1
```

## Configuración

Crea un archivo `.env` en la raíz del proyecto. `backend/database.py` lo busca exactamente allí:

```dotenv
DATABASE_URL=postgresql+psycopg://usuario:contraseña@localhost:5432/bondisapp
```

La URL debe usar el formato de SQLAlchemy. Por ejemplo, si PostgreSQL corre en el puerto por defecto:

```dotenv
DATABASE_URL=postgresql+psycopg://bondisapp:bondisapp@localhost:5432/bondisapp
```

No publiques el archivo `.env` ni incluyas contraseñas reales en el repositorio.

## Ejecución

Ejecuta Uvicorn desde la raíz del repositorio, con el entorno virtual activado:

```bash
uvicorn backend.main:app --reload
```

La aplicación quedará disponible en:

- Interfaz: `http://127.0.0.1:8000/`
- Documentación Swagger: `http://127.0.0.1:8000/docs`
- Documentación alternativa: `http://127.0.0.1:8000/redoc`

También se puede iniciar con:

```bash
python -m uvicorn backend.main:app --reload
```

Al importar `backend.main`, SQLAlchemy ejecuta `Base.metadata.create_all(bind=engine)`. Esto crea las tablas que falten, pero no reemplaza un sistema de migraciones para cambios posteriores del esquema.

## API

Todas las rutas de la API usan el prefijo `/api/v1`.

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/api/v1/paradas` | Devuelve todas las paradas. |
| `GET` | `/api/v1/paradas/{parada_id}` | Devuelve una parada por ID. Responde `404` si no existe. |
| `GET` | `/api/v1/experiencias` | Devuelve todos los reportes. |
| `GET` | `/api/v1/experiencias/{num_coche}` | Busca un reporte por número de coche. Responde `404` si no existe. |
| `POST` | `/api/v1/register` | Registra un usuario. Responde `409` si el email ya existe. |
| `POST` | `/api/v1/login` | Verifica las credenciales de un usuario. |
| `POST` | `/api/v1/reportar_experiencia` | Crea un reporte de experiencia. |

### Formato de paradas

Una parada contiene:

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

### Registro

`POST /api/v1/register` acepta:

```json
{
	"nombre": "Ana Pérez",
	"email": "ana@example.com",
	"password": "una-clave-segura"
}
```

La respuesta incluye el UUID, nombre, email y fecha de registro, pero no devuelve la contraseña.

### Login

`POST /api/v1/login` acepta el mismo email y contraseña:

```json
{
	"email": "ana@example.com",
	"password": "una-clave-segura"
}
```

Una credencial inexistente responde `404` y una contraseña incorrecta responde `401`. Actualmente el login no genera tokens ni mantiene una sesión autenticada.

### Reportar una experiencia

`POST /api/v1/reportar_experiencia` acepta:

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

Las calificaciones y `num_coche` se validan con Pydantic: las calificaciones deben estar entre 1 y 5, y el número de coche entre 1 y 999. `usuario_id` debe corresponder a un usuario existente para que la relación con PostgreSQL sea válida.

## Páginas web

FastAPI sirve estas rutas:

| Ruta | Archivo |
| --- | --- |
| `/` | `frontend/inicio.html` |
| `/paradas` | `frontend/paradas.html` |
| `/perfil` | `frontend/perfil.html` |
| `/reportar` | `frontend/reportar.html` |
| `/mapa_paradas_montevideo` | `frontend/mapa_paradas_montevideo.html` |
| `/mapa_paradas_montevideo.html` | Alias del mapa |

`frontend/index.html` existe como archivo independiente, pero no es la página que devuelve la ruta `/` cuando se ejecuta FastAPI. El backend tampoco monta actualmente `frontend/static` como directorio estático; las páginas contienen la mayor parte de sus estilos y scripts en línea.

## Estado y próximos pasos

- Conectar las acciones del frontend con los endpoints de la API.
- Servir correctamente CSS, JavaScript e imágenes desde `frontend/static`.
- Implementar autenticación con tokens y proteger los endpoints que requieren usuario.
- Añadir migraciones de base de datos, por ejemplo con Alembic.
- Añadir tests automatizados para API, validaciones y conexión a PostgreSQL.
- Completar la carga o sincronización de los datos del archivo `.dbf`.
- Reemplazar los datos de demostración de las pantallas por datos obtenidos del backend.
- Añadir validaciones de formato de email, errores de base de datos y manejo uniforme de excepciones.

## Desarrollo y colaboración

Antes de abrir un pull request, verifica al menos que la aplicación arranque con un `DATABASE_URL` válido y revisa la documentación interactiva en `/docs`. No subas `.env`, credenciales, dumps de la base de datos ni archivos generados.