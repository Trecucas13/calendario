from flask import Flask, render_template, Blueprint, flash, redirect, url_for, request, session, make_response
from database.config import mysql
from datetime import datetime, timedelta
from calendar import monthrange
from flask import Flask, Blueprint, render_template, jsonify
from auth.decorators import *
from flask_mysqldb import MySQLdb, cursors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # Estilos para el PDF
from reportlab.lib.enums import TA_CENTER, TA_LEFT  # Alineación de texto
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer  # Componentes para el PDF
from reportlab.lib.pagesizes import A3, landscape  # Tamaños de página
from reportlab.lib import colors  # Colores para el PDF
from io import BytesIO  # Para manejar el PDF en memoria
from datetime import datetime  # Para fechas y horas
import os  # Para manejo de rutas de archivos
import traceback


app = Flask(__name__)

tabla_calendarios = Blueprint('tabla_calendarios', __name__)
calendarios_creados = Blueprint('calendarios_creados', __name__)

def datos_calendario():
    try:
        # Use DictCursor instead of dictionary=True
        # id_usuario = session.get('id')
        conn = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        conn.execute("""SELECT c.*, p.nombre AS nombreProcedimiento, m.nombre AS nombreMunicipio FROM calendarios c
                        JOIN procedimientos p ON c.id_procedimiento = p.id_procedimiento
                        JOIN municipios m ON c.id_municipio = m.id_municipio
                        """)
        datos = conn.fetchall()
        conn.close()

        # Formatear las fechas antes de devolver los datos
        for calendario in datos:
            if 'fecha_inicio' in calendario and calendario['fecha_inicio']:
                calendario['fecha_inicio'] = calendario['fecha_inicio'].strftime('%Y-%m-%d')
            if 'fecha_fin' in calendario and calendario['fecha_fin']:
                calendario['fecha_fin'] = calendario['fecha_fin'].strftime('%Y-%m-%d')

        # return redirect(url_for("index"))
        return datos
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        return []


def obtener_procedimientos():
    try:
        conn = mysql.connection.cursor()
        conn.execute("SELECT * FROM procedimientos")
        procedimientos = conn.fetchall()
        conn.close()
        return procedimientos
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        return []


def generar_semanas(fecha_inicio, fecha_fin):
    # Convertir strings a objetos date
    inicio = fecha_inicio
    fin = fecha_fin
    
    if inicio > fin:
        raise ValueError("La fecha de inicio no puede ser mayor a la fecha final")

    # Encontrar el lunes anterior o igual a la fecha de inicio
    dias_hasta_lunes = inicio.weekday()  # 0 es lunes, 1 es martes, etc.
    lunes_inicio = inicio - timedelta(days=dias_hasta_lunes)
    
    # Encontrar el domingo posterior o igual a la fecha de fin
    dias_hasta_domingo = 6 - fin.weekday()  # 6 - weekday para llegar al domingo
    domingo_fin = fin + timedelta(days=dias_hasta_domingo)
    
    # Generar todas las fechas en el rango ampliado
    delta = domingo_fin - lunes_inicio
    todas_fechas = [lunes_inicio + timedelta(days=i) for i in range(delta.days + 1)]
    
    # Organizar en semanas
    semanas = []
    semana_actual = []
    
    for fecha in todas_fechas:
        # Determinar si la fecha está dentro del rango original
        dentro_rango = inicio <= fecha <= fin
        
        semana_actual.append({
            "dia": fecha.day,
            "mes": fecha.month,
            "año": fecha.year,
            "fecha_completa": fecha.strftime('%Y-%m-%d'),
            "hoy": fecha == datetime.now().date(),
            "dentro_rango": dentro_rango
        })
        # print(semana_actual)
        
        if fecha.weekday() == 6:  # Domingo
            semanas.append(semana_actual)
            semana_actual = []
    
    if semana_actual:  # Añadir la última semana incompleta
        semanas.append(semana_actual)
    
    return semanas

