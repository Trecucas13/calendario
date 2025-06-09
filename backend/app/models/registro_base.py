from sqlalchemy import Column, String, Integer, Date, DateTime
from sqlalchemy.orm import relationship # Necesario para definir relaciones
from app.core.database import Base # Importa la clase Base declarativa de SQLAlchemy.
from datetime import datetime
import uuid # Aunque uuid no se usa directamente en las columnas aquí, es bueno mantenerlo si otros modelos lo usan para defaults.

# Modelo SQLAlchemy para la tabla de RegistroBase.

class RegistroBase(Base):
    """
    Modelo SQLAlchemy que representa la tabla 'registro_base' en la base de datos.

    Esta tabla almacena información fundamental de entidades como pacientes,
    clientes, etc., sobre los cuales se realizarán gestiones.
    """
    __tablename__ = "registro_base" # Nombre de la tabla en la base de datos.

    # --- Columnas de la tabla 'registro_base' ---
    id = Column(Integer, primary_key=True, autoincrement=True) # Identificador único del registro, autoincremental.

    tipo_id = Column(String(10)) # Tipo de documento de identidad (ej. "CC", "TI", "NIT").
    num_id = Column(String(20)) # Número del documento de identidad.

    primer_nombre = Column(String(100)) # Primer nombre de la persona o entidad.
    segundo_nombre = Column(String(100), nullable=True) # Segundo nombre, puede ser nulo.
    primer_apellido = Column(String(100)) # Primer apellido.
    segundo_apellido = Column(String(100), nullable=True) # Segundo apellido, puede ser nulo.

    fecha = Column(Date, nullable=True) # Fecha relevante, como fecha de nacimiento. Puede ser nula.
    edad = Column(Integer) # Edad de la persona.

    estado_afiliacion = Column(String(50)) # Estado de afiliación (ej. "Activo", "Inactivo").
    regimen_afiliacion = Column(String(50)) # Régimen al que está afiliado (ej. "Contributivo", "Subsidiado").

    telefonos = Column(String(200)) # Números de teléfono de contacto, podría almacenar varios separados por comas.
    direccion = Column(String(200)) # Dirección de residencia.
    municipio = Column(String(100)) # Municipio de residencia.
    subregion = Column(String(100)) # Subregión geográfica.

    proceso = Column(String(100)) # Nombre o identificador del proceso al que pertenece este registro.

    fecha_carga = Column(DateTime, default=datetime.utcnow, nullable=True)  # Fecha y hora en que se cargó o creó el registro en el sistema. Por defecto UTC actual.

    # Los siguientes campos parecen ser denormalizados o calculados, relacionados con las gestiones.
    # Considerar si deben estar aquí o ser calculados dinámicamente.
    mejor_gestion = Column(String(100), nullable=True)  # Almacena la tipificación de la "mejor" gestión asociada a este registro.
    asesor = Column(String(100), nullable=True)  # Asesor que realizó la (última/mejor) gestión.
    tipo_gestion = Column(String(50), nullable=True)  # Tipo de la (última/mejor) gestión (ej. "EFECTIVO" o "NO EFECTIVO").
    fecha_gestion = Column(DateTime, default=datetime.utcnow, nullable=True)  # Fecha de la (última/mejor) gestión.

    mes  = Column(String(20), nullable=True)  # Mes de la fecha de carga o de alguna fecha relevante para agrupación.
    cantidad_gestiones = Column(Integer, default=0)  # Contador de cuántas gestiones tiene asociadas este registro.

    # --- Relaciones ---
    # Define la relación uno-a-muchos con la tabla Gestion.
    # Un RegistroBase puede tener muchas Gestiones.
    # gestiones = relationship("Gestion", back_populates="registro_base") # 'back_populates' debe coincidir con el nombre de la relación en el modelo Gestion.
    # Para que esto funcione, el modelo Gestion necesitaría:
    # registro_base = relationship("RegistroBase", back_populates="gestiones")
    # Y el ForeignKey en Gestion.registro_id ya está definido.
    # (Actualmente, la relación no está definida explícitamente con `relationship` en el código proporcionado,
    # pero el ForeignKey sí existe en el modelo Gestion)