from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.gestion import Gestion
from app.models.tipificacion import Tipificacion
from app.schemas.gestion import GestionCreate
from app.models.registro_base import RegistroBase
from datetime import datetime
import uuid

# Funciones CRUD para la gestión de registros de interacción o similar.

def crear_gestion(db: Session, data: GestionCreate):
    """
    Crea un nuevo registro de gestión en la base de datos.

    Args:
        db (Session): La sesión de base de datos SQLAlchemy.
        data (GestionCreate): El esquema Pydantic con los datos para crear la gestión.
                              Debe incluir `registro_id`, `tipificacion`, `comentario`,
                              `id_llamada` y `usuario`.

    Returns:
        Gestion: El objeto de modelo SQLAlchemy `Gestion` recién creado y guardado.
    """
    nueva = Gestion(
        # id=str(uuid.uuid4()), # El ID se genera automáticamente por la BD si es autoincremental o se maneja de otra forma.
        registro_id=data.registro_id,
        tipificacion=data.tipificacion, # La tipificación asignada a esta gestión.
        comentario=data.comentario, # Comentarios adicionales sobre la gestión.
        id_llamada=data.id_llamada, # Identificador de la llamada asociada, si aplica.
        usuario=data.usuario, # Usuario que realizó la gestión.
        fecha_gestion=datetime.utcnow() # Fecha y hora actual en UTC para la gestión.
    )
    db.add(nueva) # Añade el nuevo objeto de gestión a la sesión.
    db.commit() # Confirma la transacción en la base de datos.
    db.refresh(nueva) # Refresca el objeto `nueva` con los datos de la base de datos (ej. ID generado).
    return nueva # Retorna el objeto de gestión creado.

def obtener_mejor_gestion_por_registro(db: Session, registro_id: str):
    """
    Obtiene la "mejor" gestión para un registro específico, basada en el ranking de su tipificación.

    La "mejor" gestión se define como aquella cuya tipificación asociada tiene el menor ranking.
    Si no hay gestiones o ninguna tiene una tipificación con ranking, retorna "Sin gestión".

    Args:
        db (Session): La sesión de base de datos SQLAlchemy.
        registro_id (str): El ID del registro base para el cual se buscan las gestiones.

    Returns:
        dict or str: Un diccionario con los detalles de la mejor gestión y su tipo de contacto,
                     o la cadena "Sin gestión" si no se encuentra una gestión adecuada.
    """
    # Trae todas las gestiones asociadas al registro_id proporcionado.
    gestiones = db.query(Gestion).filter(Gestion.registro_id == registro_id).all()

    if not gestiones: # Si no hay gestiones para este registro.
        return "Sin gestión"

    # Inicializa variables para encontrar la gestión con el mejor ranking.
    mejor_gestion_encontrada = None # Almacenará el objeto Gestion de la mejor gestión.
    mejor_ranking_valor = float("inf") # Inicializa con infinito para asegurar que cualquier ranking sea menor.
    tipo_contacto_mejor_gestion = None # Almacenará el tipo de contacto de la mejor gestión.

    for gestion_actual in gestiones:
        # Busca la tipificación asociada a la gestión actual.
        tipificacion_actual = db.query(Tipificacion).filter(Tipificacion.nombre == gestion_actual.tipificacion).first()
        # Si la tipificación existe y su ranking es mejor (menor) que el actual mejor_ranking_valor.
        if tipificacion_actual and tipificacion_actual.ranking < mejor_ranking_valor:
            mejor_gestion_encontrada = gestion_actual # Actualiza la mejor gestión.
            mejor_ranking_valor = tipificacion_actual.ranking # Actualiza el mejor ranking.
            tipo_contacto_mejor_gestion = tipificacion_actual.tipo_contacto # Guarda el tipo de contacto.

    if mejor_gestion_encontrada: # Si se encontró una "mejor" gestión.
        return {
            "tipificacion": mejor_gestion_encontrada.tipificacion,
            "tipo_contacto": tipo_contacto_mejor_gestion,
            "usuario": mejor_gestion_encontrada.usuario,
            "fecha_gestion": mejor_gestion_encontrada.fecha_gestion.strftime("%Y-%m-%d %H:%M:%S"),
            # Comentarios sobre campos que podrían incluirse:
            # "mes": mejor_gestion_encontrada.fecha_gestion.strftime("%B").capitalize(), # Mes de la gestión.
            # "cantidad": len(gestiones) # Cantidad total de gestiones para este registro.
        }
    else: # Si no se encontró ninguna gestión con tipificación rankeada.
        return "Sin gestión"

