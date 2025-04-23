from flask import Flask, render_template, Blueprint, flash, redirect, url_for, request
from database.config import mysql
import traceback
from datetime import datetime
from flask import Flask, Blueprint, render_template, jsonify
from auth.decorators import *

app = Flask(__name__)

tabla_calendarios = Blueprint('tabla_calendarios', __name__)

def datos_calendario():
    try:
        conn = mysql.connection.cursor()
        conn.execute("SELECT * FROM calendarios")
        datos = conn.fetchall()
        conn.close()

        # Formatear las fechas antes de devolver los datos
        for calendario in datos:
            calendario['fecha_inicio'] = calendario['fecha_inicio'].strftime('%Y-%m-%d')
            calendario['fecha_fin'] = calendario['fecha_fin'].strftime('%Y-%m-%d')

        return datos
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        return []

def obtener_citas(calendario_id=None):
    try:
        conn = mysql.connection.cursor()
        if calendario_id:
            conn.execute("SELECT * FROM citas WHERE calendario_id = %s", (calendario_id,))
        else:
            conn.execute("SELECT * FROM citas")
        citas = conn.fetchall()
        conn.close()
        return citas
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        return []

@tabla_calendarios.route("/calendario")
@login_required
@role_required([1, 2])
def calendario():
    calendarios = datos_calendario()
    citas = []
    if calendarios and len(calendarios) > 0:
        citas = obtener_citas(calendarios[0]['id'])
    return render_template("calendario.html", calendarios=calendarios, citas=citas)

@tabla_calendarios.route("/api/citas/<int:calendario_id>")
def api_citas(calendario_id):
    citas = obtener_citas(calendario_id)
    return jsonify(citas)

@tabla_calendarios.route("/api/citas/crear", methods=['POST'])
def crear_cita():
    try:
        # Obtener datos del JSON enviado
        data = request.get_json()
        
        # Validar datos requeridos
        if not all(key in data for key in ['calendario_id', 'fecha', 'hora']):
            return jsonify({'error': 'Faltan datos requeridos'}), 400
            
        # Preparar datos para inserción
        calendario_id = data['calendario_id']
        fecha = data['fecha']
        hora = data['hora']
        estado = data.get('estado', 'confirmada')
        
        # Datos adicionales del paciente si están disponibles
        paciente = data.get('paciente', '')
        documento = data.get('documento', '')
        telefono = data.get('telefono', '')
        examen = data.get('examen', '')
        
        # Insertar en la base de datos
        conn = mysql.connection.cursor()
        query = "INSERT INTO citas (calendario_id, fecha, hora, estado, paciente, documento, telefono, examen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        conn.execute(query, (calendario_id, fecha, hora, estado, paciente, documento, telefono, examen))
        mysql.connection.commit()
        
        # Obtener el ID de la cita insertada
        cita_id = conn.lastrowid
        conn.close()
        
        return jsonify({
            'id': cita_id,
            'mensaje': 'Cita creada exitosamente',
            'calendario_id': calendario_id,
            'fecha': fecha,
            'hora': hora
        })
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        return jsonify({'error': str(e)}), 500

# Asegúrate de registrar el blueprint
app.register_blueprint(tabla_calendarios)

if __name__ == "__main__":
    app.run(debug=True)
