from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path
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

