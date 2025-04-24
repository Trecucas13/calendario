from flask import Flask, render_template, Blueprint, flash, redirect, url_for, request
from database.config import mysql
import traceback
from datetime import datetime
from flask import Flask, Blueprint, render_template, jsonify
from auth.decorators import *

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
            calendario['fecha_inicio'] = calendario['fecha_inicio'].strftime('%Y-%m-%d')
            calendario['fecha_fin'] = calendario['fecha_fin'].strftime('%Y-%m-%d')

        return datos, id_calendario
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        return [], None


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
        return [], None




def obtener_citas(id_calendario):
    try:
        conn = mysql.connection.cursor()
        if id_calendario:
            conn.execute("SELECT * FROM citas WHERE id_calendario = %s", (id_calendario,))
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
    # Obtener los datos del calendario y desempaquetar la tupla
    datos, id_ultimo_calendario = datos_calendario()
    
    # Inicializar citas como una lista vacía
    citas = []
    
    # Verificar si hay datos de calendario
    if datos and len(datos) > 0:
        # Obtener citas del primer calendario
        citas = obtener_citas(datos[0]['id'])  # Cambiar datos["id"] a datos[0]['id']
        print(citas)
    else:
        # Si no hay calendarios, obtener todas las citas
        citas = obtener_citas(None)
        
    return render_template("calendarioo.html", calendarios=datos, citas=citas)

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
        if not all(key in data for key in ['id_calendario', 'fecha', 'hora']):
            return jsonify({'error': 'Faltan datos requeridos'}), 400
            
        # Preparar datos para inserción
        id_calendario = data['id_calendario']
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
        query = "INSERT INTO citas (id_calendario, fecha, hora, estado, paciente, documento, telefono, examen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        conn.execute(query, (id_calendario, fecha, hora, estado, paciente, documento, telefono, examen))
        mysql.connection.commit()
        
        # Obtener el ID de la cita insertada
        cita_id = conn.lastrowid
        conn.close()
        
        return jsonify({
            'id': cita_id,
            'mensaje': 'Cita creada exitosamente',
            'calendario_id': id_calendario,  # Corregido: era calendario_id pero debe ser id_calendario
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
