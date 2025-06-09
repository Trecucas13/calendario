from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.schemas.gestion import GestionCreate, GestionResponse, GestionHistorico # Asumo que GestionHistorico es un schema Pydantic
from app.crud import gestion as crud # Importa las funciones CRUD para gestiones

from app.core.database import SessionLocal # Para la gestión de sesiones de BD
from typing import List # Para tipado, aunque no se usa directamente en List[GestionHistorico] aquí
from fastapi.templating import Jinja2Templates # Para renderizar plantillas HTML

# Endpoints de la API para la gestión de interacciones (gestiones).

router = APIRouter() # Creación del router para estos endpoints.

# Configuración de templates (si se van a renderizar vistas HTML desde aquí)
templates = Jinja2Templates(directory="templates") # Directorio donde se encuentran las plantillas.

def get_db():
    """
    Dependencia de FastAPI para obtener una sesión de base de datos.

    Abre una sesión de base de datos al inicio de una solicitud y
    se asegura de que se cierre correctamente al finalizar, incluso si ocurren errores.

    Yields:
        Session: Una instancia de la sesión de SQLAlchemy.
    """
    db = SessionLocal() # Crea una nueva sesión.
    try:
        yield db # Proporciona la sesión a la función de la ruta.
    finally:
        db.close() # Cierra la sesión al finalizar.

@router.post("/", response_model=GestionResponse)
def registrar_gestion(data: GestionCreate, db: Session = Depends(get_db)):
    """
    Registra una nueva gestión en la base de datos.

    Args:
        data (GestionCreate): Los datos de la gestión a crear, validados por Pydantic.
                              Se espera en el cuerpo de la solicitud (request body).
        db (Session, optional): La sesión de base de datos, inyectada por FastAPI.
                                Defaults to Depends(get_db).

    Returns:
        GestionResponse: Los datos de la gestión creada, incluyendo su ID y fecha de creación,
                         según el esquema `GestionResponse`.
                         Responde con HTTP 200 OK por defecto si es exitoso.
    """
    # Llama a la función CRUD para crear la gestión con los datos proporcionados.
    return crud.crear_gestion(db, data)

@router.get("/gestion_bd/") # El nombre de la ruta podría ser más descriptivo, ej. "/resumen-mejor-gestion/"
def listar_historico(db: Session = Depends(get_db)):
    """
    Obtiene un listado o resumen de las "mejores" gestiones para todos los registros.

    Este endpoint llama a `crud.obtener_total_mejor_gestiones` que, según su nombre,
    parece devolver un resumen agregado o la mejor gestión por cada registro base.

    Args:
        db (Session, optional): La sesión de base de datos. Defaults to Depends(get_db).

    Returns:
        list: Una lista de diccionarios (o el tipo que devuelva `crud.obtener_total_mejor_gestiones`),
              representando el resumen de las mejores gestiones.
              Responde con HTTP 200 OK.
    """
    # Obtiene el resumen de las mejores gestiones.
    return crud.obtener_total_mejor_gestiones(db)

# Nueva ruta para renderizar la plantilla HTML (o devolver datos para una página)
@router.get("/historico-page/") # Considerar si el schema de respuesta debe ser especificado con response_model
async def mostrar_historico(request: Request, db: Session = Depends(get_db)):
    """
    Obtiene el historial completo de gestiones, posiblemente para ser mostrado en una página.

    Este endpoint llama a `crud.obtener_historico_gestiones` que devuelve una lista
    detallada de todas las gestiones con información enriquecida.
    El parámetro `request` sugiere que podría usarse para renderizar una plantilla HTML,
    aunque actualmente solo devuelve los datos.

    Args:
        request (Request): El objeto de solicitud de FastAPI (necesario si se usa con templates).
        db (Session, optional): La sesión de base de datos. Defaults to Depends(get_db).

    Returns:
        list: Una lista de objetos (probablemente diccionarios) representando el historial
              completo de gestiones, tal como lo devuelve `crud.obtener_historico_gestiones`.
              Responde con HTTP 200 OK.
    """
    # Obtiene el historial completo de gestiones.
    gestiones = crud.obtener_historico_gestiones(db)
    # Si se quisiera renderizar una plantilla HTML:
    # return templates.TemplateResponse("historico.html", {"request": request, "gestiones": gestiones})
    return gestiones # Devuelve los datos directamente como JSON.