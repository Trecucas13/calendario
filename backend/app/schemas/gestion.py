from pydantic import BaseModel
from typing import Optional # Para campos opcionales.
from datetime import datetime # Para campos de fecha y hora.

# Esquemas Pydantic para la validación y serialización de datos de Gestión.

class GestionBase(BaseModel): # Podríamos definir un GestionBase si hay campos comunes que no siempre se incluyen en Create o Response.
    """
    Esquema base para los campos de una gestión.
    No se usa directamente, pero sirve como base para otros esquemas si es necesario.
    """
    registro_id: str # ID del registro base al que se asocia la gestión.
    tipificacion: str # Nombre o código de la tipificación de la gestión.
    comentario: Optional[str] = None # Comentario opcional sobre la gestión.
    id_llamada: Optional[str] = None # ID de la llamada asociada, si aplica.
    usuario: str # Nombre o ID del usuario que registra la gestión.

class GestionCreate(GestionBase): # Hereda de GestionBase o define campos directamente.
    """
    Esquema Pydantic utilizado para crear un nuevo registro de gestión.
    Define los campos esperados en el cuerpo de una solicitud POST.
    """
    # Los campos ya están definidos en GestionBase si se hereda.
    # Si no se hereda de GestionBase, se definirían aquí:
    registro_id: str # ID del registro base (paciente/cliente) al que se asocia esta gestión.
    tipificacion: str # Tipificación de la gestión (ej. "Venta", "No contesta").
    comentario: Optional[str] = None # Comentarios adicionales (opcional).
    id_llamada: Optional[str] = None # ID de la llamada asociada (opcional).
    usuario: str # Usuario que realiza la gestión.
    # Nota: fecha_gestion se suele añadir en el backend (CRUD) al momento de la creación.

class GestionResponse(GestionCreate): # Podría heredar de GestionBase y añadir campos específicos de respuesta.
    """
    Esquema Pydantic para la respuesta al solicitar o crear una gestión.
    Incluye los campos de la gestión creada/obtenida más los campos generados por la base de datos
    como el ID y la fecha de gestión.
    """
    id: str # ID único de la gestión, asignado por la base de datos.
    fecha_gestion: datetime # Fecha y hora en que se registró la gestión.

    class Config:
        """
        Configuración del esquema Pydantic.
        from_attributes = True (anteriormente orm_mode) permite que el modelo Pydantic
        se cree a partir de atributos de un objeto ORM (SQLAlchemy),
        facilitando la serialización directa de los modelos de base de datos.
        """
        from_attributes = True

class GestionHistorico(BaseModel):
    """
    Esquema Pydantic para representar un registro en el historial de gestiones.
    Este esquema combina campos del registro base y de la gestión para mostrar
    una vista enriquecida del historial.
    """
    # Campos del RegistroBase
    tipo_id: str # Tipo de identificación del paciente/registro.
    num_id: str # Número de identificación.
    primer_nombre: str # Primer nombre del paciente/registro.
    segundo_nombre: Optional[str] = None # Segundo nombre (opcional).
    primer_apellido: str # Primer apellido.
    segundo_apellido: Optional[str] = None # Segundo apellido (opcional).
    proceso: str # Proceso asociado al registro base.

    # Campos de la Gestión
    tipificacion: str # Tipificación de la gestión.
    tipo_contacto: str # Tipo de contacto (ej. "EFECTIVO", "NO EFECTIVO").
    comentario: Optional[str] = None # Comentario de la gestión.
    id_llamada: Optional[str] = None # ID de la llamada.
    fecha_gestion: datetime # Fecha de la gestión.
    usuario: str # Usuario que realizó la gestión.

    class Config:
        """
        Configuración del esquema Pydantic.
        from_attributes = True permite la creación del modelo desde atributos de objeto,
        útil si estos datos vienen de un ORM o un objeto con atributos coincidentes.
        """
        from_attributes = True