def obtener_historico_gestiones(db: Session):
    """
    Obtiene un historial completo de todas las gestiones, enriquecido con datos del registro base
    y la tipificación asociada.

    Args:
        db (Session): La sesión de base de datos SQLAlchemy.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa una gestión
              con información detallada del paciente/registro y la tipificación.
              Retorna una lista vacía si no hay gestiones.
    """
    gestiones = db.query(Gestion).all() # Obtiene todas las gestiones de la base de datos.
    resultado_historico = []  # Lista para almacenar el resultado final.

    for gestion_individual in gestiones:
        # Obtiene el registro base asociado a la gestión actual.
        registro_asociado = db.query(RegistroBase).filter(RegistroBase.id == gestion_individual.registro_id).first()
        
        if not registro_asociado: # Si no se encuentra el registro base, se salta esta gestión.
            continue  # Saltar registros inválidos o inconsistencias de datos.
        
        # Obtiene la tipificación asociada a la gestión actual.
        tipificacion_asociada = db.query(Tipificacion).filter(Tipificacion.nombre == gestion_individual.tipificacion).first()

        # Construye el diccionario con la información combinada.
        resultado_historico.append({
            "tipo_id": registro_asociado.tipo_id,
            "num_id": registro_asociado.num_id,
            "primer_nombre": registro_asociado.primer_nombre,
            "segundo_nombre": registro_asociado.segundo_nombre,
            "primer_apellido": registro_asociado.primer_apellido,
            "segundo_apellido": registro_asociado.segundo_apellido,
            "fecha": registro_asociado.fecha.strftime("%Y-%m-%d"), # Formatea la fecha
            "edad": registro_asociado.edad,
            "estado_afiliacion": registro_asociado.estado_afiliacion,
            "regimen_afiliacion": registro_asociado.regimen_afiliacion,
            "proceso": registro_asociado.proceso,
            "telefonos": registro_asociado.telefonos,
            "direccion": registro_asociado.direccion,
            "municipio": registro_asociado.municipio,
            "subregion": registro_asociado.subregion,
            # "proceso": registro_asociado.proceso, # Campo 'proceso' parece estar duplicado, se comenta uno.
            "fecha_carga": registro_asociado.fecha_carga.strftime("%Y-%m-%d %H:%M:%S"), # Formatea fecha de carga
            "mejor_gestion": obtener_mejor_gestion_por_registro(db, gestion_individual.registro_id), # Llama a la función para obtener la mejor gestión
            "tipificacion": gestion_individual.tipificacion,
            "tipo_contacto": tipificacion_asociada.tipo_contacto if tipificacion_asociada else "Sin categorizar", # Asigna tipo de contacto o default
            "comentario": gestion_individual.comentario,
            "id_llamada": gestion_individual.id_llamada,
            "fecha_gestion": gestion_individual.fecha_gestion,
            "asesor": gestion_individual.usuario,
            "llave_compuesta": gestion_individual.llave_compuesta,
            "tipo_gestion": "EFECTIVO" if tipificacion_asociada and tipificacion_asociada.tipo_contacto == "efectivo" else "no efectivo", # Determina tipo de gestión
            "mes": registro_asociado.mes, # Mes del registro base
            "cantidad_gestiones": db.query(Gestion).filter(Gestion.registro_id == gestion_individual.registro_id).count() # Cuenta total de gestiones para el registro
        })
        # print(resultado_historico) # Útil para debugging, se mantiene comentado.

    return resultado_historico # Retorna la lista completa del historial.

