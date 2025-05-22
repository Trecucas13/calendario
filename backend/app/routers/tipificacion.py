from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.tipificacion import TipificacionBase, TipificacionResponse
from app.crud import tipificacion as crud
from app.core.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TipificacionResponse)
def crear_tipificacion(data: TipificacionBase, db: Session = Depends(get_db)):
    return crud.crear_tipificacion(db, data)

@router.post("/cargar_multiples/", response_model=List[TipificacionResponse])
def cargar_multiples_tipificaciones(data: List[TipificacionBase], db: Session = Depends(get_db)):
    try:
        resultados = []
        for item in data:
            resultados.append(crud.crear_tipificacion(db, item))
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[TipificacionResponse])
def obtener_todas(db: Session = Depends(get_db)):
    return crud.listar_tipificaciones(db)
