from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from io import BytesIO
from flask import send_file
from flask import Blueprint, jsonify
from database.config import db
from auth.decorators import login_required, role_required
from sqlalchemy import text  # Importar text


datos_citas = Blueprint('datos_citas', __name__)
@datos_citas.route("/exportar_registrosExcel")
@login_required
@role_required(1)
def exportar_registrosExcel():
    """
    Genera un archivo Excel con los registros de la base de datos
    """
    try:
        # Obtener los datos de la base de datos
        registros = db.session.execute(text("""
            SELECT
                cal.nombre_calendario,
                c.fecha,
                c.hora,
                p.nombre,
                p.apellido,
                p.tipo_documento,
                p.numero_documento,
                p.fecha_nacimiento,
                p.telefono,
                p.direccion
            FROM citas c
            INNER JOIN pacientes p ON c.id_paciente = p.id
            INNER JOIN calendarios cal ON c.id_calendario = cal.id_calendario
        """)).fetchall()
        print(f"Registros obtenidos: {registros}")  # Para ver cuántos registros se obtienen

        # Crear un nuevo libro de Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Registros"

        # Definir encabezados
        headers = [
            "Nombre Calendario",
            "Fecha Cita", 
            "Hora Cita",
            "Nombre",
            "Apellido",
            "Tipo Documento",
            "Número Documento",
            "Fecha Nacimiento",
            # "Edad",
            "Teléfono",
            "Dirección"
        ]

        # Estilo para encabezados
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        
        # Agregar encabezados
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        # Agregar datos
        for row_idx, registro in enumerate(registros, 2):
            for col_idx, value in enumerate(registro, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.alignment = Alignment(horizontal="center")

        # Ajustar ancho de columnas
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width

        # Guardar el archivo en memoria
        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)

        # Crear respuesta para descarga
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='registros_pacientes.xlsx'
        )

    except Exception as e:
        print(f"Error al exportar a Excel: {e}")
        return jsonify({"error": str(e)}), 500