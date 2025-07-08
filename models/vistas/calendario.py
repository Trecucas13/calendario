from flask import Flask, render_template, Blueprint, flash, redirect, url_for, request, session, make_response
from database.config import db
from datetime import datetime, timedelta
from calendar import monthrange
from flask import Flask, Blueprint, render_template, jsonify
from auth.decorators import *
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # Estilos para el PDF
from reportlab.lib.enums import TA_CENTER, TA_LEFT  # Alineación de texto
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer  # Componentes para el PDF
from reportlab.lib.pagesizes import A3, landscape  # Tamaños de página
from reportlab.lib import colors  # Colores para el PDF
from io import BytesIO  # Para manejar el PDF en memoria
from datetime import datetime  # Para fechas y horas
from sqlalchemy import text  # Para consultas SQL
import os  # Para manejo de rutas de archivos
import traceback


app = Flask(__name__)

tabla_calendarios = Blueprint('tabla_calendarios', __name__)
calendarios_creados = Blueprint('calendarios_creados', __name__)

def datos_calendario():
    try:
        datos = db.session.execute(
            text("""SELECT c.*, p.nombre AS nombreProcedimiento, m.nombre AS nombreMunicipio FROM calendarios c
            JOIN procedimientos p ON c.id_procedimiento = p.id_procedimiento
            JOIN municipios m ON c.id_municipio = m.id_municipio
            """)
        ).mappings().fetchall()
        # print(datos)
        # Convertir RowMapping a dict y formatear fechas
        calendarios = []
        for calendario in datos:
            calendario_dict = dict(calendario)
            if 'fecha_inicio' in calendario_dict and calendario_dict['fecha_inicio']:
                calendario_dict['fecha_inicio'] = calendario_dict['fecha_inicio'].strftime('%Y-%m-%d')
            if 'fecha_fin' in calendario_dict and calendario_dict['fecha_fin']:
                calendario_dict['fecha_fin'] = calendario_dict['fecha_fin'].strftime('%Y-%m-%d')
            calendarios.append(calendario_dict)
        return calendarios
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        return []


def obtener_procedimientos():
    try:
        procedimientos = db.session.execute(text("SELECT * FROM procedimientos")).fetchall()
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
        es_domingo = fecha.weekday() == 6
        semana_actual.append({
            "dia": fecha.day,
            "mes": fecha.month,
            "año": fecha.year,
            "fecha_completa": fecha.strftime('%Y-%m-%d'),
            "hoy": fecha == datetime.now().date(),
            "dentro_rango": dentro_rango,
            "es_domingo": es_domingo
        })
        # print(semana_actual)
        
        if es_domingo:  # Domingo
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
        # Migración a SQLAlchemy
        calendario_result = db.session.execute(
            text("SELECT * FROM calendarios WHERE id_calendario = :id_calendario"),
            {"id_calendario": id_calendario}
        ).mappings().fetchone()

        citas = db.session.execute(
            text("SELECT * FROM citas WHERE id_calendario = :id_calendario"),
            {"id_calendario": id_calendario}
        ).mappings().fetchall()

        if not calendario_result:
            flash("Calendario no encontrado", "error")
            return redirect(url_for("index"))

        inicio_hora = calendario_result['hora_inicio']
        fin_hora = calendario_result['hora_fin']
        intervalo = timedelta(minutes=calendario_result['espacio_citas'])

        horarios = []
        hora_actual = inicio_hora
        while hora_actual <= fin_hora:
            horarios.append(hora_actual)
            hora_actual = (datetime.combine(datetime.today(), hora_actual) + intervalo).time()

        semanas = generar_semanas(
            calendario_result['fecha_inicio'],
            calendario_result['fecha_fin']
        )

        return render_template("calendario2.html",
                              calendario=calendario_result,
                              horarios=horarios,
                              citas=citas,
                              semanas=semanas,
                              procedimientos=obtener_procedimientos(),
                              meses=['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                                    'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                              dias_semana=['Lun', 'Mar', 'Mié', 'Jue', 'Vir', 'Sáb', 'Dom'])
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        flash("Error al cargar el calendario", "error")
        return redirect(url_for("index"))



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
        # Migración a SQLAlchemy
        filas = db.session.execute(
            text("""
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
                WHERE cal.id_calendario = :id_calendario
            """),
            {"id_calendario": id_calendario}
        ).mappings().fetchall()

        if not filas:
            return jsonify({"error": "No se encontraron datos para el calendario"}), 404

        buffer = StringIO()
        writer = csv.writer(buffer)
        headers = [
            "Calendario",
            "Municipio",
            "Fecha",
            "Hora",
            "Paciente",
            "Procedimiento"
        ]
        writer.writerow(headers)
        for fila in filas:
            writer.writerow([
                fila["nombre_calendario"],
                fila["nombre_municipio"],
                fila["fecha"].strftime("%Y-%m-%d") if fila["fecha"] else "",
                fila["hora"],
                fila["nombre_paciente"],
                fila["nombre_procedimiento"]
            ])
        response = make_response(buffer.getvalue())
        buffer.close()
        response.headers["Content-Disposition"] = "attachment; filename=informe_calendario.csv"
        response.headers["Content-Type"] = "text/csv"
        return response
    except Exception as e:
        print(f"Error al generar CSV: {e}")
        return jsonify({"error": str(e)}), 500
