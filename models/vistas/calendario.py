from flask import Flask, render_template, Blueprint, flash, redirect, url_for, request, session
from database.config import mysql
import traceback
from datetime import datetime, timedelta
from calendar import monthrange
from flask import Flask, Blueprint, render_template, jsonify
from auth.decorators import *
from flask_mysqldb import MySQLdb, cursors


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
        
        return render_template("calendario.html", 
                            calendario=calendario, 
                            horarios = horarios,
                            citas=citas,
                            semanas=semanas,
                            meses=['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                                  'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                            dias_semana=['Lun', 'Mar', 'Mié', 'Jue', 'Vir', 'Sáb', 'Dom'])
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        flash("Error al cargar el calendario", "error")
        return redirect(url_for("index"))
