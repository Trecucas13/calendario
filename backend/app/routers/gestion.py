from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.gestion import GestionCreate, GestionResponse, GestionHistorico
from app.crud import gestion as crud
from app.core.database import SessionLocal
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=GestionResponse)
def registrar_gestion(data: GestionCreate, db: Session = Depends(get_db)):
    return crud.crear_gestion(db, data)

@router.get("/historico/", response_model=List[GestionHistorico])
def listar_historico(db: Session = Depends(get_db)):
    return crud.obtener_historico_gestiones(db)