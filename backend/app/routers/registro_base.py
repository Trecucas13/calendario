from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from io import BytesIO
import pandas as pd

from app.schemas.registro_base import RegistroBaseCreate, RegistroBaseResponse, RegistroConGestion
from app.models.registro_base import RegistroBase
from app.crud import registro_base as crud
from app.core.database import SessionLocal

router = APIRouter()

# Dependency para obtener la sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=RegistroBaseResponse)
def crear_registro(data: RegistroBaseCreate, db: Session = Depends(get_db)):
    return crud.create_registro(db, data)

@router.get("/", response_model=List[RegistroBaseResponse])
def listar_registros(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_registros(db, skip, limit)

@router.get("/completo/", response_model=List[RegistroConGestion])
def listar_registros_completos(db: Session = Depends(get_db)):
    return crud.obtener_registros_con_gestion(db)

@router.post("/cargar_archivo/")
def cargar_archivo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".csv")):
        raise HTTPException(status_code=400, detail="Formato no soportado. Usa .xlsx o .csv")

    content = file.file.read()
    try:
        if file.filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(content), engine="openpyxl")
        else:
            df = pd.read_csv(BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error leyendo archivo: {str(e)}")

    columnas_requeridas = [
        "TIPO DE IDENTIFICACIÓN", "NUMERO DE IDENTIFICACIÓN", "1ER NOMBRE", "2DO NOMBRE",
        "1ER APELLDO", "2DO APELLDO", "FECHA", "EDAD", "ESTADO DE AFILIACIÓN",
        "RÉGIMEN DE AFILIACIÓN", "TELEFONO FIJO / OTRO", "DIRECCIÓN DE RESIDENCIA",
        "MUNICIPIO", "SUBREGIÓN", "PROCESO"
    ]
    if not all(col in df.columns for col in columnas_requeridas):
        raise HTTPException(status_code=400, detail="Faltan columnas requeridas en el archivo")

    registros_nuevos = 0
    for _, row in df.iterrows():
        llave = (row["TIPO DE IDENTIFICACIÓN"], str(row["NUMERO DE IDENTIFICACIÓN"]), row["PROCESO"])

        existe = db.query(RegistroBase).filter_by(
            tipo_id=llave[0],
            num_id=llave[1],
            proceso=llave[2]
        ).first()

        if not existe:
            nuevo = RegistroBase(
                tipo_id=row["TIPO DE IDENTIFICACIÓN"],
                num_id=str(row["NUMERO DE IDENTIFICACIÓN"]),
                primer_nombre=row["1ER NOMBRE"],
                segundo_nombre=row.get("2DO NOMBRE"),
                primer_apellido=row["1ER APELLDO"],
                segundo_apellido=row.get("2DO APELLDO"),
                fecha=pd.to_datetime(row["FECHA"], errors='coerce'),
                edad=int(row["EDAD"]),
                estado_afiliacion=row["ESTADO DE AFILIACIÓN"],
                regimen_afiliacion=row["RÉGIMEN DE AFILIACIÓN"],
                telefonos=row["TELEFONO FIJO / OTRO"],
                direccion=row["DIRECCIÓN DE RESIDENCIA"],
                municipio=row["MUNICIPIO"],
                subregion=row["SUBREGIÓN"],
                proceso=row["PROCESO"]
            )
            db.add(nuevo)
            registros_nuevos += 1

    db.commit()
    return {"mensaje": f"Proceso completado. Se insertaron {registros_nuevos} nuevos registros."}

