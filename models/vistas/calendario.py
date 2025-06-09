# Lógica para generar vistas relacionadas con el calendario y citas.

from flask import (Flask, render_template, Blueprint, flash, redirect, url_for,
                   request, session, make_response, jsonify) # session y request no se usan en todas las funciones.
from database.config import mysql # Conexión a la base de datos.
from datetime import datetime, timedelta # Para manipulación de fechas y horas.
# from calendar import monthrange # monthrange no se usa.
from auth.decorators import login_required, role_required # Decoradores para control de acceso.
from flask_mysqldb import MySQLdb # Para tipos de cursor como DictCursor.

# Importaciones para generación de PDF con ReportLab (actualmente comentadas en el código original).
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER, TA_LEFT
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# from reportlab.lib.pagesizes import A3, landscape
# from reportlab.lib import colors
# from io import BytesIO # Para manejar el PDF en memoria
# import os # Para manejo de rutas de archivos

import traceback # Para logging de errores.
import csv # Para la generación de CSV.
from io import StringIO # Para manejar el CSV en memoria.

# La instancia de Flask app = Flask(__name__) es inusual aquí si esto es un módulo de Blueprint.
# Normalmente, la app se crea en el archivo principal de la aplicación.
# Se comentará para evitar problemas si este archivo es solo para Blueprints.
# app = Flask(__name__)

# --- Blueprints ---
# Blueprint para la tabla principal de calendarios y la vista detallada de un calendario.
vista_calendario_bp = Blueprint('tabla_calendarios', __name__, template_folder='templates')
# Blueprint para calendarios creados (no se usa en el código proporcionado, podría ser para otra funcionalidad).
calendarios_creados_bp = Blueprint('calendarios_creados', __name__, template_folder='templates')
# Blueprint para la generación de informes CSV de calendarios.
csv_calendario_bp = Blueprint("csv_calendario", __name__, template_folder='templates')
# Blueprint para PDF (comentado en el original)
# pdf_calendario_bp = Blueprint('pdf_calendario', __name__, template_folder='templates')


# --- Funciones Auxiliares ---

def datos_calendario():
    """
    Obtiene todos los datos de los calendarios de la base de datos.

    Realiza un JOIN con las tablas `procedimientos` y `municipios` para obtener
    los nombres en lugar de solo los IDs. Formatea las fechas de inicio y fin
    de los calendarios a 'YYYY-MM-DD'.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa un calendario
              con sus datos y los nombres del procedimiento y municipio.
              Retorna una lista vacía en caso de error.
    """
    conn = None
    try:
        # Usar DictCursor para obtener resultados como diccionarios.
        conn = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Consulta para obtener datos de calendarios con nombres de procedimiento y municipio.
        conn.execute("""SELECT c.*, p.nombre AS nombreProcedimiento, m.nombre AS nombreMunicipio
                        FROM calendarios c
                        JOIN procedimientos p ON c.id_procedimiento = p.id_procedimiento
                        JOIN municipios m ON c.id_municipio = m.id_municipio
                        """)
        datos = conn.fetchall() # Recupera todas las filas.

        # Formatea las fechas antes de devolver los datos.
        for calendario_item in datos: # Renombrado 'calendario' a 'calendario_item' para evitar conflicto con la ruta.
            if 'fecha_inicio' in calendario_item and calendario_item['fecha_inicio']:
                calendario_item['fecha_inicio'] = calendario_item['fecha_inicio'].strftime('%Y-%m-%d')
            if 'fecha_fin' in calendario_item and calendario_item['fecha_fin']:
                calendario_item['fecha_fin'] = calendario_item['fecha_fin'].strftime('%Y-%m-%d')

        return datos
    except Exception as e:
        # Manejo de errores: imprime el error y el traceback, y devuelve una lista vacía.
        print(f"Error en datos_calendario: {e}")
        traceback.print_exc()
        return []
    finally:
        if conn:
            conn.close() # Asegura que la conexión se cierre.


def obtener_procedimientos():
    """
    Obtiene todos los procedimientos de la tabla `procedimientos`.

    Returns:
        list: Una lista de tuplas (o diccionarios si se usa DictCursor) con los datos
              de los procedimientos. Retorna una lista vacía en caso de error.
    """
    conn = None
    try:
        conn = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # Usar DictCursor para consistencia.
        conn.execute("SELECT * FROM procedimientos")
        procedimientos = conn.fetchall()
        return procedimientos
    except Exception as e:
        print(f"Error en obtener_procedimientos: {e}")
        traceback.print_exc()
        return []
    finally:
        if conn:
            conn.close()


