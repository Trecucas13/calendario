from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.gestion import Gestion
from app.models.tipificacion import Tipificacion
from app.schemas.gestion import GestionCreate
from app.models.registro_base import RegistroBase
from datetime import datetime
import uuid

def crear_gestion(db: Session, data: GestionCreate):
    nueva = Gestion(
        id=str(uuid.uuid4()),
        registro_id=data.registro_id,
        tipificacion=data.tipificacion,
        comentario=data.comentario,
        id_llamada=data.id_llamada,
        usuario=data.usuario,
        fecha_gestion=datetime.utcnow()
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def obtener_mejor_gestion_por_registro(db: Session, registro_id: str):
    # Trae todas las gestiones del paciente
    gestiones = db.query(Gestion).filter(Gestion.registro_id == registro_id).all()

    if not gestiones:
        return {
            "tipificacion": "SIN GESTIÓN",
            "tipo_contacto": "SIN GESTIÓN",
            "usuario": "SIN GESTIÓN",
            "fecha_gestion": "SIN GESTIÓN",
            "mes": "SIN GESTIÓN",
            "cantidad": 0
        }

    # Buscar tipificación con menor ranking
    mejor = None
    mejor_ranking = float("inf")

    for g in gestiones:
        tip = db.query(Tipificacion).filter(Tipificacion.nombre == g.tipificacion).first()
        if tip and tip.ranking < mejor_ranking:
            mejor = g
            mejor_ranking = tip.ranking
            tipo_contacto = tip.tipo_contacto

    if mejor:
        return {
            "tipificacion": mejor.tipificacion,
            "tipo_contacto": tipo_contacto,
            "usuario": mejor.usuario,
            "fecha_gestion": mejor.fecha_gestion.strftime("%Y-%m-%d %H:%M:%S"),
            "mes": mejor.fecha_gestion.strftime("%B").capitalize(),
            "cantidad": len(gestiones)
        }
    else:
        return {
            "tipificacion": "SIN GESTIÓN",
            "tipo_contacto": "SIN GESTIÓN",
            "usuario": "SIN GESTIÓN",
            "fecha_gestion": "SIN GESTIÓN",
            "mes": "SIN GESTIÓN",
            "cantidad": len(gestiones)
        }

def obtener_historico_gestiones(db: Session):
    gestiones = db.query(Gestion).all()
    resultado = []

    for g in gestiones:
        reg = db.query(RegistroBase).filter(RegistroBase.id == g.registro_id).first()
        tip = db.query(Tipificacion).filter(Tipificacion.nombre == g.tipificacion).first()

        resultado.append({
            "tipo_id": reg.tipo_id,
            "num_id": reg.num_id,
            "primer_nombre": reg.primer_nombre,
            "segundo_nombre": reg.segundo_nombre,
            "primer_apellido": reg.primer_apellido,
            "segundo_apellido": reg.segundo_apellido,
            "proceso": reg.proceso,

            "tipificacion": g.tipificacion,
            "tipo_contacto": tip.tipo_contacto if tip else "SIN CATEGORIZAR",
            "comentario": g.comentario,
            "id_llamada": g.id_llamada,
            "fecha_gestion": g.fecha_gestion,
            "usuario": g.usuario
        })

    return resultado