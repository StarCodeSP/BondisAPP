from typing import List, Optional
from sqlalchemy import create_engine, String, ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

# Declaramos la base para los modelos: Experiencia,
# TODO: Agregar más modelos según sea necesario

class Base(DeclarativeBase):
    pass

class reporteExperiencia(Base):
    __tablename__ = "reporte_experiencia"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    comentario: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    calificacion_general: Mapped[int] = mapped_column(nullable=True)
    calificacion_limpieza: Mapped[int] = mapped_column(nullable=True)
    calificacion_lleno: Mapped[str] = mapped_column(nullable=True)    
    num_coche: Mapped[int] = mapped_column(nullable=True)
    fecha_reporte: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("now()"))

