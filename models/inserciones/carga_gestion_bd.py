from flask import Blueprint, request, jsonify, send_file
from sqlalchemy.exc import SQLAlchemyError
from io import BytesIO, StringIO
import pandas as pd
import csv
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import os
import re

from tiempo_funcion import benchmark_guardado
from database.config import db
from auth.decorators import login_required, role_required

gestion_bp = Blueprint('gestion_bp', __name__)

# Mapeo de columnas
COLUMN_MAPPING = {
    "TIPO DE IDENTIFICACIÓN": "tipo_id",
    "NUMERO DE IDENTIFICACIÓN": "num_id",
    "1ER NOMBRE": "primer_nombre",
    "2DO NOMBRE": "segundo_nombre",
    "1ER APELLDO": "primer_apellido",
    "2DO APELLDO": "segundo_apellido",
    "FECHA": "fecha",
    "EDAD": "edad",
    "ESTADO DE AFILIACIÓN": "estado_afiliacion",
    "RÉGIMEN DE AFILIACIÓN": "regimen_afiliacion",
    "TELEFONO FIJO / OTRO": "telefonos",
    "DIRECCIÓN DE RESIDENCIA": "direccion",
    "MUNICIPIO": "municipio",
    "SUBREGIÓN": "subregion",
    "PROCESO": "proceso"
}

COLUMNAS_ORDEN = list(COLUMN_MAPPING.values())

def get_postgres_connection():
    """Obtener conexión directa a PostgreSQL"""
    engine = db.get_engine()
    url = engine.url
    return psycopg2.connect(
        host=url.host,
        port=url.port or 5432,
        database=url.database,
        user=url.username,
        password=url.password
    )

def create_temp_table(cursor):
    """Crear tabla temporal para staging"""
    cursor.execute("""
    CREATE TEMP TABLE staging_data (
        tipo_id TEXT,
        num_id TEXT,
        primer_nombre TEXT,
        segundo_nombre TEXT,
        primer_apellido TEXT,
        segundo_apellido TEXT,
        fecha TEXT,  -- Cambiado a TEXT para manejar cualquier formato
        edad INTEGER,
        estado_afiliacion TEXT,
        regimen_afiliacion TEXT,
        telefonos TEXT,
        direccion TEXT,
        municipio TEXT,
        subregion TEXT,
        proceso TEXT
    )
    """)

def normalizar_fecha(fecha_str):
    """Convertir diferentes formatos de fecha a YYYY-MM-DD"""
    if not fecha_str or pd.isna(fecha_str):
        return None
    
    # Intentar convertir con pandas
    try:
        fecha = pd.to_datetime(fecha_str, dayfirst=True, errors='coerce')
        if not pd.isna(fecha):
            return fecha.strftime('%Y-%m-%d')
    except:
        pass
    
    # Manejar formatos específicos
    try:
        # Formato DD/MM/YYYY
        if re.match(r'\d{1,2}/\d{1,2}/\d{4}', str(fecha_str)):
            dia, mes, anio = fecha_str.split('/')
            return f"{anio}-{mes.zfill(2)}-{dia.zfill(2)}"
        
        # Formato DD-MM-YYYY
        elif re.match(r'\d{1,2}-\d{1,2}-\d{4}', str(fecha_str)):
            dia, mes, anio = fecha_str.split('-')
            return f"{anio}-{mes.zfill(2)}-{dia.zfill(2)}"
        
        # Formato YYYYMMDD
        elif re.match(r'\d{8}', str(fecha_str)):
            return f"{fecha_str[:4]}-{fecha_str[4:6]}-{fecha_str[6:8]}"
        
    except:
        pass
    
    return None

def procesar_dataframe(df):
    """Procesar y limpiar el DataFrame"""
    # Renombrar columnas
    df = df.rename(columns=COLUMN_MAPPING)
    
    # Eliminar duplicados
    df = df.drop_duplicates(subset=['tipo_id', 'num_id', 'proceso'])
    
    # Normalizar fechas
    if 'fecha' in df.columns:
        df['fecha'] = df['fecha'].apply(normalizar_fecha)
    
    # Procesar edad
    if 'edad' in df.columns:
        df['edad'] = pd.to_numeric(df['edad'], errors='coerce').astype('Int64')
    
    # Ordenar columnas
    return df[COLUMNAS_ORDEN]

def cargar_datos_staging(cursor, df):
    """Cargar datos a la tabla temporal"""
    with StringIO() as csv_buffer:
        # Usar quoting para campos que podrían contener comas
        df.to_csv(csv_buffer, index=False, header=False, sep='\t', 
                 na_rep='\\N', quoting=csv.QUOTE_MINIMAL)
        csv_buffer.seek(0)
        
        cursor.copy_expert(
            "COPY staging_data FROM STDIN WITH (FORMAT CSV, DELIMITER E'\t', NULL '\\N')",
            csv_buffer
        )

