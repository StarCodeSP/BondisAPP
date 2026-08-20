from typing import List, Optional
from sqlalchemy import create_engine, String, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from database import Base

class Parada(Base):
    __tablename__ = "paradas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    calle_principal: Mapped[str] = mapped_column(String(100), nullable=False)
    esquina: Mapped[str] = mapped_column(String(100), nullable=False)
    latitud: Mapped[float] = mapped_column(nullable=False)
    longitud: Mapped[float] = mapped_column(nullable=False)
    activa: Mapped[bool] = mapped_column(nullable=False, server_default=text("true"))
