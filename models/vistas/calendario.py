from flask import Flask, render_template, Blueprint, flash, redirect, url_for, request, session
from database.config import mysql
import traceback
from datetime import datetime, timedelta
from flask import Flask, Blueprint, render_template, jsonify
from auth.decorators import *
from flask_mysqldb import MySQLdb, cursors

app = Flask(__name__)

tabla_calendarios = Blueprint('tabla_calendarios', __name__)

def datos_id_calendario():
    try:
        conn = mysql.connection.cursor()
        conn.execute("SELECT * FROM calendarios")
        datos = conn.fetchall()
        
        id_calendario = conn.lastrowid
        conn.close()

        # Formatear las fechas antes de devolver los datos
        for calendario in datos:
            if 'fecha_inicio' in calendario and calendario['fecha_inicio']:
                calendario['fecha_inicio'] = calendario['fecha_inicio'].strftime('%Y-%m-%d')
            if 'fecha_fin' in calendario and calendario['fecha_fin']:
                calendario['fecha_fin'] = calendario['fecha_fin'].strftime('%Y-%m-%d')

        return datos
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        return []





def datos_calendario():
    try:
        # Use DictCursor instead of dictionary=True
        id_usuario = session.get('id')
        conn = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        conn.execute("SELECT * FROM calendarios WHERE id_usuario = %s", (id_usuario,))
        datos = conn.fetchall()
        conn.close()

        # Formatear las fechas antes de devolver los datos
        for calendario in datos:
            if 'fecha_inicio' in calendario and calendario['fecha_inicio']:
                calendario['fecha_inicio'] = calendario['fecha_inicio'].strftime('%Y-%m-%d')
            if 'fecha_fin' in calendario and calendario['fecha_fin']:
                calendario['fecha_fin'] = calendario['fecha_fin'].strftime('%Y-%m-%d')

        return datos
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        return []


def obtener_citas(id_calendario):
    try:
        conn = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Si se proporciona un ID de calendario, filtrar por ese calendario
        if id_calendario:
            conn.execute("""
                SELECT c.fecha, c.hora, p.tipo_documento, p.numero_documento, 
                       p.telefono, p.direccion, p.fecha_nacimiento, p.examen_realizar
                FROM citas c
                JOIN pacientes p ON c.id_paciente = p.id
                WHERE c.id_calendario = %s
                ORDER BY c.fecha, c.hora""", 
                (id_calendario,))
        else:
            # Si no se proporciona ID, obtener todas las citas
            conn.execute("""
                SELECT c.fecha, c.hora, c.id_calendario, p.tipo_documento, p.numero_documento, 
                       p.telefono, p.direccion, p.fecha_nacimiento, p.examen_realizar
                FROM citas c
                JOIN pacientes p ON c.id_paciente = p.id
                ORDER BY c.fecha, c.hora""")
                
        citas = conn.fetchall()
        
        # Formatear las fechas para que sean compatibles con JavaScript
        for cita in citas:
            if 'fecha' in cita and cita['fecha']:
                cita['fecha'] = cita['fecha'].strftime('%Y-%m-%d')
                
        conn.close()
        return citas
    except Exception as e:
        print(f"Error al obtener citas: {str(e)}")
        return []



@tabla_calendarios.route("/calendario")
@login_required
@role_required([1, 2])
def calendario():
    # Obtener los datos del calendario (sin desempaquetar)
    calendarios = datos_calendario()
    print(calendarios)
    # Inicializar citas como una lista vacía
    citas = []
    
    # Verificar si hay datos de calendario
    if calendarios and len(calendarios) > 0:
        # Obtener citas del primer calendario
        citas = obtener_citas(calendarios[0]['id_calendario'])
        print(citas)
    else:
        # Si no hay calendarios, obtener todas las citas
        citas = obtener_citas(None)
        
    return render_template("calendarioo.html", 
                          calendarios=calendarios, 
                          citas=citas,
                          obtener_fecha_para_dia=obtener_fecha_para_dia)

# @tabla_calendarios.route("/api/citas/<int:calendario_id>")
# def api_citas(calendario_id):
#     citas = obtener_citas(calendario_id)
#     return jsonify(citas)

# @tabla_calendarios.route("/api/citas/crear", methods=['POST'])
# def crear_cita():
#     try:
#         # Obtener datos del JSON enviado
#         data = request.get_json()
        
#         # Validar datos requeridos
#         if not all(key in data for key in ['id_calendario', 'fecha', 'hora']):
#             return jsonify({'error': 'Faltan datos requeridos'}), 400
            
#         # Preparar datos para inserción
#         id_calendario = data['id_calendario']
#         fecha = data['fecha']
#         hora = data['hora']
#         estado = data.get('estado', 'confirmada')
        
#         # Datos adicionales del paciente si están disponibles
#         paciente = data.get('paciente', '')
#         documento = data.get('documento', '')
#         telefono = data.get('telefono', '')
#         examen = data.get('examen', '')
        
#         # Insertar en la base de datos
#         conn = mysql.connection.cursor()
#         query = "INSERT INTO citas (id_calendario, fecha, hora, estado, paciente, documento, telefono, examen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
#         conn.execute(query, (id_calendario, fecha, hora, estado, paciente, documento, telefono, examen))
#         mysql.connection.commit()
        
#         # Obtener el ID de la cita insertada
#         cita_id = conn.lastrowid
#         conn.close()
        
#         return jsonify({
#             'id': cita_id,
#             'mensaje': 'Cita creada exitosamente',
#             'calendario_id': id_calendario,
#             'fecha': fecha,
#             'hora': hora
#         })
#     except Exception as e:
#         error = traceback.format_exc()
#         print(error)
#         return jsonify({'error': str(e)}), 500

# Asegúrate de registrar el blueprint
app.register_blueprint(tabla_calendarios)

if __name__ == "__main__":
    app.run(debug=True)


def obtener_fecha_para_dia(dia_semana):
    hoy = datetime.now()
    dias = {
        'lunes': 0, 'martes': 1, 'miercoles': 2,
        'jueves': 3, 'viernes': 4, 'sabado': 5
    }
    diferencia = dias[dia_semana] - hoy.weekday()
    if diferencia < 0:
        diferencia += 7
    return (hoy + timedelta(days=diferencia)).strftime('%Y-%m-%d')
