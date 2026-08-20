from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path
import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db 
from backend.models.paradas import Parada as ParadaModel
from backend.models.experiencia import reporteExperiencia as ExperienciaModel
from backend.schemas.paradas import Parada
from backend.schemas.experiencia import Experiencia
from backend.schemas.user import user
from backend.models.user import user as UserModel

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent

@app.get("/")
async def read_index():
    # Leer el archivo index.html y devolverlo como respuesta HTML
    with open(BASE_DIR / "../frontend/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content, status_code=200)

@app.get("/mapa_paradas_montevideo")
async def read_mapa_paradas():
    # Leer el archivo mapa_paradas_montevideo.html y devolverlo como respuesta HTML
    with open(BASE_DIR / "../frontend/mapa_paradas_montevideo.html", "r", encoding="utf-8") as f:
        html_content = f.read()

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

@app.post("/api/v1/login", response_model=user, status_code=status.HTTP_200_OK)
async def login_user(user: user, db: Session = Depends(get_db)):
    # Lógica para autenticar al usuario
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario o contraseña incorrectos")
    
    password_bytes = user.password.encode('utf-8')
    hashed_password_bytes = db_user.password.encode('utf-8')

    if not bcrypt.checkpw(password_bytes, hashed_password_bytes):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    
    return db_user

@app.post("/api/v1/reportar_experiencia", response_model=Experiencia, status_code=status.HTTP_201_CREATED)
async def reportar_experiencia(experiencia: Experiencia, db: Session = Depends(get_db)):
    # Lógica para reportar la experiencia
    experiencia_db = ExperienciaModel(**experiencia.model_dump())
    db.add(experiencia_db)
    db.commit()
    db.refresh(experiencia_db)
    return experiencia_db
    pass

@app.post("/api/v1/register", response_model=user, status_code=status.HTTP_201_CREATED)
async def register_user(user: user, db: Session = Depends(get_db)):
    # Lógica para registrar un nuevo usuario
    password_bytes = user.password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes)
    user.password = hashed_password.decode('utf-8')
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
    pass


