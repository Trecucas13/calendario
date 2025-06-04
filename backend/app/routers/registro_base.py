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

# Dependencia para obtener la sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=RegistroBaseResponse)
def crear_registro(data: RegistroBaseCreate, db: Session = Depends(get_db)):
    return crud.create_registro(db, data)

@router.get("/listar_historico", response_model=List[RegistroBaseResponse])
def listar_registros(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_registros(db, skip, limit)

@router.get("/completo/", response_model=List[RegistroBaseResponse])
def listar_registros_completos(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return crud.get_registros_completos(db, skip, limit)

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

        row_dict = row.to_dict()
        for key in row_dict:
            if pd.isna(row_dict[key]):
                row_dict[key] = None

        llave = (row_dict["TIPO DE IDENTIFICACIÓN"], 
                str(row_dict["NUMERO DE IDENTIFICACIÓN"]), 
                row_dict["PROCESO"])

        existe = db.query(RegistroBase).filter_by(
            tipo_id=llave[0],
            num_id=llave[1],
            proceso=llave[2]
        ).first()

        if not existe:
            nuevo = RegistroBase(
                tipo_id=row_dict["TIPO DE IDENTIFICACIÓN"],
                num_id=str(row_dict["NUMERO DE IDENTIFICACIÓN"]),
                primer_nombre=row_dict["1ER NOMBRE"],
                segundo_nombre=row_dict.get("2DO NOMBRE"),
                primer_apellido=row_dict["1ER APELLDO"],
                segundo_apellido=row_dict.get("2DO APELLDO"),
                fecha=pd.to_datetime(row_dict["FECHA"], errors='coerce'),
                edad=int(row_dict["EDAD"]) if not pd.isna(row_dict["EDAD"]) else None,
                estado_afiliacion=row_dict["ESTADO DE AFILIACIÓN"],
                regimen_afiliacion=row_dict["RÉGIMEN DE AFILIACIÓN"],
                telefonos=row_dict["TELEFONO FIJO / OTRO"],
                direccion=row_dict["DIRECCIÓN DE RESIDENCIA"],
                municipio=row_dict["MUNICIPIO"],
                subregion=row_dict["SUBREGIÓN"],
                proceso=row_dict["PROCESO"]
            )
            db.add(nuevo)
            registros_nuevos += 1

    try:
        db.commit()
        return {"mensaje": f"Proceso completado. Se insertaron {registros_nuevos} nuevos registros."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

