from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.schemas.gestion import GestionCreate, GestionResponse, GestionHistorico
from app.crud import gestion as crud

from app.core.database import SessionLocal
from typing import List
from fastapi.templating import Jinja2Templates

router = APIRouter()

# Configuración de templates
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=GestionResponse)
def registrar_gestion(data: GestionCreate, db: Session = Depends(get_db)):
    return crud.crear_gestion(db, data)

@router.get("/gestion_bd/")
def listar_historico(db: Session = Depends(get_db)):
    return crud.obtener_historico_gestiones(db)

# Nueva ruta para renderizar la plantilla HTML
@router.get("/historico-page/")
async def mostrar_historico(request: Request, db: Session = Depends(get_db)):
    gestiones = crud.obtener_historico_gestiones(db)
    return gestiones