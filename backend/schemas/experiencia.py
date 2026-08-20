from pydantic import BaseModel, Field

class Experiencia(BaseModel):
    id: int
    usuario_id: str
    comentario: str
    calificacion_general: int = Field(ge=1, le=5)
    calificacion_limpieza: int = Field(ge=1, le=5)
    calificacion_lleno: str
    num_coche: int = Field(ge=1, le=999)
    fecha_reporte: str
