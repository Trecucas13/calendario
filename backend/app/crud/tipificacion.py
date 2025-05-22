from sqlalchemy.orm import Session
from app.models.tipificacion import Tipificacion
from app.schemas.tipificacion import TipificacionBase

def crear_tipificacion(db: Session, data: TipificacionBase):
    nueva = Tipificacion(**data.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def listar_tipificaciones(db: Session):
    return db.query(Tipificacion).order_by(Tipificacion.ranking).all()
