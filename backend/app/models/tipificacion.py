from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship # Necesario si se definen relaciones inversas.
from app.core.database import Base # Importa la clase Base declarativa de SQLAlchemy.
import uuid # Aunque uuid no se usa directamente en las columnas aquí, es bueno mantenerlo si otros modelos lo usan para defaults.

# Modelo SQLAlchemy para la tabla de Tipificacion.

class Tipificacion(Base):
    """
    Modelo SQLAlchemy que representa la tabla 'tipificacion' en la base de datos.

    Esta tabla almacena los diferentes tipos de resultados o categorías que puede
    tener una gestión o interacción (ej. "Venta exitosa", "No interesado", "Llamada cortada").
    Incluye un sistema de ranking para priorizar o calificar las tipificaciones y un
    tipo de contacto para agruparlas.
    """
    __tablename__ = "tipificacion" # Nombre de la tabla en la base de datos.

    # --- Columnas de la tabla 'tipificacion' ---
    id = Column(Integer, primary_key=True, default=lambda: str(uuid.uuid4())) # Identificador único de la tipificación. (Nota: El tipo Integer y un UUID como default pueden ser inconsistentes, considerar String(36) o UUID de SQLAlchemy si el motor lo soporta)

    nombre = Column(String(100), unique=True) # Nombre único de la tipificación (ej. "Contacto Efectivo - Venta").

    ranking = Column(Integer) # Ranking numérico para la tipificación. Un menor ranking puede indicar mayor prioridad o éxito.

    tipo_contacto = Column(String(50))  # Categoría general del contacto (ej. "EFECTIVO", "NO EFECTIVO", "NO CONTACTADO"). Ayuda a agrupar tipificaciones.

    # --- Relaciones (si las hubiera definido explícitamente con orm.relationship) ---
    # Si una tipificación puede estar asociada a muchas gestiones:
    # gestiones = relationship("Gestion", back_populates="tipificacion_detalle")
    # Para que esto funcione, el modelo Gestion necesitaría una columna `tipificacion_id` como ForeignKey
    # y una relación `tipificacion_detalle = relationship("Tipificacion", back_populates="gestiones")`.
    # (Actualmente, el modelo Gestion tiene un campo `tipificacion` de tipo String,
    # lo que sugiere que el nombre de la tipificación se guarda directamente allí,
    # en lugar de un ID foráneo. Esto es una forma de denormalización o una simplificación
    # si no se necesita una tabla de tipificación estrictamente normalizada con FKs.)
