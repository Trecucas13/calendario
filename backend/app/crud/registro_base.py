from sqlalchemy.orm import Session
from app.models.registro_base import RegistroBase
from app.models.gestion import Gestion
from app.schemas.registro_base import RegistroBaseCreate
from datetime import datetime

# Funciones CRUD para los registros de la base de datos de pacientes o similar.

def create_registro(db: Session, data: RegistroBaseCreate):
    """
    Crea un nuevo registro base (paciente, cliente, etc.) en la base de datos.

    Args:
        db (Session): La sesión de base de datos SQLAlchemy.
        data (RegistroBaseCreate): El esquema Pydantic con los datos para crear el registro.
                                   Los campos del esquema se mapearán directamente a las
                                   columnas del modelo `RegistroBase`.

    Returns:
        RegistroBase: El objeto de modelo SQLAlchemy `RegistroBase` recién creado y guardado.
                      Incluye la `fecha_carga` establecida a la hora UTC actual.
    """
    nuevo_registro = RegistroBase(
        **data.dict(), # Desempaqueta los datos del esquema Pydantic en los atributos del modelo.
        fecha_carga=datetime.utcnow() # Establece la fecha de carga a la hora actual en UTC.
    )
    db.add(nuevo_registro) # Añade el nuevo objeto de registro a la sesión.
    db.commit() # Confirma la transacción en la base de datos.
    db.refresh(nuevo_registro) # Refresca el objeto con datos de la BD (ej. ID generado).
    return nuevo_registro # Retorna el objeto de registro creado.

def get_registros_completos(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista paginada de todos los registros base.

    Args:
        db (Session): La sesión de base de datos SQLAlchemy.
        skip (int, optional): El número de registros a omitir (para paginación). Por defecto es 0.
        limit (int, optional): El número máximo de registros a devolver (para paginación). Por defecto es 100.

    Returns:
        list[RegistroBase]: Una lista de objetos `RegistroBase`.
    """
    return db.query(RegistroBase).offset(skip).limit(limit).all() # Realiza la consulta y la paginación.

def get_registros(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista paginada de registros de `Gestion` junto con datos relacionados
    de la tabla `RegistroBase` a la que están vinculados.

    Realiza un JOIN entre las tablas `Gestion` y `RegistroBase` utilizando `RegistroBase.id == Gestion.registro_id`.
    Selecciona campos específicos de ambas tablas.

    Args:
        db (Session): La sesión de base de datos SQLAlchemy.
        skip (int, optional): Número de registros a omitir para paginación. Por defecto es 0.
        limit (int, optional): Número máximo de registros a devolver. Por defecto es 100.

    Returns:
        list[tuple]: Una lista de tuplas. Cada tupla contiene los campos seleccionados
                     de las tablas `Gestion` y `RegistroBase` para un registro de gestión.
                     La estructura de la tupla está definida por el orden de los campos en `db.query(...)`.
    """
    # La consulta realiza un JOIN explícito entre Gestion y RegistroBase.
    # Se seleccionan campos de ambas tablas.
    resultados = db.query(
        Gestion.id.label("gestion_id"),  # Es buena práctica usar labels para evitar colisiones de nombres y dar claridad.
        Gestion.tipificacion,
        Gestion.comentario,
        Gestion.id_llamada,
        Gestion.fecha_gestion,
        Gestion.usuario,
        Gestion.registro_id, # ID del registro base al que esta gestión pertenece.
        Gestion.llave_compuesta, # Llave compuesta de la gestión.
        RegistroBase.id.label("registro_base_id"), # ID del registro base.
        RegistroBase.tipo_id, # Tipo de identificación del registro base.
        RegistroBase.num_id, # Número de identificación.
        RegistroBase.primer_nombre,
        RegistroBase.segundo_nombre,
        RegistroBase.primer_apellido,
        RegistroBase.segundo_apellido,
        RegistroBase.fecha, # Fecha relevante del registro base (ej. nacimiento).
        RegistroBase.edad,
        RegistroBase.estado_afiliacion,
        RegistroBase.regimen_afiliacion,
        RegistroBase.telefonos,
        RegistroBase.direccion,
        RegistroBase.municipio,
        RegistroBase.subregion,
        RegistroBase.proceso,
        RegistroBase.fecha_carga, # Fecha en que se cargó el registro base.
        RegistroBase.mes, # Mes asociado al registro base.
        RegistroBase.cantidad_gestiones.label("cantidad_gestiones_rb"), # Cantidad de gestiones del RegistroBase. Usar label para diferenciar.
        RegistroBase.mejor_gestion, # Mejor gestión del RegistroBase.
        RegistroBase.tipo_gestion, # Tipo de gestión del RegistroBase.
        # RegistroBase.fecha_gestion # Este campo parece pertenecer más a Gestion, considerar si es necesario aquí.
        ).join(
        Gestion, RegistroBase.id == Gestion.registro_id # Condición del JOIN.
        
    ).offset(skip).limit(limit).all() # Aplica paginación.
    
    # Bloque de impresión para depuración. Se mantiene comentado para producción.
    # print("\nRegistros obtenidos:")
    # for i, registro in enumerate(resultados, 1):
    #     print(f"\nRegistro #{i}:")
    #     print(f"Tipificación: {registro.tipificacion}")
    #     print(f"Comentario: {registro.comentario}")
    #     print(f"ID Llamada: {registro.id_llamada}")
    #     print(f"Fecha Gestión: {registro.fecha_gestion}")
    #     print(f"Usuario: {registro.usuario}")
    #     print(f"ID Registro (Gestion.registro_id): {registro.registro_id}")
    #     print(f"Mes (RegistroBase.mes): {registro.mes}")
    #     # Acceder a los campos por label o índice si es necesario, ej: registro.gestion_id, registro.registro_base_id
    
    return resultados # Retorna la lista de tuplas.

# Función comentada, se mantiene así.
# def get_lista_completa(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(RegistroBase).offset(skip).limit(limit).all()