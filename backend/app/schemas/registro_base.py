from pydantic import BaseModel
from typing import Optional # Para campos opcionales.
from datetime import date, datetime # Para tipos de fecha y fecha-hora.

# Esquemas Pydantic para los datos de RegistroBase.

# Nota: El prefijo "✅ Schema para..." en comentarios originales se ha mantenido donde aplicaba.

class RegistroBaseBase(BaseModel): # Esquema base con campos comunes
    """
    Esquema base para `RegistroBase` con campos comunes que se esperan
    tanto en la creación como en la respuesta.
    """
    tipo_id: str # Tipo de identificación (ej. CC, TI).
    num_id: int # Número de identificación. (Considerar cambiar a str si puede tener ceros a la izquierda o caracteres no numéricos).
    primer_nombre: str # Primer nombre del titular del registro.
    segundo_nombre: Optional[str] = None # Segundo nombre (opcional).
    primer_apellido: str # Primer apellido.
    segundo_apellido: Optional[str] = None # Segundo apellido (opcional).
    fecha: date # Fecha relevante (ej. fecha de nacimiento).
    edad: int # Edad.
    estado_afiliacion: str # Estado de afiliación (ej. Activo, Retirado).
    regimen_afiliacion: str # Régimen de afiliación (ej. Contributivo, Subsidiado).
    telefonos: str # Números de teléfono de contacto.
    direccion: str # Dirección de residencia.
    municipio: str # Municipio de residencia.
    subregion: str # Subregión geográfica.
    proceso: str # Proceso al que pertenece el registro (ej. MDE202301).
    # Campos relacionados a la gestión que parecen estar denormalizados o ser parte de la carga inicial:
    tipificacion: str # Tipificación de la gestión asociada (si aplica durante la creación del registro base).
    tipo_gestion: Optional[str] = None # Tipo de gestión (ej. EFECTIVO), opcional.
    usuario: Optional[str] = None  # Usuario que realizó la gestión (si aplica en este contexto), opcional.
    fecha_gestion: Optional[datetime] = None # Fecha de la gestión (si aplica), opcional.

# ✅ Schema para creación individual
class RegistroBaseCreate(RegistroBaseBase): # Hereda de RegistroBaseBase
    """
    Esquema Pydantic utilizado para crear un nuevo `RegistroBase`.
    Hereda todos los campos de `RegistroBaseBase`.
    No añade campos adicionales, asumiendo que `RegistroBaseBase` ya contiene todo lo necesario para la creación.
    """
    pass # No necesita campos adicionales, hereda de RegistroBaseBase.

# ✅ Schema para respuesta individual
class RegistroBaseResponse(RegistroBaseBase): # Hereda de RegistroBaseBase
    """
    Esquema Pydantic para la respuesta al solicitar o crear un `RegistroBase`.
    Incluye todos los campos de `RegistroBaseBase` más campos adicionales que se
    generan o se obtienen de la base de datos.
    """
    id: int # ID único del registro base, asignado por la base de datos.
    fecha_carga: Optional[datetime] = None  # Fecha y hora en que se cargó el registro.
    comentario: Optional[str] = None  # Comentario opcional asociado a la gestión o registro.
    mes: Optional[str] = None  # Mes asociado al registro (ej. mes de carga o de la fecha de gestión).
    id_llamada: Optional[int] = None  # ID de la llamada asociada (si aplica), opcional. (Nota: el tipo era int, en Gestion es str)
    cantidad_gestiones: Optional[int] = None  # Número de gestiones asociadas a este registro.
    mejor_gestion: Optional[str] = None  # Descripción de la mejor gestión asociada.
    # `tipificacion` ya está en RegistroBaseBase, pero aquí es Optional, lo cual podría ser intencional si puede no tenerla en la respuesta.
    tipificacion: Optional[str] = None # Tipificación asociada (puede ser diferente de la de creación o nula).
    asesor: Optional[str] = None  # Asesor asociado a la (mejor/última) gestión.
    # `tipo_gestion`, `usuario`, `fecha_gestion` ya están en RegistroBaseBase, pero aquí son Optional,
    # lo cual es coherente si no siempre están presentes en la respuesta.

    class Config:
        """
        Configuración del esquema Pydantic.
        from_attributes = True permite que el modelo Pydantic se cree a partir
        de atributos de un objeto ORM (SQLAlchemy).
        """
        from_attributes = True

# ✅ Schema extendido con mejor gestión
class MejorGestion(BaseModel):
    """
    Esquema Pydantic para representar la información detallada de la "mejor gestión"
    asociada a un registro base.
    """
    tipificacion: str # Nombre de la tipificación de la mejor gestión.
    tipo_contacto: str # Tipo de contacto de la mejor gestión (ej. EFECTIVO).
    usuario: str # Usuario que realizó la mejor gestión.
    fecha_gestion: str # Fecha de la mejor gestión (como string, considerar datetime si es más apropiado).
    mes: str # Mes en que se realizó la mejor gestión.
    cantidad: int # Cantidad de gestiones (podría referirse a la cantidad total para ese registro o un subconjunto).

class RegistroConGestion(BaseModel):
    """
    Esquema Pydantic para representar un `RegistroBase` junto con la información
    detallada de su "mejor gestión".
    """
    # Campos del RegistroBase
    id: int # ID del registro base.
    tipo_id: int # Tipo de identificación. (Nota: en RegistroBaseBase es str)
    num_id: str # Número de identificación.
    primer_nombre: str
    segundo_nombre: Optional[str]
    primer_apellido: str
    segundo_apellido: Optional[str]
    fecha: date
    edad: int
    estado_afiliacion: str
    regimen_afiliacion: str
    telefonos: str
    direccion: str
    municipio: str
    subregion: str
    proceso: str
    # Campo anidado para la mejor gestión
    mejor_gestion: MejorGestion # Objeto anidado con los detalles de la mejor gestión.

    class Config:
        """
        Configuración del esquema Pydantic.
        from_attributes = True permite la creación desde atributos de objeto.
        """
        from_attributes = True