def generar_semanas(fecha_inicio, fecha_fin):
    """
    Genera una estructura de datos representando las semanas entre una fecha de inicio y fin.

    Ajusta el rango para empezar en el lunes de la semana de `fecha_inicio` y terminar
    en el domingo de la semana de `fecha_fin`. Cada día en la estructura contiene
    información sobre el día, mes, año, fecha completa, si es el día actual ('hoy'),
    y si está dentro del rango original de `fecha_inicio` a `fecha_fin`.

    Args:
        fecha_inicio (date): La fecha de inicio del rango original.
        fecha_fin (date): La fecha de fin del rango original.

    Returns:
        list: Una lista de semanas. Cada semana es una lista de diccionarios,
              donde cada diccionario representa un día.

    Raises:
        ValueError: Si `fecha_inicio` es posterior a `fecha_fin`.
    """
    # Se asume que fecha_inicio y fecha_fin ya son objetos date.
    # Si fueran strings, necesitarían conversión: datetime.strptime(fecha_str, '%Y-%m-%d').date()
    
    if not isinstance(fecha_inicio, datetime.date) or not isinstance(fecha_fin, datetime.date):
        raise TypeError("Las fechas de inicio y fin deben ser objetos date.")

    if fecha_inicio > fecha_fin:
        raise ValueError("La fecha de inicio no puede ser mayor que la fecha final.")

    # Encuentra el lunes anterior o igual a la fecha de inicio.
    dias_hasta_lunes = fecha_inicio.weekday()  # weekday(): Lunes es 0 y Domingo es 6.
    lunes_inicio_semana = fecha_inicio - timedelta(days=dias_hasta_lunes)
    
    # Encuentra el domingo posterior o igual a la fecha de fin.
    dias_hasta_domingo = 6 - fecha_fin.weekday()
    domingo_fin_semana = fecha_fin + timedelta(days=dias_hasta_domingo)
    
    # Genera todas las fechas en el rango ampliado (de lunes a domingo).
    delta_total_dias = (domingo_fin_semana - lunes_inicio_semana).days
    todas_las_fechas_del_rango_ampliado = [lunes_inicio_semana + timedelta(days=i) for i in range(delta_total_dias + 1)]
    
    semanas_generadas = []
    semana_actual_lista = []
    
    for fecha_iter in todas_las_fechas_del_rango_ampliado:
        # Determina si la fecha está dentro del rango original (fecha_inicio a fecha_fin).
        esta_dentro_rango_original = (fecha_inicio <= fecha_iter <= fecha_fin)
        
        semana_actual_lista.append({
            "dia": fecha_iter.day,
            "mes": fecha_iter.month,
            "año": fecha_iter.year,
            "fecha_completa": fecha_iter.strftime('%Y-%m-%d'), # Formato estándar para fechas.
            "hoy": fecha_iter == datetime.now().date(), # Compara con la fecha actual.
            "dentro_rango": esta_dentro_rango_original # Indica si es parte del intervalo original.
        })
        
        if fecha_iter.weekday() == 6:  # Si es Domingo, se completa una semana.
            semanas_generadas.append(semana_actual_lista)
            semana_actual_lista = [] # Reinicia la lista para la siguiente semana.
    
    if semana_actual_lista:  # Añade la última semana si quedó incompleta (no terminó en domingo).
        semanas_generadas.append(semana_actual_lista)
    
    return semanas_generadas

# --- Rutas Principales del Calendario ---

