from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path
import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db 
from backend.models.paradas import Parada
from backend.models.experiencia import Experiencia
from backend.schemas.paradas import Parada, ParadaCreate, ParadaUpdate
from backend.schemas.experiencia import reporteExperiencia

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



@app.post("/api/v1/reportar_experiencia", response_model=reporteExperiencia, status_code=status.HTTP_201_CREATED)
async def reportar_experiencia(experiencia: reporteExperiencia, db: Session = Depends(get_db)):
    # Lógica para reportar la experiencia
    db.add(experiencia)
    db.commit()
    db.refresh(experiencia)
    return experiencia
    pass

@app.post("/api/v1/register", response_model=user, status_code=status.HTTP_201_CREATED)
async def register_user(user: user, db: Session = Depends(get_db)):
    # Lógica para registrar un nuevo usuario
    password_bytes() = user.password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    user.password = hashed_password.decode('utf-8')
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
    pass
