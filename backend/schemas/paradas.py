from pydantic import BaseModel

class Parada(BaseModel):
    id: int
    calle_principal: str
    esquina: str
    latitud: float
    longitud: float
    activa: bool 

    model_config = {"from_attributes": True}

class parada_omnibus(BaseModel):
    id: int
    id_parada: int
    omnibus: str
    consultas: int
    last_update: str

    model_config = {"from_attributes": True}
