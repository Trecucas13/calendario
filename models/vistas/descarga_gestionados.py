import pandas as pd
from io import StringIO
from flask import send_file, Response
from flask import Blueprint, jsonify
from database.config import db
from auth.decorators import login_required, role_required
from sqlalchemy import text


datos_gestionados = Blueprint('datos_gestionados', __name__)

@datos_gestionados.route("/exportar_registros_csv")
@login_required
@role_required([1, 2])
def exportar_registros_csv():
    """
    Genera un archivo CSV con los registros de la base de datos usando pandas para mejor rendimiento
    """
    try:
        # Verificar que la columna cantidad_gestiones existe
        column_check = db.session.execute(
            text("""SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'registro_base' 
                    AND column_name = 'cantidad_gestiones'
                )""")
        ).scalar()
        
        if not column_check:
            print("⚠️  Columna cantidad_gestiones no existe. Creándola...")
            db.session.execute(
                text("ALTER TABLE registro_base ADD COLUMN cantidad_gestiones INTEGER DEFAULT 0")
            )
            # Inicializar valores
            db.session.execute(
                text("""UPDATE registro_base 
                        SET cantidad_gestiones = (
                            SELECT COUNT(*) 
                            FROM gestion g 
                            WHERE g.registro_id = registro_base.id
                        )""")
            )
            db.session.commit()
            print("✅ Columna cantidad_gestiones creada e inicializada")
        
        # Definir la consulta SQL corregida - sin DISTINCT para poder usar ORDER BY
        query = """
            SELECT
                r.id,
                r.tipo_id, 
                r.num_id, 
                r.primer_nombre, 
                r.segundo_nombre,
                r.primer_apellido,
                r.segundo_apellido,
                r.fecha,
                r.edad,
                r.estado_afiliacion,
                r.regimen_afiliacion,
                r.telefonos,
                r.direccion,
                r.municipio,
                r.subregion,
                r.proceso,
                -- Asegurar que cantidad_gestiones se incluya correctamente
                COALESCE(r.cantidad_gestiones, 0) as cantidad_gestiones,
                -- Datos de la gestión más reciente
                (
                    SELECT g.motivo 
                    FROM gestion g 
                    WHERE g.registro_id = r.id 
                    ORDER BY g.fecha_gestion DESC 
                    LIMIT 1
                ) as motivo,
                (
                    SELECT g.fecha_gestion 
                    FROM gestion g 
                    WHERE g.registro_id = r.id 
                    ORDER BY g.fecha_gestion DESC 
                    LIMIT 1
                ) as fecha_gestion,
                (
                    SELECT g.tipificacion 
                    FROM gestion g 
                    WHERE g.registro_id = r.id 
                    ORDER BY g.fecha_gestion DESC 
                    LIMIT 1
                ) as tipificacion,
                (
                    SELECT g.comentario 
                    FROM gestion g 
                    WHERE g.registro_id = r.id 
                    ORDER BY g.fecha_gestion DESC 
                    LIMIT 1
                ) as comentario,
                (
                    SELECT g.usuario 
                    FROM gestion g 
                    WHERE g.registro_id = r.id 
                    ORDER BY g.fecha_gestion DESC 
                    LIMIT 1
                ) as asesor
            FROM registro_base r
            ORDER BY r.id
        """
        
        # Usar pandas para leer directamente desde la base de datos
        df = pd.read_sql_query(query, db.engine)
        
        # Definir nombres de columnas más legibles (excluyendo 'id' del resultado final)
        column_names = {
            'tipo_id': 'Tipo Documento',
            'num_id': 'Número Documento',
            'primer_nombre': 'Primer Nombre',
            'segundo_nombre': 'Segundo Nombre',
            'primer_apellido': 'Primer Apellido',
            'segundo_apellido': 'Segundo Apellido',
            'fecha': 'Fecha Nacimiento',
            'edad': 'Edad',
            'estado_afiliacion': 'Estado Afiliación',
            'regimen_afiliacion': 'Régimen Afiliado',
            'telefonos': 'Teléfonos',
            'direccion': 'Dirección',
            'municipio': 'Municipio',
            'subregion': 'Subregión',
            'proceso': 'Proceso',
            'cantidad_gestiones': 'Cantidad Gestiones',
            'motivo': 'Motivo',
            'fecha_gestion': 'Fecha Gestión',
            'tipificacion': 'Tipificación',
            'comentario': 'Comentario',
            'asesor': 'Asesor'
        }
        
        # Remover la columna 'id' antes de renombrar (solo la necesitábamos para ORDER BY)
        if 'id' in df.columns:
            df = df.drop('id', axis=1)
        
        # Renombrar las columnas
        df = df.rename(columns=column_names)
        
        # Crear el archivo CSV en memoria
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8-sig', sep=';')
        csv_buffer.seek(0)
        
        # Log de confirmación para CSV
        print(f"📄 Archivo CSV generado exitosamente con {len(df)} registros")
        
        # Crear respuesta para descarga
        return Response(
            csv_buffer.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=registros_completos.csv',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )

    except Exception as e:
        print(f"Error al exportar a CSV: {e}")
        return jsonify({"error": str(e)}), 500

# Mantener también la función Excel original como alternativa
@datos_gestionados.route("/exportar_registros_excel") 
@login_required
@role_required([1, 2])
def exportar_registros_excel():
    """
    Genera un archivo Excel con los registros de la base de datos usando pandas (más rápido que openpyxl)
    """
    try:
        # Verificar que la columna cantidad_gestiones existe
        column_check = db.session.execute(
            text("""SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'registro_base' 
                    AND column_name = 'cantidad_gestiones'
                )""")
        ).scalar()
        
        if not column_check:
            print("⚠️  Columna cantidad_gestiones no existe. Creándola...")
            db.session.execute(
                text("ALTER TABLE registro_base ADD COLUMN cantidad_gestiones INTEGER DEFAULT 0")
            )
            # Inicializar valores
            db.session.execute(
                text("""UPDATE registro_base 
                        SET cantidad_gestiones = (
                            SELECT COUNT(*) 
                            FROM gestion g 
                            WHERE g.registro_id = registro_base.id
                        )""")
            )
            db.session.commit()
            print("✅ Columna cantidad_gestiones creada e inicializada")
        
        # Definir la consulta SQL optimizada - obtener datos únicos de registro_base
        query = """
            SELECT DISTINCT
                r.id,
                r.tipo_id, 
                r.num_id, 
                r.primer_nombre, 
                r.segundo_nombre,
                r.primer_apellido,
                r.segundo_apellido,
                r.fecha,
                r.edad,
                r.estado_afiliacion,
                r.regimen_afiliacion,
                r.telefonos,
                r.direccion,
                r.municipio,
                r.subregion,
                r.proceso,
                -- Asegurar que cantidad_gestiones se incluya correctamente
                COALESCE(r.cantidad_gestiones, 0) as cantidad_gestiones,
                -- Datos de la gestión más reciente
                (
                    SELECT g.motivo 
                    FROM gestion g 
                    WHERE g.registro_id = r.id 
                    ORDER BY g.fecha_gestion DESC 
                    LIMIT 1
                ) as motivo,
                (
                    SELECT g.fecha_gestion 
                    FROM gestion g 
                    WHERE g.registro_id = r.id 
                    ORDER BY g.fecha_gestion DESC 
                    LIMIT 1
                ) as fecha_gestion,
                (
                    SELECT g.tipificacion 
                    FROM gestion g 
                    WHERE g.registro_id = r.id 
                    ORDER BY g.fecha_gestion DESC 
                    LIMIT 1
                ) as tipificacion,
                (
                    SELECT g.comentario 
                    FROM gestion g 
                    WHERE g.registro_id = r.id 
                    ORDER BY g.fecha_gestion DESC 
                    LIMIT 1
                ) as comentario,
                (
                    SELECT g.usuario 
                    FROM gestion g 
                    WHERE g.registro_id = r.id 
                    ORDER BY g.fecha_gestion DESC 
                    LIMIT 1
                ) as asesor
            FROM registro_base r
            ORDER BY r.id
        """
        
        # Usar pandas para leer directamente desde la base de datos
        df = pd.read_sql_query(query, db.engine)
        
        # Definir nombres de columnas más legibles
        column_names = {
            'tipo_id': 'Tipo Documento',
            'num_id': 'Número Documento',
            'primer_nombre': 'Primer Nombre',
            'segundo_nombre': 'Segundo Nombre',
            'primer_apellido': 'Primer Apellido',
            'segundo_apellido': 'Segundo Apellido',
            'fecha': 'Fecha Nacimiento',
            'edad': 'Edad',
            'estado_afiliacion': 'Estado Afiliación',
            'regimen_afiliacion': 'Régimen Afiliado',
            'telefonos': 'Teléfonos',
            'direccion': 'Dirección',
            'municipio': 'Municipio',
            'subregion': 'Subregión',
            'proceso': 'Proceso',
            'cantidad_gestiones': 'Cantidad Gestiones',
            'motivo': 'Motivo',
            'fecha_gestion': 'Fecha Gestión',
            'tipificacion': 'Tipificación',
            'comentario': 'Comentario',
            'asesor': 'Asesor'
        }
        
        # Remover la columna 'id' antes de renombrar (solo la necesitábamos para ORDER BY)
        if 'id' in df.columns:
            df = df.drop('id', axis=1)
        
        # Renombrar las columnas
        df = df.rename(columns=column_names)
        
        # Log de confirmación para Excel
        if 'Cantidad Gestiones' in df.columns:
            total_gestiones = df['Cantidad Gestiones'].sum()
            registros_con_gestiones = df[df['Cantidad Gestiones'] > 0].shape[0]
            print(f"✅ Excel: Exportando {len(df)} registros con {total_gestiones} gestiones total")
            print(f"📊 Excel: {registros_con_gestiones} registros tienen gestiones")
        
        # Crear el archivo Excel en memoria usando pandas (más rápido que openpyxl)
        from io import BytesIO
        excel_buffer = BytesIO()
        
        # Escribir a Excel con pandas (incluye autoajuste de columnas automáticamente)
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Registros', index=False)
            
            # Obtener la hoja y aplicar estilos
            workbook = writer.book
            worksheet = writer.sheets['Registros']
            
            # Aplicar estilo a los encabezados
            from openpyxl.styles import Font, PatternFill
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)
            
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
            
            # Autoajustar el ancho de las columnas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # Máximo 50 caracteres
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        excel_buffer.seek(0)
        
        # Crear respuesta para descarga
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='registros_completos.xlsx'
        )

    except Exception as e:
        print(f"Error al exportar a Excel: {e}")
        return jsonify({"error": str(e)}), 500