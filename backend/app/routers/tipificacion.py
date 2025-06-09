from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List # Para tipar listas en las solicitudes y respuestas.

from app.schemas.tipificacion import TipificacionBase, TipificacionResponse # Schemas Pydantic.
from app.crud import tipificacion as crud # Funciones CRUD para tipificaciones.
from app.core.database import SessionLocal # Para la gestión de sesiones de BD.

# Endpoints de la API para la tipificación de gestiones.

router = APIRouter() # Creación del router para estos endpoints.

def get_db():
    """
    Dependencia de FastAPI para obtener una sesión de base de datos.

    Abre una sesión de base de datos al inicio de una solicitud y
    se asegura de que se cierre correctamente al finalizar.

    Yields:
        Session: Una instancia de la sesión de SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TipificacionResponse)
def crear_tipificacion(data: TipificacionBase, db: Session = Depends(get_db)):
    """
    Crea una nueva tipificación en la base de datos.

    Args:
        data (TipificacionBase): Los datos de la tipificación a crear, validados por Pydantic.
                                 Se espera en el cuerpo de la solicitud (request body).
        db (Session, optional): La sesión de base de datos. Defaults to Depends(get_db).

    Returns:
        TipificacionResponse: Los datos de la tipificación creada, según el esquema `TipificacionResponse`.
                              Responde con HTTP 200 OK por defecto.
    """
    # Llama a la función CRUD para crear la tipificación.
    return crud.crear_tipificacion(db, data)

@router.post("/cargar_multiples/", response_model=List[TipificacionResponse])
def cargar_multiples_tipificaciones(data: List[TipificacionBase], db: Session = Depends(get_db)):
    """
    Carga múltiples tipificaciones en la base de datos a partir de una lista.

    Args:
        data (List[TipificacionBase]): Una lista de objetos de tipificación a crear.
                                       Se espera en el cuerpo de la solicitud (request body).
        db (Session, optional): La sesión de base de datos. Defaults to Depends(get_db).

    Raises:
        HTTPException: Con código 500 si ocurre un error durante la creación
                       de alguna de las tipificaciones.

    Returns:
        List[TipificacionResponse]: Una lista de las tipificaciones creadas.
                                    Responde con HTTP 200 OK.
    """
    try:
        resultados_creacion = [] # Lista para almacenar las tipificaciones creadas.
        # Itera sobre cada item de datos y lo crea en la BD.
        for item_tipificacion in data:
            resultados_creacion.append(crud.crear_tipificacion(db, item_tipificacion))
        return resultados_creacion # Devuelve la lista de tipificaciones creadas.
    except Exception as e:
        # Si ocurre cualquier error durante el proceso, se lanza una excepción HTTP.
        # Considerar un manejo de errores más específico si es necesario (ej. por duplicados).
        raise HTTPException(status_code=500, detail=f"Error al cargar múltiples tipificaciones: {str(e)}")

@router.get("/lista_tipificaciones/", response_model=List[TipificacionResponse])
def obtener_todas(db: Session = Depends(get_db)):
    """
    Obtiene una lista de todas las tipificaciones existentes en la base de datos.

    Las tipificaciones se devuelven ordenadas según el criterio definido en la función CRUD
    (probablemente por ranking).

    Args:
        db (Session, optional): La sesión de base de datos. Defaults to Depends(get_db).

    Returns:
        List[TipificacionResponse]: Una lista de todas las tipificaciones.
                                    Responde con HTTP 200 OK.
    """
    # Llama a la función CRUD para listar todas las tipificaciones.
    return crud.listar_tipificaciones(db)
