from sqlalchemy import Column, String, Integer, Date, DateTime
from app.core.database import Base
from datetime import datetime
import uuid

class RegistroBase(Base):
    __tablename__ = "registro_base"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_id = Column(String(10))
    num_id = Column(String(20))
    primer_nombre = Column(String(100))
    segundo_nombre = Column(String(100), nullable=True)
    primer_apellido = Column(String(100))
    segundo_apellido = Column(String(100), nullable=True)
    fecha = Column(Date, nullable=True)
    edad = Column(Integer)
    estado_afiliacion = Column(String(50))
    regimen_afiliacion = Column(String(50))
    telefonos = Column(String(200))
    direccion = Column(String(200))
    municipio = Column(String(100))
    subregion = Column(String(100))
    proceso = Column(String(100))
    fecha_carga = Column(DateTime, default=datetime.utcnow, nullable=True)  # Fecha de carga del registro
    mejor_gestion = Column(String(100), nullable=True)  # Mejor gestión asociada
    asesor = Column(String(100), nullable=True)  # Asesor que realizó la gestión
    tipo_gestion = Column(String(50), nullable=True)  # Tipo de gestión (EFECTIVO o NO EFECTIVO)
    fecha_gestion = Column(DateTime, default=datetime.utcnow, nullable=True)  # Fecha de la gestión
    mes  = Column(String(20), nullable=True)  # Mes de la fecha de carga
    cantidad_gestiones = Column(Integer, default=0)  # Cantidad de gestiones asociadas
  