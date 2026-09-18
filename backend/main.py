from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime, timedelta, timezone
import os
import bcrypt
import jwt
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db 
from backend.models.paradas import Parada as ParadaModel
from backend.models.experiencia import reporteExperiencia as ExperienciaModel
from backend.schemas.paradas import Parada
from backend.schemas.experiencia import Experiencia, ExperienciaCreate
from backend.schemas.user import AuthResponse, UserCreate, UserLogin, user
from backend.models.user import user as UserModel
from backend.stmAPI import STMAPIError, stm_client

app = FastAPI()

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
@app.get("/")
async def read_index():
    # Leer el archivo inicio.html y devolverlo como respuesta HTML
    html_content = _read_frontend_html("inicio.html")
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/paradas")
async def read_paradas():
    html_content = _read_frontend_html("paradas.html")
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/perfil")
async def read_perfil():
    html_content = _read_frontend_html("perfil.html")
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/reportar")
async def read_reportar():
    html_content = _read_frontend_html("reportar.html")
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/mapa_paradas_montevideo")
async def read_mapa_paradas():
    # Leer el archivo mapa_paradas_montevideo.html y devolverlo como respuesta HTML
    html_content = _read_frontend_html("mapa_paradas_montevideo.html")

    return HTMLResponse(content=html_content, status_code=200)


@app.get("/mapa_paradas_montevideo.html")
async def read_mapa_paradas_html():
    # Alias para compatibilidad con referencias directas al archivo .html
    html_content = _read_frontend_html("mapa_paradas_montevideo.html")

    return HTMLResponse(content=html_content, status_code=200)

@app.get("/api/v1/paradas", response_model=list[Parada])
async def get_paradas(db: Session = Depends(get_db)):   
    # Lógica para obtener todas las paradas
    paradas = db.query(ParadaModel).all()
    return paradas

@app.get("/api/v1/paradas/{parada_id}", response_model=Parada)
async def get_parada(parada_id: int, db: Session = Depends(get_db)):
    # Lógica para obtener una parada específica por su ID
    parada = db.query(ParadaModel).filter(ParadaModel.id == parada_id).first()
    if not parada:
        raise HTTPException(status_code=404, detail="Parada no encontrada")
    return parada

@app.get("/api/v1/experiencias", response_model=list[Experiencia])
async def get_experiencias(db: Session = Depends(get_db)):
    # Lógica para obtener todas las experiencias
    experiencias = db.query(ExperienciaModel).all()
    return experiencias

@app.get("/api/v1/experiencias/{num_coche}", response_model=Experiencia)
async def get_experiencia(num_coche: int, db: Session = Depends(get_db)):
    # Lógica para obtener una experiencia específica por el número de coche
    experiencia = db.query(ExperienciaModel).filter(ExperienciaModel.num_coche == num_coche).first()
    if not experiencia:
        raise HTTPException(status_code=404, detail="Experiencias no encontradas")
    return experiencia

@app.post("/api/v1/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
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

@app.post("/api/v1/reportar_experiencia", response_model=Experiencia, status_code=status.HTTP_201_CREATED)
async def reportar_experiencia(experiencia: ExperienciaCreate, db: Session = Depends(get_db)):
    # Lógica para reportar la experiencia
    experiencia_db = ExperienciaModel(**experiencia.model_dump())
    db.add(experiencia_db)
    db.commit()
    db.refresh(experiencia_db)
    return experiencia_db

@app.post("/api/v1/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
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


@app.get("/api/v1/transport/montevideo/paradas")
async def get_stm_paradas(query: str | None = None, stop_id: str | None = None):
    try:
        return stm_client.get_stops(query=query, stop_id=stop_id)
    except STMAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

# TODO: Arribos no funciona, revisar la documentación de la API de STM.
@app.get("/api/v1/transport/montevideo/arribos/{stop_id}")
async def get_stm_arrivals(stop_id: str):
    try:
        return stm_client.get_arrivals(stop_id=stop_id)
    except STMAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@app.get("/api/v1/transport/montevideo/buses")
async def get_stm_buses():
    try:
        return stm_client.get_lines()
    except STMAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@app.get("/api/v1/transport/montevideo/busstops")
async def get_stm_busstops():
    try:
        return stm_client.get_busstops()
    except STMAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@app.get("/login")
async def login_page():
    html_content = _read_frontend_html("login.html")
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/register")
async def register_page():
    html_content = _read_frontend_html("signin.html")
    return HTMLResponse(content=html_content, status_code=200)
