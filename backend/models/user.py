from uuid import UUID as PyUUID

from sqlalchemy import String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

class Base(DeclarativeBase):
    pass

class user(Base):
    __tablename__ = "users"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=None)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_registro: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("now()"))