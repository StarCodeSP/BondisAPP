from typing import Optional
from uuid import UUID as PyUUID

from sqlalchemy import String, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from database import Base

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

