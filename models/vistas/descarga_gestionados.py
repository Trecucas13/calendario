from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from io import BytesIO
from flask import send_file
from flask import Blueprint, jsonify
from database.config import db
from auth.decorators import login_required, role_required


datos_gestionados = Blueprint('datos_gestionados', __name__)
@datos_gestionados.route("/exportar_registros_excel")
@login_required
@role_required(1)
def exportar_registros_excel():
    """
    Genera un archivo Excel con los registros de la base de datos
    """
    try:
        # Obtener los datos de la base de datos
        registros = db.session.execute("""SELECT
                    g.fecha_gestion,
                    r.tipo_id, 
                    r.num_id, 
                    r.primer_nombre, 
                    r.segundo_nombre,
                    r.primer_apellido,
                    r.segundo_apellido,
                    r.fecha,
                    r.edad,
                    r.telefonos,
                    r.direccion
                    FROM registro_base r
                    JOIN gestion g ON r.id = g.registro_id
        """).fetchall()

        # Crear un nuevo libro de Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Registros"

        # Definir encabezados
        headers = [
            "Fecha Gestión", 
            "Tipo Documento",
            "Número Documento",
            "Primer Nombre",
            "Segundo Aombre",   
            "Primer Apellido",
            "Segundo Apellido",
            "Fecha Nacimiento",
            "Edad",
            "Teléfonos",
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
        for row, registro in enumerate(registros, 2):
            for col, value in enumerate(registro.values(), 1):
                cell = ws.cell(row=row, column=col, value=value)
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
            download_name='registros_historico.xlsx'
        )

    except Exception as e:
        print(f"Error al exportar a Excel: {e}")
        return jsonify({"error": str(e)}), 500