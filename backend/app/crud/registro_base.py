from sqlalchemy.orm import Session
from app.models.registro_base import RegistroBase
from app.models.gestion import Gestion
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

def get_registros_completos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(RegistroBase).offset(skip).limit(limit).all()

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
        RegistroBase.asesor,
        RegistroBase.tipo_gestion,
        RegistroBase.fecha_gestion
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
        print(f"Tipo ID: {registro.tipo_id}")
    
    return resultados

# def get_lista_completa(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(RegistroBase).offset(skip).limit(limit).all()