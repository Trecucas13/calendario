from flask import Blueprint, request, jsonify, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from io import BytesIO
import pandas as pd

from database.config import db

gestion_bp = Blueprint('gestion_bp', __name__)

@gestion_bp.route('/carga_gestion', methods=['POST'])
def carga_gestion():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No se ha enviado ningún archivo'}), 400

    if not file.filename.endswith(('.xlsx', '.csv')):
        return jsonify({'error': 'Formato no soportado. Usa .xlsx o .csv'}), 400

    content = file.read()
    try:
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(content), engine='openpyxl')
        else:
            df = pd.read_csv(BytesIO(content))
    except Exception as e:
        return jsonify({'error': f'Error leyendo archivo: {str(e)}'}), 400

    columnas_requeridas = [
        "TIPO DE IDENTIFICACIÓN", "NUMERO DE IDENTIFICACIÓN", "1ER NOMBRE", "2DO NOMBRE",
        "1ER APELLDO", "2DO APELLDO", "FECHA", "EDAD", "ESTADO DE AFILIACIÓN",
        "RÉGIMEN DE AFILIACIÓN", "TELEFONO FIJO / OTRO", "DIRECCIÓN DE RESIDENCIA",
        "MUNICIPIO", "SUBREGIÓN", "PROCESO"
    ]
    if not all(col in df.columns for col in columnas_requeridas):
        return jsonify({'error': 'Faltan columnas requeridas en el archivo'}), 400

    nuevos = 0
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        # — reemplazar NaN por None —
        for k, v in row_dict.items():
            if pd.isna(v):
                row_dict[k] = None

        tipo_id = row_dict["TIPO DE IDENTIFICACIÓN"]
        num_id = str(row_dict["NUMERO DE IDENTIFICACIÓN"])
        proceso = row_dict["PROCESO"]

        existe = db.session.execute(
            text("SELECT 1 FROM registro_base WHERE tipo_id=:tipo_id AND num_id=:num_id AND proceso=:proceso"),
            {"tipo_id": tipo_id, "num_id": num_id, "proceso": proceso}
        ).fetchone()

        if not existe:
            fecha_val = pd.to_datetime(row_dict["FECHA"], errors='coerce')
            params = {
                "tipo_id": tipo_id,
                "num_id": num_id,
                "primer_nombre": row_dict["1ER NOMBRE"],
                "segundo_nombre": row_dict.get("2DO NOMBRE"),
                "primer_apellido": row_dict["1ER APELLDO"],
                "segundo_apellido": row_dict.get("2DO APELLDO"),
                "fecha": fecha_val.to_pydatetime() if fecha_val is not pd.NaT else None,
                "edad": int(row_dict["EDAD"]) if row_dict.get("EDAD") is not None else None,
                "estado_afiliacion": row_dict["ESTADO DE AFILIACIÓN"],
                "regimen_afiliacion": row_dict["RÉGIMEN DE AFILIACIÓN"],
                "telefonos": row_dict["TELEFONO FIJO / OTRO"],
                "direccion": row_dict["DIRECCIÓN DE RESIDENCIA"],
                "municipio": row_dict["MUNICIPIO"],
                "subregion": row_dict["SUBREGIÓN"],
                "proceso": proceso
            }

            db.session.execute(text("""
                INSERT INTO registro_base
                  (tipo_id, num_id, primer_nombre, segundo_nombre,
                   primer_apellido, segundo_apellido, fecha, edad,
                   estado_afiliacion, regimen_afiliacion, telefonos,
                   direccion, municipio, subregion, proceso)
                VALUES
                  (:tipo_id, :num_id, :primer_nombre, :segundo_nombre,
                   :primer_apellido, :segundo_apellido, :fecha, :edad,
                   :estado_afiliacion, :regimen_afiliacion, :telefonos,
                   :direccion, :municipio, :subregion, :proceso)
            """), params)
            nuevos += 1

    try:
        db.session.commit()
        return redirect(url_for('index'))
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500