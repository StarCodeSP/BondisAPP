from pydantic import BaseModel

class Parada(BaseModel):
    id: int
    calle_principal: str
    esquina: str
    latitud: float
    longitud: float
    activa: bool 
