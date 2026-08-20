from uuid import UUID

from pydantic import BaseModel

class UserCreate(BaseModel):
    nombre: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class user(BaseModel):
    id: UUID
    nombre: str
    email: str
    fecha_registro: str

    model_config = {"from_attributes": True}