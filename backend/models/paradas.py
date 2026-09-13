from typing import List, Optional
from sqlalchemy import create_engine, String, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from backend.database import Base

class Parada(Base):
    __tablename__ = "paradas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    calle_principal: Mapped[str] = mapped_column(String(100), nullable=False)
    esquina: Mapped[str] = mapped_column(String(100), nullable=False)
    latitud: Mapped[float] = mapped_column(nullable=False)
    longitud: Mapped[float] = mapped_column(nullable=False)
    activa: Mapped[bool] = mapped_column(nullable=False, server_default=text("true"))

class parada_omnibus(Base):
    __tablename__ = "paradas_omnibus"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_parada: Mapped[int] = mapped_column(ForeignKey("paradas.id"), nullable=False)
    omnibus: Mapped[str] = mapped_column(String(100), nullable=False)
    consultas: Mapped[int] = mapped_column(nullable=False, server_default=text("0"))
    last_update: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("now()"))