def obtener_total_mejor_gestiones(db: Session):
    """
    Obtiene un resumen de todos los registros base, mostrando la información de su última gestión
    o indicando "Sin gestión" si no existen gestiones para ese registro.

    Para cada registro base, se determina su "mejor gestión" (basada en ranking) y se extrae
    información de la última gestión realizada (la más reciente por fecha, implícitamente
    tomada como `gestiones[-1]`).

    Args:
        db (Session): La sesión de base de datos SQLAlchemy.

    Returns:
        list: Una lista de diccionarios. Cada diccionario representa un registro base
              junto con los detalles de su última gestión o valores por defecto si no tiene gestiones.
    """
    resultado_final = [] # Lista para almacenar el resultado.
    registros_base_todos = db.query(RegistroBase).all() # Obtiene todos los registros base.
        
    for registro_actual in registros_base_todos:
        # Obtiene todas las gestiones para el registro actual.
        gestiones_del_registro = db.query(Gestion).filter(Gestion.registro_id == registro_actual.id).all()
        
        # Si existen gestiones para este registro.
        if gestiones_del_registro:
            ultima_gestion_realizada = gestiones_del_registro[-1] # Asume que la última en la lista es la más reciente.
            # Se podría ordenar por fecha explícitamente si fuera necesario: .order_by(Gestion.fecha_gestion.desc()).first()

            tipificacion_ultima_gestion = db.query(Tipificacion).filter(Tipificacion.nombre == ultima_gestion_realizada.tipificacion).first()
            
            # Obtiene la "mejor gestión" usando la función auxiliar.
            mejor_gestion_info = obtener_mejor_gestion_por_registro(db, registro_actual.id)
            # Se extrae la tipificación de la mejor gestión, o se usa el valor directo si es "Sin gestión".
            tipificacion_mejor_gestion = mejor_gestion_info["tipificacion"] if isinstance(mejor_gestion_info, dict) else mejor_gestion_info

            resultado_final.append({
                "tipo_id": registro_actual.tipo_id,
                "num_id": registro_actual.num_id,
                "primer_nombre": registro_actual.primer_nombre,
                "segundo_nombre": registro_actual.segundo_nombre,
                "primer_apellido": registro_actual.primer_apellido,
                "segundo_apellido": registro_actual.segundo_apellido,
                "fecha": registro_actual.fecha, # Podría formatearse: registro_actual.fecha.strftime("%Y-%m-%d")
                "edad": registro_actual.edad,
                "estado_afiliacion": registro_actual.estado_afiliacion,
                "regimen_afiliacion": registro_actual.regimen_afiliacion,
                "proceso": registro_actual.proceso,
                "telefonos": registro_actual.telefonos,
                "direccion": registro_actual.direccion,
                "municipio": registro_actual.municipio,
                "subregion": registro_actual.subregion,
                "fecha_carga": registro_actual.fecha_carga.strftime("%Y-%m-%d %H:%M:%S"),
                "mejor_gestion": tipificacion_mejor_gestion, # Tipificación de la mejor gestión.
                "tipificacion": ultima_gestion_realizada.tipificacion, # Tipificación de la última gestión.
                "tipo_contacto": tipificacion_ultima_gestion.tipo_contacto if tipificacion_ultima_gestion else "sin categorizar",
                "comentario": ultima_gestion_realizada.comentario,
                "id_llamada": ultima_gestion_realizada.id_llamada,
                "fecha_gestion": ultima_gestion_realizada.fecha_gestion, # Podría formatearse.
                "asesor": ultima_gestion_realizada.usuario,
                "tipo_gestion": "efectivo" if tipificacion_ultima_gestion and tipificacion_ultima_gestion.tipo_contacto == "efectivo" else "no efectivo",
                "mes": ultima_gestion_realizada.fecha_gestion.strftime("%B").capitalize(), # Mes de la última gestión.
                "cantidad_gestiones": len(gestiones_del_registro) # Total de gestiones para este registro.
            })
            # print(resultado_final) # Útil para debugging.
        else:
            # Si no hay gestiones para este registro, se añaden valores por defecto.
            resultado_final.append({
                "tipo_id": registro_actual.tipo_id,
                "num_id": registro_actual.num_id,
                "primer_nombre": registro_actual.primer_nombre,
                "segundo_nombre": registro_actual.segundo_nombre,
                "primer_apellido": registro_actual.primer_apellido,
                "segundo_apellido": registro_actual.segundo_apellido,
                "fecha": registro_actual.fecha, # Podría formatearse.
                "edad": registro_actual.edad,
                "estado_afiliacion": registro_actual.estado_afiliacion,
                "regimen_afiliacion": registro_actual.regimen_afiliacion,
                "proceso": registro_actual.proceso,
                "telefonos": registro_actual.telefonos,
                "direccion": registro_actual.direccion,
                "municipio": registro_actual.municipio,
                "subregion": registro_actual.subregion,
                "fecha_carga": registro_actual.fecha_carga.strftime("%Y-%m-%d %H:%M:%S"),
                "mejor_gestion": obtener_mejor_gestion_por_registro(db, registro_actual.id), # Será "Sin gestión".
                "tipificacion": "Sin gestión",
                "tipo_contacto": "Sin gestión",
                "comentario": "",
                "id_llamada": "",
                "fecha_gestion": "No existe", # Indica que no hay fecha de gestión.
                "asesor": "",
                "tipo_gestion": "Sin gestión",
                "mes": registro_actual.mes, # Mes del registro base.
                "cantidad_gestiones": 0 # Cero gestiones.
            })

    return resultado_final

