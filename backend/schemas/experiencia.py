from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field

class Experiencia(BaseModel):
    id: int
    usuario_id: UUID
    comentario: Optional[str] = None
    calificacion_general: int = Field(ge=1, le=5)
    calificacion_limpieza: int = Field(ge=1, le=5)
    calificacion_lleno: str
    num_coche: int = Field(ge=1, le=999)
    fecha_reporte: str

    model_config = {"from_attributes": True}

class ExperienciaCreate(BaseModel):
    usuario_id: UUID
    comentario: Optional[str] = None
    calificacion_general: int = Field(ge=1, le=5)
    calificacion_limpieza: int = Field(ge=1, le=5)
    calificacion_lleno: str
    num_coche: int = Field(ge=1, le=999)