@vista_calendario_bp.route("/calendario/<int:id_calendario>", methods=["GET"]) # Removido POST si no se maneja.
@login_required # Requiere inicio de sesión.
@role_required([1, 2]) # Permite acceso a roles 1 (Admin) y 2 (Usuario regular, por ejemplo).
def vista_detalle_calendario(id_calendario): # Nombre de función más descriptivo.
    """
    Muestra la vista detallada de un calendario específico, incluyendo sus citas y horarios.

    Obtiene los datos del calendario, las citas asociadas, genera los horarios disponibles
    basados en la configuración del calendario (hora de inicio, fin, intervalo de citas),
    y prepara la estructura de semanas para la visualización.
    Pasa todos estos datos a la plantilla 'calendario2.html'.

    Args:
        id_calendario (int): El ID del calendario a visualizar, obtenido de la URL.

    Returns:
        Response: Renderiza la plantilla 'calendario2.html' con los datos del calendario,
                  o redirige a la página de inicio con un mensaje de error si ocurre una excepción.
    """
    conn = None
    try:
        conn = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # Usar DictCursor.
        # Obtener datos del calendario específico.
        conn.execute("SELECT * FROM calendarios WHERE id_calendario = %s", (id_calendario,))
        calendario_db = conn.fetchone() # Datos del calendario.

        if not calendario_db:
            flash(f"Calendario con ID {id_calendario} no encontrado.", "warning")
            return redirect(url_for("index")) # O a una página de listado de calendarios.

        # Obtener citas para este calendario.
        conn.execute("SELECT * FROM citas WHERE id_calendario = %s", (id_calendario,))
        citas_db = conn.fetchall() # Lista de citas.
        
        # --- Generación de Horarios ---
        # Convertir strings de hora a objetos time o datetime si es necesario para la lógica.
        # Aquí se asume que son objetos time o que la comparación directa funciona.
        # Si son strings, podrían necesitar conversión: datetime.strptime(calendario_db['hora_inicio'], '%H:%M:%S').time()
        
        # Validar que las horas y el intervalo son válidos antes de proceder.
        if not all(k in calendario_db and calendario_db[k] is not None for k in ['hora_inicio', 'hora_fin', 'espacio_citas']):
            flash("Datos de configuración de horario incompletos o inválidos para el calendario.", "danger")
            return redirect(url_for("index")) # O a una página de error o listado.

        # Asegurar que las horas son objetos time para la comparación.
        # Si ya son time desde la BD (poco común para MySQL), esto no es necesario.
        # Si son strings, necesitan conversión. Si son timedelta (desde MySQL TIME type), necesitan manejo.
        # Por simplicidad, si son strings 'HH:MM:SS', se convierten a datetime con fecha dummy.
        try:
            hora_inicio_dt = datetime.strptime(str(calendario_db['hora_inicio']), '%H:%M:%S')
            hora_fin_dt = datetime.strptime(str(calendario_db['hora_fin']), '%H:%M:%S')
        except ValueError:
             # Si ya son timedelta (común con MySQL TIME y algunos conectores)
            if isinstance(calendario_db['hora_inicio'], timedelta) and isinstance(calendario_db['hora_fin'], timedelta):
                base_date = datetime.min.date() # Fecha base para convertir timedelta a datetime
                hora_inicio_dt = datetime.combine(base_date, (datetime.min + calendario_db['hora_inicio']).time())
                hora_fin_dt = datetime.combine(base_date, (datetime.min + calendario_db['hora_fin']).time())
            else:
                raise ValueError("Formato de hora de inicio/fin no reconocido.")

        intervalo_minutos = int(calendario_db['espacio_citas'])
        intervalo_td = timedelta(minutes=intervalo_minutos)

        horarios_disponibles = []
        hora_actual_dt = hora_inicio_dt
    
        while hora_actual_dt <= hora_fin_dt:
            horarios_disponibles.append(hora_actual_dt.time()) # Almacena solo la parte de la hora.
            hora_actual_dt += intervalo_td
        
        # --- Generación de Semanas ---
        # Asegurar que las fechas son objetos date.
        fecha_inicio_cal = calendario_db['fecha_inicio']
        fecha_fin_cal = calendario_db['fecha_fin']
        if isinstance(fecha_inicio_cal, str):
            fecha_inicio_cal = datetime.strptime(fecha_inicio_cal, '%Y-%m-%d').date()
        if isinstance(fecha_fin_cal, str):
            fecha_fin_cal = datetime.strptime(fecha_fin_cal, '%Y-%m-%d').date()

        semanas_vista = generar_semanas(fecha_inicio_cal, fecha_fin_cal)
        
        # Contexto para la plantilla.
        contexto_plantilla = {
            "calendario": calendario_db,
            "horarios": horarios_disponibles,
            "citas": citas_db,
            "semanas": semanas_vista,
            "procedimientos": obtener_procedimientos(), # Obtiene lista de procedimientos para formularios, etc.
            "meses": ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                      'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            "dias_semana": ['Lun', 'Mar', 'Mié', 'Jue', 'Vir', 'Sáb', 'Dom']
        }
        return render_template("calendario2.html", **contexto_plantilla)
    
    except Exception as e:
        # Manejo de errores generales al cargar el calendario.
        print(f"Error en vista_detalle_calendario (ID: {id_calendario}): {e}")
        traceback.print_exc()
        flash("Error al cargar el calendario. Por favor, intente más tarde.", "danger")
        return redirect(url_for("index")) # Redirige a la página principal o de error.
    finally:
        if conn:
            conn.close()


# --- Generación de Informes (PDF y CSV) ---
# La sección de PDF está mayormente comentada en el original. Se mantendrá así.
# El Blueprint original para PDF era 'tabla_trabajadores', lo cual es confuso.
# Se comentan las rutas de PDF por ahora, ya que el código está incompleto/comentado.

