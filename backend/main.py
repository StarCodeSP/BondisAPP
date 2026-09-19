from fastapi import Depends, FastAPI, status, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime, timedelta, timezone
import os
import bcrypt
import jwt
from sqlalchemy.orm import Session
from sqlalchemy import func
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.database import Base, engine, get_db 
from backend.models.paradas import Parada as ParadaModel
from backend.models.experiencia import reporteExperiencia as ExperienciaModel
from backend.schemas.paradas import Parada
from backend.schemas.experiencia import Experiencia, ExperienciaCreate
from backend.schemas.user import AuthResponse, UserCreate, UserLogin, user
from backend.models.user import user as UserModel
from backend.stmAPI import STMAPIError, stm_client, transporteRest_client

app = FastAPI(
    title="BondisAPP",
    description="La primera app colaborativa del transporte publico en Uruguay.",
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded, 
    _rate_limit_exceeded_handler,
)

# Las tablas se manejan con Alembic; no se crean acá manualmente.
# Base.metadata.create_all(bind=engine)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY no está configurada")


def _create_access_token(db_user: UserModel) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(db_user.id),
        "email": db_user.email,
        "exp": expires_at,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def _read_frontend_html(filename: str) -> str:
    html_path = FRONTEND_DIR / filename
    if not html_path.exists():
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {filename}")
    return html_path.read_text(encoding="utf-8")

 
app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")

# TODO: Agregar manejo de errores y excepciones
@app.get("/", summary="Página de inicio")
async def read_index():
    # Leer el archivo inicio.html y devolverlo como respuesta HTML
    html_content = _read_frontend_html("inicio.html")
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/paradas", summary="Página de paradas")
async def read_paradas():
    html_content = _read_frontend_html("paradas.html")
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/perfil", summary="Página de perfil")
async def read_perfil():
    html_content = _read_frontend_html("perfil.html")
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/reportar", summary="Página de reportar experiencia")
async def read_reportar():
    html_content = _read_frontend_html("reportar.html")
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/mapa_paradas_montevideo", summary="Mapa de paradas")
async def read_mapa_paradas():
    # Leer el archivo mapa_paradas_montevideo.html y devolverlo como respuesta HTML
    html_content = _read_frontend_html("mapa_paradas_montevideo.html")

    return HTMLResponse(content=html_content, status_code=200)


@app.get("/mapa_paradas_montevideo.html", summary="Mapa de paradas (alias)")
async def read_mapa_paradas_html():
    # Alias para compatibilidad con referencias directas al archivo .html
    html_content = _read_frontend_html("mapa_paradas_montevideo.html")

    return HTMLResponse(content=html_content, status_code=200)

@app.get("/api/v1/paradas", summary="Obtener todas las paradas", response_model=list[Parada])
@limiter.limit("60/minute")
async def get_paradas(request: Request, db: Session = Depends(get_db)):   
    # Lógica para obtener todas las paradas
    paradas = db.query(ParadaModel).all()
    return paradas

@app.get("/api/v1/paradas/cercanas", summary="Obtener paradas cercanas a una ubicación", response_model=list[Parada])
@limiter.limit("60/minute")
async def get_paradas_cercanas(request: Request, lat: float, lon: float, radius: float = 300, db: Session = Depends(get_db)):
    radio_tierra_metros = 6371000

    # Ecuación de Haversine para calcular la distancia entre dos puntos geográficos
    distancia = (
        radio_tierra_metros * func.acos(
            func.cos(func.radians(lat)) *
            func.cos(func.radians(ParadaModel.latitud)) *
            func.cos(func.radians(ParadaModel.longitud) - func.radians(lon)) +
            func.sin(func.radians(lat)) *
            func.sin(func.radians(ParadaModel.latitud))
        )
    )

    # DB calcula la distancia y filtra las paradas dentro del radio especificado
    paradas_cercanas = db.query(ParadaModel).filter(distancia <= radius).order_by(distancia).all()
    
    return paradas_cercanas

