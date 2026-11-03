from typing import Optional
from uuid import UUID as PyUUID

from sqlalchemy import DateTime, String, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from backend.database import Base
from datetime import datetime, timedelta, timezone

class reporteExperiencia(Base):
    __tablename__ = "reporte_experiencia"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    comentario: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    calificacion_general: Mapped[int] = mapped_column(nullable=True)
    calificacion_limpieza: Mapped[int] = mapped_column(nullable=True)
    calificacion_lleno: Mapped[str] = mapped_column(nullable=True)    
    num_coche: Mapped[int] = mapped_column(nullable=True)
    fecha_reporte: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("now()"))

class reporteParadaExperiencia(Base):
    __tablename__ = "reporte_parada_experiencia"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    comentario: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    calificacion_general: Mapped[int] = mapped_column(nullable=True)
    calificacion_seguridad: Mapped[int] = mapped_column(nullable=True)
    calificacion_lleno: Mapped[str] = mapped_column(nullable=True)    
    id_parada: Mapped[int] = mapped_column(ForeignKey("paradas.id"), nullable=False)
    fecha_reporte: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))