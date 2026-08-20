from pydantic import BaseModel

class Experiencia(BaseModel):
    id: int
    usuario_id: str
    comentario: str
    calificacion_general: int = field(ge=1, le=5)
    calificacion_limpieza: int = field(ge=1, le=5)
    calificacion_lleno: str
    num_coche: int = field(ge=1, le=999)
    fecha_reporte: str
