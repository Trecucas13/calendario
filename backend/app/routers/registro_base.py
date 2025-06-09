from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List # Para tipar listas en las respuestas.
from io import BytesIO # Para manejar el contenido de archivos en memoria.
import pandas as pd # Para leer y procesar archivos Excel y CSV.

from app.schemas.registro_base import RegistroBaseCreate, RegistroBaseResponse, RegistroConGestion # Schemas Pydantic para validación y serialización.
from app.models.registro_base import RegistroBase # Modelo SQLAlchemy.
from app.crud import registro_base as crud # Funciones CRUD.
from app.core.database import SessionLocal # Para la gestión de sesiones de BD.

# Endpoints de la API para los registros base (pacientes).

router = APIRouter() # Creación del router para estos endpoints.

# Dependencia para obtener la sesión de base de datos.
def get_db():
    """
    Dependencia de FastAPI para obtener una sesión de base de datos.

    Abre una sesión de base de datos al inicio de una solicitud y
    se asegura de que se cierre correctamente al finalizar.

    Yields:
        Session: Una instancia de la sesión de SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=RegistroBaseResponse)
def crear_registro(data: RegistroBaseCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo registro base en la base de datos.

    Args:
        data (RegistroBaseCreate): Los datos del registro a crear, validados por Pydantic.
                                   Se espera en el cuerpo de la solicitud (request body).
        db (Session, optional): La sesión de base de datos. Defaults to Depends(get_db).

    Returns:
        RegistroBaseResponse: Los datos del registro creado, según el esquema `RegistroBaseResponse`.
                              Responde con HTTP 200 OK por defecto.
    """
    return crud.create_registro(db, data)

