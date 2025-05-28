from sqlalchemy.orm import Session
from app.models.registro_base import RegistroBase
from app.schemas.registro_base import RegistroBaseCreate
from datetime import datetime

def create_registro(db: Session, data: RegistroBaseCreate):
    nuevo = RegistroBase(
        **data.dict(),
        fecha_carga=datetime.utcnow()
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def get_registros(db: Session, skip: int = 0, limit: int = 100):
    return db.query(RegistroBase).offset(skip).limit(limit).all()


def get_lista_completa(db: Session, skip: int = 0, limit: int = 100):
    return db.query(RegistroBase).offset(skip).limit(limit).all()