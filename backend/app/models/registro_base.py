from sqlalchemy import Column, String, Integer, Date, DateTime
from app.core.database import Base
from datetime import datetime
import uuid

class RegistroBase(Base):
    __tablename__ = "RegistroBase"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tipo_id = Column(String(10))
    num_id = Column(String(20))
    primer_nombre = Column(String(100))
    segundo_nombre = Column(String(100), nullable=True)
    primer_apellido = Column(String(100))
    segundo_apellido = Column(String(100), nullable=True)
    fecha = Column(Date)
    edad = Column(Integer)
    estado_afiliacion = Column(String(50))
    regimen_afiliacion = Column(String(50))
    telefonos = Column(String(200))
    direccion = Column(String(200))
    municipio = Column(String(100))
    subregion = Column(String(100))
    proceso = Column(String(100))
    fecha_carga = Column(DateTime, default=datetime.utcnow)
    