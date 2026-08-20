from typing import List, Optional
from sqlalchemy import create_engine, String, ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

# Declaramos la base para los modelos: Parada, 
# TODO: Agregar más modelos según sea necesario
class Base(DeclarativeBase):
    pass

class Parada(Base):
    __tablename__ = "paradas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    calle_principal: Mapped[str] = mapped_column(String(100), nullable=False)
    esquina: Mapped[str] = mapped_column(String(100), nullable=False)
    latitud: Mapped[float] = mapped_column(nullable=False)
    longitud: Mapped[float] = mapped_column(nullable=False)
    activa: Mapped[bool] = mapped_column(nullable=False, server_default=text("true"))
