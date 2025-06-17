from sqlalchemy.orm import Session
from app.models.registro_base import RegistroBase
from app.models.gestion import Gestion
from app.models.tipificacion import Tipificacion
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

def get_registros_completos(db: Session):
    resultado = []
    registros = db.query(RegistroBase).all()
        
    for r in registros:
        gestiones = db.query(Gestion).filter(Gestion.registro_id == r.id).all()
        
        if not r: 
            continue
        
        if gestiones:
            ultima_gestion = gestiones[-1]
            tip = db.query(Tipificacion).filter(Tipificacion.nombre == ultima_gestion.tipificacion).first()
            resultado.append({
                "tipo_id": r.tipo_id,
                "registro_id": r.id,
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
                "fecha_carga": r.fecha_carga.strftime("%Y-%m-%d %H:%M:%S") if r.fecha_carga else None,
                "tipificacion": ultima_gestion.tipificacion,
                "tipo_contacto": tip.tipo_contacto if tip else "sin categorizar",
                "comentario": ultima_gestion.comentario,
                "id_llamada": ultima_gestion.id_llamada,
                "fecha_gestion": ultima_gestion.fecha_gestion,
                "asesor": ultima_gestion.usuario,
                "tipo_gestion": "efectivo" if tip and tip.tipo_contacto == "efectivo" else "no efectivo",
                "mes": ultima_gestion.fecha_gestion.strftime("%B").capitalize() if ultima_gestion.fecha_gestion else None,
                "cantidad_gestiones": len(gestiones)
            })
        else:
            resultado.append({
                "tipo_id": r.tipo_id,
                "registro_id": r.id,
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
                "fecha_carga": r.fecha_carga.strftime("%Y-%m-%d %H:%M:%S") if r.fecha_carga else None,
                "tipificacion": None,
                "tipo_contacto": None,
                "comentario": None,
                "id_llamada": None,
                "fecha_gestion": None,
                "asesor": None,
                "tipo_gestion": None,
                "mes": None,
                "cantidad_gestiones": 0
            })
        # print(resultado)
    return resultado

def get_registros(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene registros de Gestión junto con datos relacionados de RegistroBase
    Devuelve una lista de tuplas con los campos seleccionados
    """
    resultados = db.query( 
        Gestion.id,  # Usamos label para claridad
        Gestion.tipificacion,
        Gestion.comentario,
        Gestion.id_llamada,
        Gestion.fecha_gestion,
        Gestion.usuario,
        Gestion.registro_id,
        Gestion.llave_compuesta,
        Gestion.motivo,
        RegistroBase.id,  # Usamos label para claridad
        RegistroBase.tipo_id,
        RegistroBase.num_id,
        RegistroBase.primer_nombre,
        RegistroBase.segundo_nombre,
        RegistroBase.primer_apellido,
        RegistroBase.segundo_apellido,
        RegistroBase.fecha,
        RegistroBase.edad,
        RegistroBase.estado_afiliacion,
        RegistroBase.regimen_afiliacion,
        RegistroBase.telefonos,
        RegistroBase.direccion,
        RegistroBase.municipio,
        RegistroBase.subregion,
        RegistroBase.proceso,
        RegistroBase.fecha_carga,
        RegistroBase.mes,
        RegistroBase.cantidad_gestiones.label("cantidad_gestiones"), # Asegúrate de que este campo exista
        RegistroBase.mejor_gestion,
        RegistroBase.tipo_gestion,
        # RegistroBase.fecha_gestion
        ).join(
        Gestion, RegistroBase.id == Gestion.registro_id
        
    ).offset(skip).limit(limit).all()
    
    # Imprimir resultados para depuración
    print("\nRegistros obtenidos:")
    for i, registro in enumerate(resultados, 1):
        print(f"\nRegistro #{i}:")
        print(f"Tipificación: {registro.tipificacion}")
        print(f"Comentario: {registro.comentario}")
        print(f"ID Llamada: {registro.id_llamada}")
        print(f"Fecha Gestión: {registro.fecha_gestion}")
        print(f"Usuario: {registro.usuario}")
        print(f"ID Registro: {registro.registro_id}")
        print(f"mes: {registro.mes}")
        print(f"motivo: {registro.motivo}")
    
    return resultados

# def get_lista_completa(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(RegistroBase).offset(skip).limit(limit).all()