from pydantic import BaseModel

class user(BaseModel):
    id: int
    nombre: str
    email: str
    password: str
    fecha_registro: str