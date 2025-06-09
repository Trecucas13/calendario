from sqlalchemy.orm import Session
from app.models.tipificacion import Tipificacion
from app.schemas.tipificacion import TipificacionBase

# Funciones CRUD para la tipificación de gestiones o interacciones.

def crear_tipificacion(db: Session, data: TipificacionBase):
    """
    Crea un nuevo registro de tipificación en la base de datos.

    Las tipificaciones se utilizan para categorizar las gestiones o interacciones
    (ej. "Contacto efectivo", "No contesta", "Información errónea").
    Pueden tener un ranking para priorizar o definir la "mejor" gestión.

    Args:
        db (Session): La sesión de base de datos SQLAlchemy.
        data (TipificacionBase): El esquema Pydantic con los datos para crear la tipificación.
                                 Debe incluir `nombre`, `descripcion`, `ranking`, `tipo_contacto`.

    Returns:
        Tipificacion: El objeto de modelo SQLAlchemy `Tipificacion` recién creado y guardado.
    """
    nueva_tipificacion = Tipificacion(**data.dict()) # Desempaqueta los datos del esquema Pydantic.
    db.add(nueva_tipificacion) # Añade el nuevo objeto a la sesión.
    db.commit() # Confirma la transacción.
    db.refresh(nueva_tipificacion) # Refresca el objeto con datos de la BD.
    return nueva_tipificacion # Retorna el objeto creado.

def listar_tipificaciones(db: Session):
    """
    Obtiene una lista de todas las tipificaciones existentes, ordenadas por su ranking.

    Args:
        db (Session): La sesión de base de datos SQLAlchemy.

    Returns:
        list[Tipificacion]: Una lista de objetos `Tipificacion`, ordenados ascendentemente
                            por el campo `ranking`.
    """
    # Consulta todas las tipificaciones y las ordena por el campo 'ranking'.
    return db.query(Tipificacion).order_by(Tipificacion.ranking).all()
