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
        # id=str(uuid.uuid4()),
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
        return "Sin gestión"

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
            # "mes": mejor.fecha_gestion.strftime("%B").capitalize(),
            # "cantidad": len(gestiones)
        }
    else:
        return "Sin gestión"
def obtener_historico_gestiones(db: Session):
    gestiones = db.query(Gestion).all()
    resultado = []  

    for g in gestiones:
        reg = db.query(RegistroBase).filter(RegistroBase.id == g.registro_id).first()
        
        if not reg:
            continue  # Saltar registros inválidos
        
        tip = db.query(Tipificacion).filter(Tipificacion.nombre == g.tipificacion).first()

        resultado.append({
            "tipo_id": reg.tipo_id,
            "num_id": reg.num_id,
            "primer_nombre": reg.primer_nombre,
            "segundo_nombre": reg.segundo_nombre,
            "primer_apellido": reg.primer_apellido,
            "segundo_apellido": reg.segundo_apellido,
            "fecha": reg.fecha.strftime("%Y-%m-%d"),
            "edad": reg.edad,
            "estado_afiliacion": reg.estado_afiliacion,
            "regimen_afiliacion": reg.regimen_afiliacion,
            "proceso": reg.proceso,
            "telefonos": reg.telefonos,
            "direccion": reg.direccion,
            "municipio": reg.municipio,
            "subregion": reg.subregion,
            "proceso": reg.proceso,
            "fecha_carga": reg.fecha_carga.strftime("%Y-%m-%d %H:%M:%S"),
            "mejor_gestion": obtener_mejor_gestion_por_registro(db, g.registro_id),
            "tipificacion": g.tipificacion,
            "tipo_contacto": tip.tipo_contacto if tip else "Sin categorizar",
            "comentario": g.comentario,
            "id_llamada": g.id_llamada,
            "fecha_gestion": g.fecha_gestion,
            "asesor": g.usuario,
            "llave_compuesta": g.llave_compuesta,
            "tipo_gestion": "EFECTIVO" if tip and tip.tipo_contacto == "efectivo" else "no efectivo",
            "mes": reg.mes,
            "cantidad_gestiones": db.query(Gestion).filter(Gestion.registro_id == g.registro_id).count()
            # "cantidad_gestiones": db.query(Gestion).filter(Gestion.registro_id == g.registro_id).count()
        })
        print(resultado)

    return resultado

def obtener_total_mejor_gestiones(db: Session):
    resultado = []
    registros = db.query(RegistroBase).all()
        
    for r in registros:
        # Get all gestiones for this registro
        gestiones = db.query(Gestion).filter(Gestion.registro_id == r.id).all()
        
        # If there are gestiones, get the latest one
        if gestiones:
            ultima_gestion = gestiones[-1]
            tip = db.query(Tipificacion).filter(Tipificacion.nombre == ultima_gestion.tipificacion).first()
            
            resultado.append({
                "tipo_id": r.tipo_id,
                "num_id": r.num_id,
                "primer_nombre": r.primer_nombre,
                "segundo_nombre": r.segundo_nombre,
                "primer_apellido": r.primer_apellido,
                "segundo_apellido": r.segundo_apellido,
                "fecha": r.fecha,
                "edad": r.edad,
                "estado_afiliacion": r.estado_afiliacion,
                "regimen_afiliacion": r.regimen_afiliacion,
                "proceso": r.proceso,
                "telefonos": r.telefonos,
                "direccion": r.direccion,
                "municipio": r.municipio,
                "subregion": r.subregion,
                "fecha_carga": r.fecha_carga.strftime("%Y-%m-%d %H:%M:%S"),
                "mejor_gestion": obtener_mejor_gestion_por_registro(db, r.id)["tipificacion"],
                "tipificacion": ultima_gestion.tipificacion,
                "tipo_contacto": tip.tipo_contacto if tip else "sin categorizar",
                "comentario": ultima_gestion.comentario,
                "id_llamada": ultima_gestion.id_llamada,
                "fecha_gestion": ultima_gestion.fecha_gestion,
                "asesor": ultima_gestion.usuario,
                "tipo_gestion": "efectivo" if tip and tip.tipo_contacto == "efectivo" else "no efectivo",
                "mes": ultima_gestion.fecha_gestion.strftime("%B").capitalize(),
                "cantidad_gestiones": len(gestiones)
            })
            # print(resultado)
        else:
            # If no gestiones, add registro with default values
            resultado.append({
                "tipo_id": r.tipo_id,
                "num_id": r.num_id,
                "primer_nombre": r.primer_nombre,
                "segundo_nombre": r.segundo_nombre,
                "primer_apellido": r.primer_apellido,
                "segundo_apellido": r.segundo_apellido,
                "fecha": r.fecha,
                "edad": r.edad,
                "estado_afiliacion": r.estado_afiliacion,
                "regimen_afiliacion": r.regimen_afiliacion,
                "proceso": r.proceso,
                "telefonos": r.telefonos,
                "direccion": r.direccion,
                "municipio": r.municipio,
                "subregion": r.subregion,
                "fecha_carga": r.fecha_carga.strftime("%Y-%m-%d %H:%M:%S"),
                "mejor_gestion": obtener_mejor_gestion_por_registro(db, r.id),
                "tipificacion": "Sin gestión",
                "tipo_contacto": "Sin gestión",
                "comentario": "",
                "id_llamada": "",
                "fecha_gestion": "No existe",
                "asesor": "",
                "tipo_gestion": "Sin gestión",
                "mes": r.mes,
                "cantidad_gestiones": 0
            })

    return resultado