@router.get("/listar_historico", response_model=List[RegistroBaseResponse]) # El schema de respuesta podría ser List[RegistroConGestion] si esa es la intención.
def listar_registros(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista los registros de gestión junto con información del registro base asociado.

    Este endpoint utiliza `crud.get_registros` que realiza un JOIN entre gestiones y registros base.
    Permite paginación a través de los parámetros `skip` y `limit`.

    Args:
        skip (int, optional): Número de registros a omitir. Defaults to 0.
        limit (int, optional): Número máximo de registros a devolver. Defaults to 100.
        db (Session, optional): La sesión de base de datos. Defaults to Depends(get_db).

    Returns:
        List[RegistroBaseResponse]: Una lista de registros. El schema `RegistroBaseResponse`
                                    debería reflejar la estructura devuelta por `crud.get_registros`
                                    (que parece ser una tupla o un objeto con campos de ambas tablas).
                                    Si `crud.get_registros` devuelve tuplas, se necesitaría un mapeo
                                    manual o un schema más complejo para `RegistroBaseResponse`.
                                    Responde con HTTP 200 OK.
    """
    # Llama a la función CRUD que obtiene registros con JOIN (probablemente gestiones y sus registros base).
    return crud.get_registros(db, skip, limit)

@router.get("/completo/", response_model=List[RegistroBaseResponse])
def listar_registros_completos(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Lista todos los registros base de forma paginada, sin unirse con gestiones necesariamente.

    Este endpoint utiliza `crud.get_registros_completos` que parece devolver solo
    los registros de la tabla `RegistroBase`.

    Args:
        db (Session, optional): La sesión de base de datos. Defaults to Depends(get_db).
        skip (int, optional): Número de registros a omitir. Defaults to 0.
        limit (int, optional): Número máximo de registros a devolver. Defaults to 100.

    Returns:
        List[RegistroBaseResponse]: Una lista de registros base.
                                    Responde con HTTP 200 OK.
    """
    return crud.get_registros_completos(db, skip, limit)

@router.post("/cargar_archivo/", response_class=RedirectResponse)
def cargar_archivo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Carga registros base desde un archivo Excel (.xlsx) o CSV (.csv).

    El archivo debe contener columnas específicas. El endpoint procesa el archivo,
    verifica la existencia de registros basados en una llave compuesta
    (TIPO DE IDENTIFICACIÓN, NUMERO DE IDENTIFICACIÓN, PROCESO) y solo inserta
    los registros nuevos. Finalmente, redirige a "/gestion_bd" en el frontend.

    Args:
        file (UploadFile): El archivo a cargar. Se espera como parte de un formulario (form-data).
        db (Session, optional): La sesión de base de datos. Defaults to Depends(get_db).

    Raises:
        HTTPException: Con código 400 si el formato del archivo no es soportado,
                       si hay un error leyendo el archivo, o si faltan columnas requeridas.
                       También si ocurre un error durante el commit a la base de datos.

    Returns:
        RedirectResponse: Redirige a "http://localhost:5000/gestion_bd" con código 303
                          si el proceso es exitoso.
    """
    # Validación del tipo de archivo.
    if not file.filename.endswith((".xlsx", ".csv")):
        raise HTTPException(status_code=400, detail="Formato no soportado. Usa .xlsx o .csv")

    content = file.file.read() # Lee el contenido del archivo.
    try:
        # Lee el archivo en un DataFrame de Pandas.
        if file.filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(content), engine="openpyxl")
        else:
            df = pd.read_csv(BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error leyendo archivo: {str(e)}")

    # Definición de las columnas esperadas en el archivo.
    columnas_requeridas = [
        "TIPO DE IDENTIFICACIÓN", "NUMERO DE IDENTIFICACIÓN", "1ER NOMBRE", "2DO NOMBRE",
        "1ER APELLDO", "2DO APELLDO", "FECHA", "EDAD", "ESTADO DE AFILIACIÓN",
        "RÉGIMEN DE AFILIACIÓN", "TELEFONO FIJO / OTRO", "DIRECCIÓN DE RESIDENCIA",
        "MUNICIPIO", "SUBREGIÓN", "PROCESO"
    ]
    # Verifica que todas las columnas requeridas estén presentes.
    if not all(col in df.columns for col in columnas_requeridas):
        raise HTTPException(status_code=400, detail="Faltan columnas requeridas en el archivo")

    registros_nuevos_contador = 0 # Contador para los registros nuevos insertados.
    # Itera sobre cada fila del DataFrame.
    for _, row in df.iterrows():

        row_dict = row.to_dict() # Convierte la fila a un diccionario.
        # Reemplaza valores NaN (Not a Number) de Pandas con None de Python.
        for key in row_dict:
            if pd.isna(row_dict[key]):
                row_dict[key] = None

        # Crea una llave compuesta para verificar si el registro ya existe.
        llave_existencia = (row_dict["TIPO DE IDENTIFICACIÓN"],
                            str(row_dict["NUMERO DE IDENTIFICACIÓN"]), # Asegura que el número de ID sea string.
                            row_dict["PROCESO"])

        # Consulta la base de datos para ver si el registro ya existe.
        existe = db.query(RegistroBase).filter_by(
            tipo_id=llave_existencia[0],
            num_id=llave_existencia[1],
            proceso=llave_existencia[2]
        ).first()

        # Si el registro no existe, se crea uno nuevo.
        if not existe:
            nuevo_registro_obj = RegistroBase(
                tipo_id=row_dict["TIPO DE IDENTIFICACIÓN"],
                num_id=str(row_dict["NUMERO DE IDENTIFICACIÓN"]),
                primer_nombre=row_dict["1ER NOMBRE"],
                segundo_nombre=row_dict.get("2DO NOMBRE"), # Usa .get() para campos opcionales.
                primer_apellido=row_dict["1ER APELLDO"],
                segundo_apellido=row_dict.get("2DO APELLDO"),
                fecha=pd.to_datetime(row_dict["FECHA"], errors='coerce'), # Convierte a datetime, errores resultan en NaT (None).
                edad=int(row_dict["EDAD"]) if not pd.isna(row_dict["EDAD"]) else None, # Convierte edad a int si no es NaN.
                estado_afiliacion=row_dict["ESTADO DE AFILIACIÓN"],
                regimen_afiliacion=row_dict["RÉGIMEN DE AFILIACIÓN"],
                telefonos=row_dict["TELEFONO FIJO / OTRO"],
                direccion=row_dict["DIRECCIÓN DE RESIDENCIA"],
                municipio=row_dict["MUNICIPIO"],
                subregion=row_dict["SUBREGIÓN"],
                proceso=row_dict["PROCESO"]
                # `fecha_carga` se establece por defecto en el modelo.
            )
            db.add(nuevo_registro_obj) # Añade el nuevo registro a la sesión.
            registros_nuevos_contador += 1 # Incrementa el contador.

    try:
        db.commit() # Confirma todas las inserciones a la base de datos.
        # Se comenta el retorno de mensaje JSON y se usa la redirección.
        # return {"mensaje": f"Proceso completado. Se insertaron {registros_nuevos_contador} nuevos registros."}
        return RedirectResponse(url="http://localhost:5000/gestion_bd", status_code=303) # Redirige al frontend.
    except Exception as e:
        db.rollback() # Si hay un error, revierte los cambios.
        raise HTTPException(status_code=400, detail=f"Error al guardar en base de datos: {str(e)}")

