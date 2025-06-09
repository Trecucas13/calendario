from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from app.core.database import Base # Importa la clase Base declarativa de SQLAlchemy.
from datetime import datetime
import uuid

# Modelo SQLAlchemy para la tabla de Gestión.

class Gestion(Base):
    """
    Modelo SQLAlchemy que representa la tabla 'gestion' en la base de datos.

    Esta tabla almacena información sobre las interacciones o gestiones realizadas
    en relación con un registro base (ej. un paciente o cliente).
    """
    __tablename__ = "gestion" # Nombre de la tabla en la base de datos.

    # --- Columnas de la tabla 'gestion' ---
    id = Column(Integer, primary_key=True, default=lambda: str(uuid.uuid4())) # Identificador único de la gestión. Se autogenera un UUID como string por defecto. (Nota: El tipo Integer y un UUID como default pueden ser inconsistentes, considerar String(36) o UUID de SQLAlchemy si el motor lo soporta)

    registro_id = Column(Integer, ForeignKey("registro_base.id")) # Clave foránea que referencia al ID de la tabla 'registro_base'. Vincula la gestión con un registro específico.

    tipificacion = Column(String(100)) # Tipo de gestión o resultado de la interacción (ej. "Venta cerrada", "No interesado", "Llamar más tarde"). Debería idealmente ser una FK a una tabla de tipificaciones.

    comentario = Column(Text) # Campo de texto libre para añadir comentarios o notas sobre la gestión.

    id_llamada = Column(String(100)) # Identificador de la llamada telefónica asociada a esta gestión, si aplica.

    fecha_gestion = Column(DateTime, default=datetime.utcnow) # Fecha y hora en que se realizó o registró la gestión. Se establece la hora UTC actual por defecto.

    usuario = Column(String(100), nullable=True) # Nombre o identificador del usuario/agente que realizó la gestión. Puede ser nulo.

    llave_compuesta = Column(String(100), nullable=True)  # Campo para una llave compuesta, posiblemente para evitar duplicados o para lógicas de negocio específicas. Puede ser nulo.

    # --- Relaciones (si las hubiera definido explícitamente con orm.relationship) ---
    # Ejemplo:
    # registro_base = relationship("RegistroBase", back_populates="gestiones")
    # tipificacion_detalle = relationship("Tipificacion", foreign_keys=[tipificacion_id]) # Si 'tipificacion' fuera un FK a una tabla 'tipificacion'
    # (Actualmente 'tipificacion' es un String, no un FK directo a un modelo Tipificacion en este snippet)