@app.get("/api/v1/paradas/{parada_id}", summary="Obtener una parada específica", response_model=Parada)
@limiter.limit("60/minute")
async def get_parada(request: Request, parada_id: int, db: Session = Depends(get_db)):
    # Lógica para obtener una parada específica por su ID
    parada = db.query(ParadaModel).filter(ParadaModel.id == parada_id).first()
    if not parada:
        raise HTTPException(status_code=404, detail="Parada no encontrada")
    return parada

@app.get("/api/v1/experiencias", summary="Obtener todas las experiencias", response_model=list[Experiencia])
@limiter.limit("60/minute")
async def get_experiencias(request: Request, db: Session = Depends(get_db)):
    # Lógica para obtener todas las experiencias
    experiencias = db.query(ExperienciaModel).all()
    return experiencias

@app.get("/api/v1/experiencias/{num_coche}", summary="Obtener experiencias según el número de coche", response_model=Experiencia)
@limiter.limit("60/minute")
async def get_experiencia(request: Request, num_coche: int, db: Session = Depends(get_db)):
    # Lógica para obtener una experiencia específica por el número de coche
    experiencia = db.query(ExperienciaModel).filter(ExperienciaModel.num_coche == num_coche).first()
    if not experiencia:
        raise HTTPException(status_code=404, detail="Experiencias no encontradas")
    return experiencia

@app.post("/api/v1/login", summary="Iniciar sesión", response_model=AuthResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def login_user(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    # Lógica para autenticar al usuario
    db_user = db.query(UserModel).filter(UserModel.email == credentials.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario o contraseña incorrectos")
    
    password_bytes = credentials.password.encode('utf-8')
    hashed_password_bytes = db_user.password.encode('utf-8')

    if not bcrypt.checkpw(password_bytes, hashed_password_bytes):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    
    return {
        "access_token": _create_access_token(db_user),
        "token_type": "bearer",
        "user": db_user,
    }

@app.post("/api/v1/reportar_experiencia", summary="Reportar una nueva experiencia", response_model=Experiencia, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def reportar_experiencia(request: Request, experiencia: ExperienciaCreate, db: Session = Depends(get_db)):
    # Lógica para reportar la experiencia
    experiencia_db = ExperienciaModel(**experiencia.model_dump())
    db.add(experiencia_db)
    db.commit()
    db.refresh(experiencia_db)
    return experiencia_db

@app.post("/api/v1/register", summary="Registrar un nuevo usuario", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register_user(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    # Lógica para registrar un nuevo usuario
    if db.query(UserModel).filter(UserModel.email == user_data.email).first():
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    password_bytes = user_data.password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    user_db = UserModel(
        nombre=user_data.nombre,
        email=user_data.email,
        password=hashed_password.decode('utf-8'),
    )
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return {
        "access_token": _create_access_token(user_db),
        "token_type": "bearer",
        "user": user_db,
    }


@app.get("/api/v1/transport/montevideo/paradas", summary="Obtener todas las paradas (API IMM)")
@limiter.limit("60/minute")
async def get_stm_paradas(request: Request, query: str | None = None, stop_id: str | None = None):
    try:
        return stm_client.get_stops(query=query, stop_id=stop_id)
    except STMAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@app.get("/api/v1/transport/montevideo/arribos/{stop_id}", summary="Obtener arribos a una parada (API IMM TransporteRest)")
@limiter.limit("300/minute")
async def get_stm_arrivals(request: Request, stop_id: str):
    try:
        return transporteRest_client.nextAtBusstop(busstop_id=stop_id)
    except STMAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@app.get("/api/v1/transport/montevideo/buses", summary="Obtener líneas de transporte (API IMM)")
@limiter.limit("60/minute")
async def get_stm_buses(request: Request):
    try:
        return stm_client.get_lines()
    except STMAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@app.get("/login", summary="Página de inicio de sesión")
async def login_page():
    html_content = _read_frontend_html("login.html")
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/register", summary="Página de registro")
async def register_page():
    html_content = _read_frontend_html("signin.html")
    return HTMLResponse(content=html_content, status_code=200)

