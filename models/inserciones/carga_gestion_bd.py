from flask import Blueprint, request, jsonify, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from io import BytesIO, StringIO
import pandas as pd
import csv
import psycopg2
import os

from tiempo_funcion import benchmark_guardado  # Importa la función de benchmarking
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
            # Para archivos grandes, leer en chunks y usar configuraciones optimizadas
            df = pd.read_excel(BytesIO(content), engine='openpyxl', 
                             dtype=str,  # Leer todo como string para evitar problemas de tipo
                             na_filter=False)  # No convertir strings vacíos a NaN
        else:
            df = pd.read_csv(BytesIO(content), dtype=str, na_filter=False)
            
        print(f"Archivo cargado: {len(df)} registros encontrados")
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

    # Procesar datos en lotes para mejorar rendimiento (optimizado para archivos grandes)
    registros_nuevos = []
    registros_existentes = set()
    
    # Para archivos muy grandes, procesar la verificación en chunks
    CHUNK_SIZE = 10000  # Aumentar tamaño de chunk para menos consultas
    
    print("Preparando datos para verificación de duplicados...")
    
    # Convertir DataFrame a lista de diccionarios una sola vez
    df_records = df.to_dict('records')
    total_records = len(df_records)
    
    # Usar conexión directa de PostgreSQL para mejor rendimiento
    pg_conn = None
    try:
        pg_conn = get_postgres_connection()
        pg_conn.autocommit = False  # Usar transacciones manuales
        cursor = pg_conn.cursor()
        
        # Procesar en chunks para verificar registros existentes
        for chunk_start in range(0, total_records, CHUNK_SIZE):
            chunk_end = min(chunk_start + CHUNK_SIZE, total_records)
            chunk_records = df_records[chunk_start:chunk_end]
            
            print(f"Verificando duplicados en chunk {chunk_start//CHUNK_SIZE + 1}/{(total_records-1)//CHUNK_SIZE + 1}")
            
            # Extraer combinaciones del chunk actual
            combinaciones_chunk = []
            for record in chunk_records:
                # Procesar valores NaN/None más eficientemente
                tipo_id = str(record.get("TIPO DE IDENTIFICACIÓN", "")).strip()
                num_id = str(record.get("NUMERO DE IDENTIFICACIÓN", "")).strip()
                proceso = str(record.get("PROCESO", "")).strip()
                
                if tipo_id and num_id and proceso:  # Solo procesar si tiene valores válidos
                    combinaciones_chunk.append((tipo_id, num_id, proceso))
            
            # Consulta masiva para verificar registros existentes del chunk
            if combinaciones_chunk:
                # Usar consulta preparada más eficiente
                placeholders = ','.join(['(%s,%s,%s)'] * len(combinaciones_chunk))
                query_existentes = f"""
                    SELECT tipo_id, num_id, proceso 
                    FROM registro_base 
                    WHERE (tipo_id, num_id, proceso) IN (VALUES {placeholders})
                """
                
                # Aplanar la lista de tuplas para los parámetros
                params = [item for tupla in combinaciones_chunk for item in tupla]
                
                try:
                    cursor.execute(query_existentes, params)
                    resultados_existentes = cursor.fetchall()
                    # Agregar a set de existentes
                    chunk_existentes = set((r[0], r[1], r[2]) for r in resultados_existentes)
                    registros_existentes.update(chunk_existentes)
                except Exception as e:
                    print(f"Error en verificación de chunk: {e}")
                    # Continuar con el siguiente chunk si hay error
        
        cursor.close()
        
    except Exception as e:
        print(f"Error conectando a PostgreSQL: {e}")
        # Fallback a SQLAlchemy si falla la conexión directa
        return jsonify({'error': f'Error de conexión a base de datos: {str(e)}'}), 500
    finally:
        if pg_conn:
            pg_conn.close()
    
    print(f"Registros existentes encontrados: {len(registros_existentes)}")
    
    # Preparar registros para inserción masiva
    print("Preparando registros nuevos para inserción...")
    
    for i, record in enumerate(df_records):
        if i % 10000 == 0:
            print(f"Procesando registro {i+1}/{total_records}")
            
        # Procesar cada registro
        tipo_id = str(record.get("TIPO DE IDENTIFICACIÓN", "")).strip()
        num_id = str(record.get("NUMERO DE IDENTIFICACIÓN", "")).strip()
        proceso = str(record.get("PROCESO", "")).strip()

        # Verificar si el registro ya existe
        if (tipo_id, num_id, proceso) not in registros_existentes:
            # Procesar fecha de manera más robusta
            fecha_str = str(record.get("FECHA", "")).strip()
            fecha_val = None
            if fecha_str:
                try:
                    fecha_val = pd.to_datetime(fecha_str, errors='coerce')
                    if pd.isna(fecha_val):
                        fecha_val = None
                    else:
                        fecha_val = fecha_val.to_pydatetime()
                except:
                    fecha_val = None
            
            # Procesar edad de manera más robusta
            edad_val = None
            edad_str = str(record.get("EDAD", "")).strip()
            if edad_str and edad_str.isdigit():
                try:
                    edad_val = int(edad_str)
                except:
                    edad_val = None
            
            registro = {
                "tipo_id": tipo_id,
                "num_id": num_id,
                "primer_nombre": str(record.get("1ER NOMBRE", "")).strip(),
                "segundo_nombre": str(record.get("2DO NOMBRE", "")).strip() or None,
                "primer_apellido": str(record.get("1ER APELLDO", "")).strip(),
                "segundo_apellido": str(record.get("2DO APELLDO", "")).strip() or None,
                "fecha": fecha_val,
                "edad": edad_val,
                "estado_afiliacion": str(record.get("ESTADO DE AFILIACIÓN", "")).strip(),
                "regimen_afiliacion": str(record.get("RÉGIMEN DE AFILIACIÓN", "")).strip(),
                "telefonos": str(record.get("TELEFONO FIJO / OTRO", "")).strip(),
                "direccion": str(record.get("DIRECCIÓN DE RESIDENCIA", "")).strip(),
                "municipio": str(record.get("MUNICIPIO", "")).strip(),
                "subregion": str(record.get("SUBREGIÓN", "")).strip(),
                "proceso": proceso
            }
            registros_nuevos.append(registro)
    
    # Inserción masiva usando COPY directo con psycopg2 (máximo rendimiento)
    nuevos = len(registros_nuevos)
    print(f"Preparando inserción de {nuevos} registros nuevos...")
    
    if registros_nuevos:
        pg_conn = None
        try:
            # Usar conexión directa de PostgreSQL para máximo rendimiento
            pg_conn = get_postgres_connection()
            pg_conn.autocommit = False  # Control manual de transacciones
            cursor = pg_conn.cursor()
            
            # Crear buffer CSV completo en memoria (más eficiente para COPY)
            print("Creando buffer CSV para COPY...")
            csv_buffer = StringIO()
            csv_writer = csv.writer(csv_buffer, delimiter='\t ', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            # Escribir todos los datos al buffer de una vez
            for i, registro in enumerate(registros_nuevos):
                if i % 50000 == 0 and i > 0:
                    print(f"Preparando registro {i}/{nuevos} para COPY...")
                
                # Formatear fecha como string para COPY
                fecha_str = registro['fecha'].strftime('%Y-%m-%d %H:%M:%S') if registro['fecha'] else None
                
                row_data = [
                    registro['tipo_id'] or None,
                    registro['num_id'] or None,
                    registro['primer_nombre'] or None,
                    registro['segundo_nombre'],
                    registro['primer_apellido'] or None,
                    registro['segundo_apellido'],
                    fecha_str,
                    str(registro['edad']) if registro['edad'] is not None else None,
                    registro['estado_afiliacion'] or None,
                    registro['regimen_afiliacion'] or None,
                    registro['telefonos'] or None,
                    registro['direccion'] or None,
                    registro['municipio'] or None,
                    registro['subregion'] or None,
                    registro['proceso'] or None
                ]
                csv_writer.writerow(row_data)
            
            # Obtener el contenido del buffer
            csv_data = csv_buffer.getvalue()
            csv_buffer.close()
            
            print("Ejecutando COPY masivo...")
            
            # Crear StringIO con los datos CSV
            data_io = StringIO(csv_data)
            
            # Ejecutar COPY FROM - La forma más rápida de insertar en PostgreSQL
            cursor.copy_expert("""
                COPY registro_base (
                    tipo_id, num_id, primer_nombre, segundo_nombre,
                    primer_apellido, segundo_apellido, fecha, edad,
                    estado_afiliacion, regimen_afiliacion, telefonos,
                    direccion, municipio, subregion, proceso
                ) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t', NULL '', QUOTE '"')
            """, data_io)
            
            # Commit la transacción
            pg_conn.commit()
            cursor.close()
            
            print("COPY masivo completado exitosamente")
                
        except Exception as copy_error:
            # Si COPY falla, hacer rollback y usar fallback
            print(f"COPY masivo falló ({str(copy_error)}), usando fallback con psycopg2...")
            if pg_conn:
                pg_conn.rollback()
                cursor = pg_conn.cursor()
                
                # Fallback usando INSERT con psycopg2 (más rápido que SQLAlchemy)
                BATCH_SIZE = 5000  # Lotes más grandes con psycopg2
                
                try:
                    for i in range(0, len(registros_nuevos), BATCH_SIZE):
                        lote = registros_nuevos[i:i + BATCH_SIZE]
                        
                        if i % 25000 == 0:
                            print(f"Insertando lote {i//BATCH_SIZE + 1}/{(len(registros_nuevos)-1)//BATCH_SIZE + 1}")
                        
                        # Preparar datos para inserción por lotes
                        insert_data = []
                        for registro in lote:
                            fecha_val = registro['fecha'] if registro['fecha'] else None
                            insert_data.append((
                                registro['tipo_id'],
                                registro['num_id'],
                                registro['primer_nombre'],
                                registro['segundo_nombre'],
                                registro['primer_apellido'],
                                registro['segundo_apellido'],
                                fecha_val,
                                registro['edad'],
                                registro['estado_afiliacion'],
                                registro['regimen_afiliacion'],
                                registro['telefonos'],
                                registro['direccion'],
                                registro['municipio'],
                                registro['subregion'],
                                registro['proceso']
                            ))
                        
                        # Usar execute_values para inserción por lotes eficiente
                        from psycopg2.extras import execute_values
                        execute_values(
                            cursor,
                            """INSERT INTO registro_base 
                               (tipo_id, num_id, primer_nombre, segundo_nombre,
                                primer_apellido, segundo_apellido, fecha, edad,
                                estado_afiliacion, regimen_afiliacion, telefonos,
                                direccion, municipio, subregion, proceso)
                               VALUES %s""",
                            insert_data,
                            template=None,
                            page_size=1000  # Procesar en páginas de 1000
                        )
                        
                        # Commit cada lote grande para evitar bloqueos largos
                        if (i // BATCH_SIZE + 1) % 5 == 0:
                            pg_conn.commit()
                    
                    # Commit final
                    pg_conn.commit()
                    cursor.close()
                    print("Inserción por lotes completada exitosamente")
                    
                except Exception as batch_error:
                    pg_conn.rollback()
                    if cursor:
                        cursor.close()
                    return jsonify({'error': f'Error en inserción por lotes: {str(batch_error)}'}), 500
            else:
                return jsonify({'error': f'Error en COPY y no se pudo establecer conexión: {str(copy_error)}'}), 500
        
        finally:
            if pg_conn:
                pg_conn.close()

    # Retorno exitoso - no necesitamos commit adicional ya que se hizo en psycopg2
    print(f"Carga completada exitosamente: {nuevos} registros procesados")
    
    # Ejecutar benchmark después del procesamiento exitoso
    benchmark_guardado(lambda: print(f"Procesados {nuevos} registros nuevos"), repeticiones=1)
    return redirect(url_for('index'))

def get_postgres_connection():
    """Obtener conexión directa a PostgreSQL sin SQLAlchemy"""
    # Obtener configuración de la base de datos desde SQLAlchemy
    engine = db.get_engine()
    url = engine.url
    
    # Crear conexión directa con psycopg2
    connection = psycopg2.connect(
        host=url.host,
        port=url.port or 5432,
        database=url.database,
        user=url.username,
        password=url.password
    )
    return connection
