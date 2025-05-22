from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from app.core.database import Base
from datetime import datetime
import uuid

class Gestion(Base):
    __tablename__ = "Gestion"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    registro_id = Column(String(36), ForeignKey("RegistroBase.id"))
    tipificacion = Column(String(100))
    comentario = Column(Text)
    id_llamada = Column(String(100))
    fecha_gestion = Column(DateTime, default=datetime.utcnow)
    usuario = Column(String(100))
