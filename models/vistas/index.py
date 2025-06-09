# Lógica para la vista principal o dashboard de la aplicación.
# NOTA: Todo el código funcional en este archivo se encuentra actualmente comentado.
# El código comentado sugiere funcionalidades para generar un informe PDF de citas,
# incluyendo datos de pacientes y procedimientos.

# # Importaciones necesarias
# from flask import (
#     Flask,
#     Blueprint,
#     render_template,
#     redirect,
#     url_for,
#     jsonify,
#     make_response,
# )
# from database.config import mysql  # Conexión a la base de datos
# from decorators.decorators import *  # Decoradores para control de acceso
# # Importaciones para generación de PDF
# from reportlab.lib import colors  # Colores para el PDF
# from reportlab.lib.pagesizes import letter, landscape, A3  # Tamaños de página
# from reportlab.platypus import (  # Componentes para construir el PDF
#     SimpleDocTemplate,
#     Table,
#     TableStyle,
#     Paragraph,
#     Spacer,
#     Image,
# )
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # Estilos para el PDF
# from reportlab.lib.enums import TA_CENTER, TA_LEFT  # Alineación de texto
# from io import BytesIO  # Para manejar el PDF en memoria
# from datetime import datetime  # Para fechas y horas
# import os  # Para manejo de rutas de archivos

# @datos_citas.route("/generar_informe_calendario_pdf")
# @login_required  # Requiere que el usuario esté autenticado
# @role_required(1)  # Requiere que el usuario tenga rol de administrador (rol 1)
# def generar_informe_calendario_pdf():
#     """
#     Ruta que genera un informe PDF con la lista de trabajadores.
    
#     Returns:
#         Response: Archivo PDF para descargar o mensaje de error
#     """
#     try:
#         # 1. Obtener datos de trabajadores
#         cur = mysql.connection.cursor()
#         cur.execute(
#             """
#             SELECT p.*, c.fecha, 
#                     c.hora, 
#                     c.id, 
#                     c.id_calendario, 
#                     c.id_procedimiento, 
#                     pr.nombre AS nombre_procedimiento
#             FROM pacientes p 
#             LEFT JOIN citas c ON p.id = c.id_paciente
#             LEFT JOIN procedimientos pr ON c.id_procedimiento = pr.id_procedimiento
#             """
#         )
#         citas = cur.fetchall()
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

#         # # 7. Definir la ruta del logo
#         # logo_path = os.path.join(
#         #     os.path.dirname(os.path.abspath(__file__)),
#         #     "..",
#         #     "..",
#         #     "static",
#         #     "img",
#         #     "logoSinFondo.png",
#         # )

#         # 8. Agregar título centrado
#         title_style.alignment = TA_CENTER
#         elements.append(Paragraph("CITAS", title_style))
#         elements.append(Spacer(1, 10))

#         # 9. Agregar fecha de generación
#         fecha_generacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         elements.append(
#             Paragraph(f"Fecha de generación: {fecha_generacion}", normal_style)
#         )
#         elements.append(Spacer(1, 20))

#         # 10. Definir encabezados de la tabla
#         headers = [
#             "Nombre",
#             "Apellido",
#             "Tipo documento",
#             "Documento"
#             "Celular",
#             "Fecha cita",
#             "Hora cita",
#             "Procedimiento",
#         ]

#         # 11. Inicializar datos para la tabla con los encabezados
#         data = [headers]

#         # 12. Agregar filas de datos de cada empleado
#         for citas in citas:
#             # Formatear fechas
#             fecha_nacimiento = (
#                 citas["fecha"].strftime("%Y-%m-%d")
#                 if citas["fecha"]
#                 else ""
#             )


#             # Crear fila con datos del empleado
#             row = [
#                 citas["nombre"],
#                 citas["apellido"],
#                 citas["tipo_documento"],
#                 citas["documento"],
#                 citas["telefono"],
#                 citas["fecha"],
#                 citas["hora"],
#                 citas["nombre_procedimiento"],
               
#             ]
#             data.append(row)

#         # 13. Crear la tabla con ancho específico para cada columna
#         col_widths = [
#             120,  # Nombre
#             80,   # apellido
#             100,  # Tipo de documento
#             100,  # Documento
#             100,  # Celular
#             100,  # Fecha 
#             100,  # Hora  
#             100,  # Procedimiento
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
#             footer_text = "Andes BPO S.A.S"
#             canvas.drawCentredString(doc.width / 2 + doc.leftMargin, 35, footer_text)
            
#             # Segunda línea del pie de página
#             footer_text2 = "La Ceja-Antioquia, 604 553 7866"
#             canvas.drawCentredString(doc.width / 2 + doc.leftMargin, 25, footer_text2)
            
#             # Tercera línea del pie de página
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