# @pdf_calendario_bp.route("/generar_informe_pdf/<int:id_calendario>")
# @login_required
# @role_required(1)
# def generar_informe_calendario_pdf(id_calendario):
#     """
#     (Comentado en el original) Genera un informe PDF para un calendario específico.
#     Contendría detalles del calendario, citas, pacientes y procedimientos.
#     """
#     # ... (Lógica de generación de PDF aquí) ...
#     pass


@csv_calendario_bp.route("/generar_informe_csv/<int:id_calendario>")
@login_required # Requiere inicio de sesión.
@role_required(1) # Solo rol 1 (Admin) puede generar informes.
def generar_informe_calendario_csv(id_calendario):
    """
    Genera un informe en formato CSV con los datos de las citas de un calendario específico.

    Consulta la base de datos para obtener el nombre del calendario, municipio,
    y detalles de cada cita (fecha, hora, paciente, procedimiento).
    Luego, construye un archivo CSV en memoria y lo devuelve como una descarga.

    Args:
        id_calendario (int): El ID del calendario para el cual generar el informe.

    Returns:
        Response: Un objeto `Response` de Flask con el archivo CSV para descargar,
                  o un JSON con un mensaje de error si no se encuentran datos o si ocurre una excepción.
    """
    conn = None
    try:
        conn = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # Usar DictCursor.

        # Consulta para obtener los datos necesarios para el informe CSV.
        conn.execute(
            """
            SELECT cal.nombre_calendario, m.nombre AS nombre_municipio,
                   c.fecha, c.hora,
                   pa.nombre AS nombre_paciente, pa.primer_apellido AS apellido_paciente,
                   p.nombre AS nombre_procedimiento
            FROM calendarios cal 
            LEFT JOIN municipios m ON cal.id_municipio = m.id_municipio
            LEFT JOIN procedimientos p ON cal.id_procedimiento = p.id_procedimiento
            LEFT JOIN citas c ON cal.id_calendario = c.id_calendario
            LEFT JOIN pacientes pa ON c.id_paciente = pa.id  -- Asumiendo que la FK en citas es id_paciente y PK en pacientes es id
            WHERE cal.id_calendario = %s
            ORDER BY c.fecha, c.hora -- Ordenar por fecha y hora de la cita
            """,
            (id_calendario,),
        )
        filas_datos = conn.fetchall() # Obtiene todas las filas.

        if not filas_datos: # Si no hay datos para el calendario.
            return jsonify({"error": "No se encontraron datos para el calendario especificado."}), 404

        # --- Creación del archivo CSV en memoria ---
        buffer_csv = StringIO() # Buffer para escribir el CSV.
        escritor_csv = csv.writer(buffer_csv)

        # Escribir los encabezados del CSV.
        encabezados = [
            "Nombre Calendario", "Municipio", "Fecha Cita", "Hora Cita",
            "Nombre Paciente", "Apellido Paciente", "Procedimiento"
        ]
        escritor_csv.writerow(encabezados)

        # Escribir las filas de datos en el CSV.
        for fila in filas_datos:
            # Formatear la fecha de la cita.
            fecha_cita_formateada = fila["fecha"].strftime("%Y-%m-%d") if fila["fecha"] else ""
            # Formatear la hora de la cita (si es timedelta, convertir a string HH:MM:SS).
            hora_cita_str = str(fila["hora"]) if fila["hora"] else ""
            if isinstance(fila["hora"], timedelta):
                 total_seconds = int(fila["hora"].total_seconds())
                 hours, remainder = divmod(total_seconds, 3600)
                 minutes, seconds = divmod(remainder, 60)
                 hora_cita_str = f"{hours:02}:{minutes:02}:{seconds:02}"


            escritor_csv.writerow([
                fila["nombre_calendario"],
                fila["nombre_municipio"],
                fecha_cita_formateada,
                hora_cita_str, # Usar la hora formateada.
                fila["nombre_paciente"],
                fila["apellido_paciente"], # Añadido apellido para más detalle.
                fila["nombre_procedimiento"]
            ])

        # --- Preparación de la respuesta HTTP ---
        contenido_csv = buffer_csv.getvalue()
        buffer_csv.close() # Cierra el buffer.

        respuesta = make_response(contenido_csv)
        # Define las cabeceras para la descarga del archivo.
        respuesta.headers["Content-Disposition"] = f"attachment; filename=informe_calendario_{id_calendario}.csv"
        respuesta.headers["Content-Type"] = "text/csv; charset=utf-8" # Especificar charset.

        return respuesta

    except Exception as e:
        # Manejo de errores en la generación del CSV.
        print(f"Error al generar informe CSV para calendario ID {id_calendario}: {e}")
        traceback.print_exc()
        return jsonify({"error": f"Error interno al generar el informe CSV: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()
