from pydantic import BaseModel

# Esquemas Pydantic para los datos de Tipificacion.

class TipificacionBase(BaseModel):
    """
    Esquema base para los datos de una tipificación.
    Contiene los campos comunes que se utilizan tanto para la creación
    como para la representación de una tipificación.
    """
    nombre: str # Nombre único de la tipificación (ej. "Venta Cruzada", "No Contesta").
    ranking: int # Valor numérico para ordenar o priorizar tipificaciones (menor ranking puede ser más prioritario).
    tipo_contacto: str # Categoría general del contacto (ej. "EFECTIVO", "NO EFECTIVO", "NO CONTACTADO").

class TipificacionCreate(TipificacionBase):
    """
    Esquema Pydantic utilizado para crear una nueva tipificación.
    Hereda todos los campos de `TipificacionBase`.
    Actualmente no añade campos adicionales, ya que `TipificacionBase`
    contiene todos los necesarios para la creación.
    """
    # No se necesitan campos adicionales más allá de los de TipificacionBase.
    pass

class TipificacionResponse(TipificacionBase):
    """
    Esquema Pydantic para la respuesta al solicitar o crear una tipificación.
    Incluye todos los campos de `TipificacionBase` más el ID asignado por la base de datos.
    """
    id: int # ID único de la tipificación, generado por la base de datos.

    class Config:
        """
        Configuración del esquema Pydantic.
        from_attributes = True (anteriormente orm_mode) permite que el modelo
        Pydantic se cree a partir de atributos de un objeto ORM (SQLAlchemy),
        facilitando la serialización de los modelos de base de datos.
        """
        from_attributes = True

# Si se necesitara un esquema específico para leer desde la BD que sea diferente de TipificacionResponse,
# se podría definir aquí, por ejemplo, TipificacionInDBBase o Tipificacion.
# class TipificacionInDBBase(TipificacionBase):
#     id: int
#     # otros campos específicos de la BD si los hubiera
#
#     class Config:
#         from_attributes = True
#
# class Tipificacion(TipificacionInDBBase):
#     # campos adicionales si fueran necesarios para la representación completa
#     pass