@tabla_calendarios.route("/calendario/<int:id_calendario>", methods=["GET", "POST"])
@login_required
@role_required([1, 2])
def calendario(id_calendario):
    try:
        conn = mysql.connection.cursor()
        conn.execute("SELECT * FROM calendarios WHERE id_calendario = %s", (id_calendario,))
        calendario = conn.fetchone()

        conn.execute("SELECT * FROM citas WHERE id_calendario = %s", (id_calendario,))
        citas = conn.fetchall()
        # print(citas)
        conn.close()  
        
        
        inicio_hora = calendario['hora_inicio']
        fin_hora = calendario['hora_fin']
        intervalo = timedelta(minutes = calendario['espacio_citas'])
    
        
        horarios = []
        hora_actual = inicio_hora
    
        while hora_actual <= fin_hora:
            horarios.append(hora_actual)
            hora_actual += intervalo
        
        
        
        # citas = obtener_citas(id_calendario)
        # horario = horario_tabla()
        semanas = generar_semanas(
            calendario['fecha_inicio'], 
            calendario['fecha_fin']
        )
        
        return render_template("calendario2.html", 
                            calendario=calendario, 
                            horarios = horarios,
                            citas=citas,
                            semanas=semanas,
                            procedimientos = obtener_procedimientos(),
                            meses=['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                                  'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                            dias_semana=['Lun', 'Mar', 'Mié', 'Jue', 'Vir', 'Sáb', 'Dom'])
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        flash("Error al cargar el calendario", "error")
        return redirect(url_for("index"))


# Generar PDF
# @tabla_trabajadores.route("/obtener_citas_pdf/<int:id_calendario>")
# @login_required  # Requiere que el usuario esté autenticado
# @role_required(1)  # Requiere que el usuario tenga rol de administrador (rol 1)
# def obtener_empleado(id_calendario):
#     """
#     Ruta que obtiene la información detallada de un empleado específico.
#     Si el empleado tiene acceso al sistema, también incluye sus datos de usuario.
    
#     Args:
#         id_empleado (int): ID del empleado a consultar
        
#     Returns:
#         Response: Datos del empleado en formato JSON
#     """
#     try:
#         # Iniciar conexión a la base de datos
#         cur = mysql.connection.cursor()

#         # 1. Obtener datos básicos del empleado
#         cur.execute(
#             """
#             SELECT cal.nombre_calendario,
#                 c.fecha,
#                 c.hora,
#                 pa.nombre AS nombre_paciente,
#                 p.nombre AS nombre_procedimiento,
#             FROM calendario cal 
#             LEFT JOIN municipios m ON cal.id_municipio = m.id_municipio
#             LEFT JOIN procedimientos p ON cal.id_procedimiento = p.id_procedimiento
#             LEFT JOIN citas c ON cal.id_calendario = c.id_calendario
#             LEFT JOIN pacientes pa ON c.id_paciente = pa.id_pacient
#             WHERE cal.id_calendario = %s
#             """,
#             (id_calendario,),
#         )

#         # Obtener el resultado
#         calendario = cur.fetchone()
#         print(calendario)
#         # # Verificar si se encontró el empleado
#         if not calendario:
#             return jsonify({"error": "Calendario no encontrado"}), 404

#         # # 2. Si tiene acceso al sistema, obtener datos del usuario asociado
#         # if empleado["accesoSistema"] == "1":
#         #     cur.execute(
#         #         """
#         #         SELECT u.*, r.idRol, r.nombreRol
#         #         FROM usuario u
#         #         LEFT JOIN rol r ON u.idRol = r.idRol
#         #         WHERE u.idEmpleado = %s
#         #         """,
#         #         (id_empleado,),
#         #     )
#         #     usuario = cur.fetchone()

#         #     # Si no se encuentra el usuario, crear un objeto vacío
#         #     if not usuario:
#         #         usuario = {"idRol": None, "nombreRol": None, "fechaCreacion": None}

#         #     # Convertir fechas a formato string para JSON
#         #     if "fechaCreacion" in usuario and usuario["fechaCreacion"]:
#         #         usuario["fechaCreacion"] = usuario["fechaCreacion"].strftime("%Y-%m-%d")

#         #     # Asegurarse de que el idRol sea un string para la comparación en JavaScript
#         #     if "idRol" in usuario and usuario["idRol"] is not None:
#         #         usuario["idRol"] = str(usuario["idRol"])

#         #     # Agregar datos de usuario al objeto empleado
#         #     empleado["usuario"] = usuario
#         # else:
#         #     # Si no tiene acceso al sistema, establecer usuario como None
#         #     empleado["usuario"] = None

#         # # 3. Convertir fechas a formato string para JSON
#         # if "fechaNacimiento" in empleado and empleado["fechaNacimiento"]:
#         #     empleado["fechaNacimiento"] = empleado["fechaNacimiento"].strftime(
#         #         "%Y-%m-%d"
#         #     )
#         # if "fechaContratacion" in empleado and empleado["fechaContratacion"]:
#         #     empleado["fechaContratacion"] = empleado["fechaContratacion"].strftime(
#         #         "%Y-%m-%d"
#         #     )

#         # # 4. Asegurarse de que accesoSistema sea un string para la comparación en JavaScript
#         # if "accesoSistema" in empleado:
#         #     empleado["accesoSistema"] = str(empleado["accesoSistema"])

#         # 5. Devolver los datos en formato JSON
#         return jsonify(empleado)

#     except Exception as e:
#         # Manejar errores en la consulta
#         print(f"Error al obtener empleado: {e}")
#         return jsonify({"error": str(e)}), 500

#     finally:
#         # Asegurar que el cursor se cierre incluso si hay errores
#         if "cur" in locals():
#             cur.close()



# pdf_calendario = Blueprint('pdf_calendario', __name__)

# @pdf_calendario.route("/generar_informe_pdf/<int:id_calendario>")
# @login_required  # Requiere que el usuario esté autenticado
# @role_required(1)  # Requiere que el usuario tenga rol de administrador (rol 1)
# def generar_informe_calendario_pdf(id_calendario):
#     """
#     Ruta que genera un informe PDF con la lista de trabajadores.
    
#     Returns:
#         Response: Archivo PDF para descargar o mensaje de error
#     """
#     try:
#         # 1. Obtener datos de trabajadores
#         cur = mysql.connection.cursor()

#         # 1. Obtener datos básicos del empleado
#         cur.execute(
#             """
#             SELECT cal.nombre_calendario,
#                 m.nombre AS nombre_municipio,
#                 c.fecha,
#                 c.hora,
#                 pa.nombre AS nombre_paciente,
#                 p.nombre AS nombre_procedimiento
#             FROM calendarios cal 
#             LEFT JOIN municipios m ON cal.id_municipio = m.id_municipio
#             LEFT JOIN procedimientos p ON cal.id_procedimiento = p.id_procedimiento
#             LEFT JOIN citas c ON cal.id_calendario = c.id_calendario
#             LEFT JOIN pacientes pa ON c.id_paciente = pa.id
#             WHERE cal.id_calendario = %s
#             """,
#             (id_calendario,),
#         )

#         # Obtener el resultado
#         calendario = cur.fetchone()
#         print(calendario)
#         cur.close()

#         # 2. Crear un buffer en memoria para el PDF
#         buffer = BytesIO()

#         # 3. Configurar el documento PDF
#         doc = SimpleDocTemplate(
#             buffer,
#             pagesize=landscape(A3),  # Orientación horizontal con tamaño A3 (más grande que A4)
#             rightMargin=20,
#             leftMargin=20,
#             topMargin=60,  # Aumentado para dejar espacio para el logo
#             bottomMargin=60,  # Aumentado para dejar espacio para el pie de página
#         )

#         # 4. Configurar estilos para el documento
#         styles = getSampleStyleSheet()
#         title_style = styles["Heading1"]
#         normal_style = styles["Normal"]

#         # 5. Crear estilo para el pie de página
#         footer_style = ParagraphStyle(
#             "Footer",
#             parent=styles["Normal"],
#             fontSize=8,
#             alignment=TA_CENTER,
#         )

#         # 6. Inicializar lista de elementos del PDF
#         elements = []

#         # 7. Definir la ruta del logo
#         logo_path = os.path.join(
#             os.path.dirname(os.path.abspath(__file__)),
#             "..",
#             "..",
#             "static",
#             "img",
#             "logoSinFondo.png",
#         )

#         # 8. Agregar título centrado
#         title_style.alignment = TA_CENTER
#         elements.append(Paragraph("Informe de Calendario", title_style))
#         elements.append(Spacer(1, 10))

#         # 9. Agregar fecha de generación
#         fecha_generacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         elements.append(
#             Paragraph(f"Fecha de generación: {fecha_generacion}", normal_style)
#         )
#         elements.append(Spacer(1, 20))

#         # 10. Definir encabezados de la tabla
#         headers = [
#             "Calendario",
#             "Municipio",
#             "Fecha",
#             "Hora",
#             "Paciente",
#             "Procedimiento",
#         ]

#         # 11. Inicializar datos para la tabla con los encabezados
#         data = [headers]

#         # 12. Agregar fila de datos del calendario
#         if calendario:
#             fecha_formateada = (
#                 calendario["fecha"].strftime("%Y-%m-%d")
#                 if calendario["fecha"]
#                 else ""
#             )

#             # Crear fila con datos del calendario
#             row = [
#                 calendario["nombre_calendario"],
#                 calendario["nombre_municipio"],
#                 fecha_formateada,
#                 calendario["hora"],
#                 calendario["nombre_paciente"],
#                 calendario["nombre_procedimiento"],
#             ]
#             data.append(row)

#         # 13. Crear la tabla con ancho específico para cada columna
#         col_widths = [
#             120,  # Nombre calendario
#             80,   # Nombre municipio
#             90,   # Fecha 
#             60,   # Hora
#             120,  # Nombre paciente
#             80,   # Nombre procedimiento
#         ]
#         table = Table(data, repeatRows=1, colWidths=col_widths)

#         # 14. Definir estilo de la tabla
#         table_style = TableStyle(
#             [
#                 # Estilo para la fila de encabezados
#                 ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
#                 ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
#                 ("ALIGN", (0, 0), (-1, 0), "CENTER"),
#                 ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
#                 ("FONTSIZE", (0, 0), (-1, 0), 10),
#                 ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                
#                 # Estilo para las filas de datos
#                 ("BACKGROUND", (0, 1), (-1, -1), colors.white),
#                 ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
#                 ("ALIGN", (0, 1), (-1, -1), "LEFT"),
#                 ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
#                 ("FONTSIZE", (0, 1), (-1, -1), 9),
                
#                 # Estilo general de la tabla
#                 ("GRID", (0, 0), (-1, -1), 1, colors.black),
#                 ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
#                 ("WORDWRAP", (0, 0), (-1, -1), True),  # Permitir que el texto se ajuste
                
#                 # Padding para mejorar legibilidad
#                 ("LEFTPADDING", (0, 0), (-1, -1), 6),
#                 ("RIGHTPADDING", (0, 0), (-1, -1), 6),
#                 ("TOPPADDING", (0, 0), (-1, -1), 4),
#                 ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
#             ]
#         )

#         # 15. Aplicar estilo alternado de filas (filas pares con fondo gris claro)
#         for i in range(1, len(data)):
#             if i % 2 == 0:
#                 table_style.add("BACKGROUND", (0, i), (-1, i), colors.lightgrey)

#         # 16. Aplicar estilo a la tabla y agregarla a los elementos
#         table.setStyle(table_style)
#         elements.append(table)

#         # 17. Agregar espacio antes del pie de página
#         elements.append(Spacer(1, 30))

#         # 18. Definir función para agregar encabezado y pie de página en cada página
#         def add_page_elements(canvas, doc):
#             """
#             Función que agrega elementos comunes a todas las páginas:
#             logo en la esquina superior derecha y pie de página.
            
#             Args:
#                 canvas: Lienzo del PDF
#                 doc: Documento PDF
#             """
#             # Guardar estado del lienzo
#             canvas.saveState()

#             # Agregar logo en la esquina superior derecha
#             if os.path.exists(logo_path):
#                 canvas.drawImage(
#                     logo_path,
#                     doc.width + doc.leftMargin - 150,  # Posición X en la esquina derecha
#                     doc.height + doc.bottomMargin - 50,  # Posición Y
#                     width=150,
#                     height=50,
#                     preserveAspectRatio=True,
#                     mask="auto",
#                 )

#             # Agregar línea horizontal encima del pie de página
#             canvas.setStrokeColor(colors.black)
#             canvas.line(doc.leftMargin, 50, doc.width + doc.leftMargin, 50)

#             # Agregar texto del pie de página debajo de la línea
#             canvas.setFont("Helvetica", 8)
            
#             # Primera línea del pie de página
#             # footer_text = "Trabajamos con la mejor calidad en la manufactura del hierro"
#             # canvas.drawCentredString(doc.width / 2 + doc.leftMargin, 35, footer_text)
            
#             # Segunda línea del pie de página
#             # footer_text2 = "Carrera 24 N°17.19 La Ceja Antioquia Celular: 3113148914"
#             # canvas.drawCentredString(doc.width / 2 + doc.leftMargin, 25, footer_text2)
            
#             # # Tercera línea del pie de página
#             # footer_text3 = "metalicas.fino@hotmail.com"
#             # canvas.drawCentredString(doc.width / 2 + doc.leftMargin, 15, footer_text3)

#             # Restaurar estado del lienzo
#             canvas.restoreState()

#         # 19. Construir el PDF con la función de encabezado y pie de página
#         doc.build(
#             elements, onFirstPage=add_page_elements, onLaterPages=add_page_elements
#         )

#         # 20. Obtener el contenido del buffer y cerrarlo
#         pdf_value = buffer.getvalue()
#         buffer.close()

#         # 21. Crear respuesta HTTP con el PDF
#         response = make_response(pdf_value)
#         response.headers["Content-Type"] = "application/pdf"
#         response.headers["Content-Disposition"] = (
#             "attachment; filename=informe_trabajadores.pdf"
#         )

#         return response

#     except Exception as e:
#         # Manejar errores en la generación del PDF
#         print(f"Error al generar PDF: {e}")
#         return jsonify({"error": str(e)}), 500


#Descarga en CSV
from flask import make_response, jsonify
import csv
from io import StringIO

csv_calendario = Blueprint("csv_calendario", __name__)

@csv_calendario.route("/generar_informe_csv/<int:id_calendario>")
@login_required
@role_required(1)
def generar_informe_calendario_csv(id_calendario):
    """
    Ruta que genera un informe CSV con la lista de trabajadores del calendario.
    
    Returns:
        Response: Archivo CSV para descargar o mensaje de error
    """
    try:
        # Conexión a la base de datos
        cur = mysql.connection.cursor()

        # Consulta de datos
        cur.execute(
            """
            SELECT cal.nombre_calendario,
                   m.nombre AS nombre_municipio,
                   c.fecha,
                   c.hora,
                   pa.nombre AS nombre_paciente,
                   p.nombre AS nombre_procedimiento
            FROM calendarios cal 
            LEFT JOIN municipios m ON cal.id_municipio = m.id_municipio
            LEFT JOIN procedimientos p ON cal.id_procedimiento = p.id_procedimiento
            LEFT JOIN citas c ON cal.id_calendario = c.id_calendario
            LEFT JOIN pacientes pa ON c.id_paciente = pa.id
            WHERE cal.id_calendario = %s
            """,
            (id_calendario,),
        )

        # Obtener todos los resultados
        filas = cur.fetchall()
        cur.close()

        if not filas:
            return jsonify({"error": "No se encontraron datos para el calendario"}), 404

        # Crear archivo CSV en memoria
        buffer = StringIO()
        writer = csv.writer(buffer)

        # Escribir encabezados
        headers = [
            "Calendario",
            "Municipio",
            "Fecha",
            "Hora",
            "Paciente",
            "Procedimiento"
        ]
        writer.writerow(headers)

        # Escribir filas
        for fila in filas:
            writer.writerow([
                fila["nombre_calendario"],
                fila["nombre_municipio"],
                fila["fecha"].strftime("%Y-%m-%d") if fila["fecha"] else "",
                fila["hora"],
                fila["nombre_paciente"],
                fila["nombre_procedimiento"]
            ])

        # Crear respuesta con el contenido del CSV
        response = make_response(buffer.getvalue())
        buffer.close()
        response.headers["Content-Disposition"] = "attachment; filename=informe_calendario.csv"
        response.headers["Content-Type"] = "text/csv"

        return response

    except Exception as e:
        print(f"Error al generar CSV: {e}")
        return jsonify({"error": str(e)}), 500