def handle_duplicates(cursor):
    """Manejar duplicados entre el archivo y la base de datos"""
    # Paso 1: Eliminar registros existentes que coinciden con los nuevos
    cursor.execute("""
    DELETE FROM registro_base r
    USING staging_data s
    WHERE r.tipo_id = s.tipo_id
        AND r.num_id = s.num_id
        AND r.proceso = s.proceso
    RETURNING r.id, r.tipo_id, r.num_id, r.primer_nombre, 
              r.primer_apellido, r.segundo_apellido, r.municipio, r.proceso
    """)
    deleted_records = cursor.fetchall()
    
    # Paso 2: Insertar nuevos registros con manejo de conflictos
    cursor.execute("""
    INSERT INTO registro_base (
        tipo_id, num_id, primer_nombre, segundo_nombre,
        primer_apellido, segundo_apellido, fecha, edad,
        estado_afiliacion, regimen_afiliacion, telefonos,
        direccion, municipio, subregion, proceso
    )
    SELECT 
        tipo_id, num_id, primer_nombre, segundo_nombre,
        primer_apellido, segundo_apellido, 
        CASE WHEN fecha ~ '^\d{4}-\d{2}-\d{2}$' THEN fecha::DATE ELSE NULL END,
        edad,
        estado_afiliacion, regimen_afiliacion, telefonos,
        direccion, municipio, subregion, proceso
    FROM staging_data
    ON CONFLICT (tipo_id, num_id, proceso) DO NOTHING
    """)
    
    return deleted_records, cursor.rowcount

@gestion_bp.route('/carga_gestion', methods=['POST'])
@login_required
@role_required([1, 2])
def carga_gestion():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No se ha enviado ningún archivo'}), 400

    if not file.filename.endswith(('.xlsx', '.csv')):
        return jsonify({'error': 'Formato no soportado. Usa .xlsx o .csv'}), 400

    try:
        # Leer archivo
        content = file.read()
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(content), engine='openpyxl', dtype=str, na_filter=False)
        else:
            df = pd.read_csv(BytesIO(content), dtype=str, na_filter=False)
        
        print(f"Archivo cargado: {len(df)} registros encontrados")
        
        # Validar columnas requeridas
        columnas_requeridas = list(COLUMN_MAPPING.keys())
        if not all(col in df.columns for col in columnas_requeridas):
            return jsonify({'success': False, 'error': 'Faltan columnas requeridas en el archivo'}), 400
        
        # Procesar DataFrame
        df = procesar_dataframe(df)
        print("DataFrame procesado y limpiado")
        
        # Conexión a la base de datos
        pg_conn = get_postgres_connection()
        pg_conn.autocommit = False
        cursor = pg_conn.cursor()
        
        # Crear tabla temporal
        create_temp_table(cursor)
        print("Tabla temporal creada")
        
        # Cargar datos a staging
        cargar_datos_staging(cursor, df)
        print("Datos cargados en tabla temporal")
        
        # Manejar duplicados e insertar
        deleted_records, new_records_count = handle_duplicates(cursor)
        
        # Commit de todas las operaciones
        pg_conn.commit()
        print(f"Operaciones completadas: {len(deleted_records)} duplicados eliminados, {new_records_count} nuevos registros insertados")
        
        # Preparar información de duplicados
        duplicates_info = []
        for record in deleted_records:
            duplicates_info.append({
                'id': record[0],
                'tipo_id': record[1],
                'num_id': record[2],
                'primer_nombre': record[3],
                'primer_apellido': record[4],
                'segundo_apellido': record[5] or '',
                'municipio': record[6],
                'proceso': record[7]
            })
        
        # Retornar resultados
        response_data = {
            'success': True,
            'nuevos_registros': new_records_count,
            'duplicados_eliminados': len(deleted_records),
            'duplicados_info': duplicates_info[:100]  # Limitar a 100 para el modal
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        # Manejo de errores
        if 'pg_conn' in locals() and pg_conn:
            pg_conn.rollback()
        return jsonify({
            'success': False, 
            'error': f'Error en el proceso: {str(e)}'
        }), 500
        
    finally:
        # Limpieza final
        if 'pg_conn' in locals() and pg_conn:
            cursor.close()
            pg_conn.close()

@gestion_bp.route('/eliminar_base', methods=['POST'])
@login_required
@role_required([1, 2])
def eliminar_base():
    try:
        # Conexión a la base de datos
        pg_conn = get_postgres_connection()
        cursor = pg_conn.cursor()

        # Eliminar todos los registros de la tabla
        cursor.execute("DELETE FROM registro_base")
        pg_conn.commit()

        return jsonify({
            'success': True,
            'message': 'Todos los registros han sido eliminados correctamente.'
        })

    except Exception as e:
        # Manejo de errores
        if 'pg_conn' in locals() and pg_conn:
            pg_conn.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al eliminar la base: {str(e)}'
        }), 500

    finally:
        # Limpieza final
        if 'pg_conn' in locals() and pg_conn:
            cursor.close()
            pg_conn.close()

@gestion_bp.route('/exportar_excel', methods=['GET'])
@login_required
@role_required([1, 2])
def exportar_excel():
    try:
        # Conexión a la base de datos
        pg_conn = get_postgres_connection()
        cursor = pg_conn.cursor()

        # Consultar todos los registros
        cursor.execute("SELECT * FROM registro_base")
        registros = cursor.fetchall()

        # Obtener nombres de columnas
        columnas = [desc[0] for desc in cursor.description]

        # Crear DataFrame
        df = pd.DataFrame(registros, columns=columnas)

        # Generar archivo Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Registros")
        output.seek(0)

        # Enviar archivo al cliente
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name="registros.xlsx")

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al exportar los registros: {str(e)}'
        }), 500

    finally:
        if 'pg_conn' in locals() and pg_conn:
            cursor.close()
            pg_conn.close()