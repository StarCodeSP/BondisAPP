from typing import List, Optional
from sqlalchemy import create_engine, String, ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

class Base(DeclarativeBase):
    pass

class user(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_registro: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("now()"))