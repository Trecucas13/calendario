from sqlalchemy import Column, String, Integer
from app.core.database import Base
import uuid

class Tipificacion(Base):
    __tablename__ = "Tipificaciones"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), unique=True)
    ranking = Column(Integer)
    tipo_contacto = Column(String(50))  # "EFECTIVO", "NO EFECTIVO", "NO CONTACTADO"
