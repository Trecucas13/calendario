# Utilidades o lógica relacionada con la gestión de 'espacios' o 'slots' de calendario.
# Este archivo define una API Flask para verificar disponibilidad, listar espacios y reservar citas.
# Puede funcionar como un microservicio o ser parte de una aplicación Flask más grande.

from flask import Flask, jsonify, request
from flask.blueprints import Blueprint
from database.config import db_conexion, mysql # Para la configuración y conexión a la BD.
from flask_mysqldb import MySQLdb # Para tipos de cursor como DictCursor.
import traceback # Para logging de errores.

# --- Inicialización de Aplicación Flask y Conexión a BD (si se ejecuta como standalone) ---
# Si este Blueprint se importa en otra aplicación Flask principal (como app.py),
# esta inicialización de 'app' y 'db_conexion(app)' no sería necesaria aquí,
# ya que la app principal se encargaría de ello.
app = Flask(__name__) # Crea una instancia de Flask.
db_conexion(app) # Configura la conexión a la base de datos para esta instancia de app.

# --- Creación del Blueprint para la API de Espacios ---
espacios_api = Blueprint('espacios_api', __name__) # Define el Blueprint.

@espacios_api.route('/api/espacios-disponibles', methods=['GET'])
def verificar_espacio():
    """
    Verifica si un espacio de cita específico está disponible en un calendario.

    Parámetros de consulta (query parameters):
        id_calendario (str/int): ID del calendario.
        fecha (str): Fecha de la cita (formato YYYY-MM-DD).
        hora (str): Hora de la cita (formato HH:MM o HH:MM:SS).

    Returns:
        JSON: Un objeto JSON indicando el estado ('disponible' u 'ocupado') del espacio,
              junto con los datos de la consulta.
              Código 200 OK si la verificación es exitosa.
              Código 400 Bad Request si faltan parámetros.
              Código 500 Internal Server Error si ocurre un error en el servidor.
    """
    conn = None # Inicializa conn para el bloque finally.
    try:
        # Obtiene los parámetros de la URL.
        id_calendario = request.args.get('id_calendario')
        fecha = request.args.get('fecha')
        hora = request.args.get('hora')

        # Valida que todos los parámetros necesarios estén presentes.
        if not id_calendario or not fecha or not hora:
            return jsonify({'error': 'Faltan parámetros (id_calendario, fecha, hora son requeridos)'}), 400

        conn = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # Cursor que devuelve diccionarios.
        # Consulta para verificar si ya existe una cita en el espacio especificado.
        query = """
            SELECT estado FROM citas
            WHERE id_calendario = %s AND fecha = %s AND hora = %s
        """
        conn.execute(query, (id_calendario, fecha, hora))
        resultado_cita = conn.fetchone() # Obtiene la primera fila (si existe).

        if resultado_cita is None:
            estado_espacio = 'disponible' # Si no hay resultado, el espacio está disponible.
        else:
            # Si hay resultado, el espacio está ocupado (podría usarse resultado_cita['estado'] si fuera relevante).
            estado_espacio = 'ocupado'

        return jsonify({
            'estado': estado_espacio,
            'fecha': fecha,
            'hora': hora,
            'id_calendario': id_calendario
        }), 200
    except Exception as e:
        print(f"Error en verificar_espacio: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()


@espacios_api.route('/api/espacios-por-fecha', methods=['GET'])
def espacios_por_fecha():
    """
    Obtiene todos los horarios y su estado (disponible/ocupado) para una fecha específica en un calendario.

    Parámetros de consulta (query parameters):
        id_calendario (str/int): ID del calendario.
        fecha (str): Fecha para la cual se consultan los espacios (formato YYYY-MM-DD).

    Returns:
        JSON: Un objeto JSON con la fecha, id_calendario y una lista de 'espacios',
              donde cada espacio tiene 'hora' y 'estado'.
              Código 200 OK si la consulta es exitosa.
              Código 400 Bad Request si faltan parámetros.
              Código 500 Internal Server Error si ocurre un error en el servidor.
    """
    conn = None
    try:
        id_calendario = request.args.get('id_calendario')
        fecha = request.args.get('fecha')
        
        if not id_calendario or not fecha:
            return jsonify({'error': 'Faltan parámetros (id_calendario, fecha son requeridos)'}), 400

        conn = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Consulta para obtener todas las horas de citas y su estado para un calendario y fecha dados.
        # COALESCE se usa para mostrar 'disponible' si el estado es NULL (lo cual no debería ocurrir si la cita existe).
        # Esta query podría mejorarse para listar TODOS los slots posibles y luego marcar los ocupados.
        # Actualmente solo lista los slots que YA SON CITAS.
        query = """
            SELECT hora, estado FROM citas h -- COALESCE(h.estado, 'disponible') as estado (esta lógica es para todos los slots)
            WHERE h.id_calendario = %s AND h.fecha = %s
            ORDER BY h.hora
        """
        # Para obtener todos los slots y su estado, se necesitaría una tabla de slots o generarlos y hacer LEFT JOIN.
        # La query actual solo devuelve citas existentes y su estado.

        conn.execute(query, (id_calendario, fecha)) # Falta el parámetro de fecha en la consulta original.
        resultados_citas = conn.fetchall()

        # Convierte objetos timedelta (si 'hora' es de tipo TIME en BD) a string.
        espacios_procesados = []
        for r in resultados_citas:
            hora_str = str(r["hora"]) # Conversión simple a string. Podría necesitar formateo específico.
            # Si r["hora"] es timedelta:
            # total_seconds = int(r["hora"].total_seconds())
            # hours, remainder = divmod(total_seconds, 3600)
            # minutes, seconds = divmod(remainder, 60)
            # hora_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            espacios_procesados.append({
                'hora': hora_str,
                'estado': r["estado"]
            })

        return jsonify({
            'fecha': fecha,
            'id_calendario': id_calendario,
            'espacios': espacios_procesados # Lista de espacios con su estado.
        }), 200
    except Exception as e:
        print(f"Error en espacios_por_fecha: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@espacios_api.route('/api/reservar-cita', methods=['POST'])
def reservar_cita():
    """
    Crea una nueva reserva de cita si el espacio está disponible.

    Parámetros de consulta (query parameters, aunque para POST sería mejor usar el cuerpo JSON):
        id_calendario (str/int): ID del calendario.
        fecha (str): Fecha de la cita (YYYY-MM-DD).
        hora (str): Hora de la cita (HH:MM o HH:MM:SS).
        id_paciente (str/int): ID del paciente.
        id_usuario (str/int): ID del usuario que realiza la reserva (ej. personal médico).

    Returns:
        JSON: Mensaje de éxito con id_cita y estado 'ocupado' si la reserva es exitosa (Código 201 Created).
              Mensaje de error si faltan parámetros (Código 400 Bad Request).
              Mensaje de error si el espacio ya no está disponible (Código 409 Conflict).
              Mensaje de error si ocurre un error interno (Código 500 Internal Server Error).
    """
    conn = None
    try:
        # Obtiene parámetros. Para un POST, es más común usar request.json o request.form.
        # Usar request.args para POST no es estándar pero es lo que está en el original.
        id_calendario = request.args.get('id_calendario')
        fecha = request.args.get('fecha')
        hora = request.args.get('hora')
        id_paciente = request.args.get('id_paciente')
        id_usuario = request.args.get('id_usuario') # Usuario que agenda la cita (ej. personal).

        # Valida datos requeridos.
        if not all([id_calendario, fecha, hora, id_paciente, id_usuario]): # Todos son requeridos.
            return jsonify({'error': 'Faltan parámetros requeridos (id_calendario, fecha, hora, id_paciente, id_usuario)'}), 400

        conn = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # --- Verificar disponibilidad del espacio ---
        query_verificar = """
            SELECT estado FROM citas
            WHERE id_calendario = %s AND fecha = %s AND hora = %s
        """
        conn.execute(query_verificar, (id_calendario, fecha, hora))
        cita_existente = conn.fetchone()

        if cita_existente is not None: # Si ya existe una cita en ese horario.
            # El espacio está ocupado.
            return jsonify({'error': 'El espacio de cita seleccionado ya no está disponible.'}), 409 # 409 Conflict.

        # --- Crear la nueva cita ---
        estado_nueva_cita = "ocupado" # Estado inicial de la cita al ser reservada.
        # El id_procedimiento no se está recibiendo, se omite del INSERT o se necesitaría añadir.
        query_insertar = """
            INSERT INTO citas (id_calendario, fecha, hora, id_paciente, estado, id_usuario)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        conn.execute(query_insertar, (
            id_calendario, fecha, hora, id_paciente, estado_nueva_cita, id_usuario
        ))
        mysql.connection.commit() # Confirma la transacción.
        id_cita_creada = conn.lastrowid # Obtiene el ID de la cita recién insertada.

        return jsonify({
            'mensaje': 'Cita agendada exitosamente.',
            'id_cita': id_cita_creada,
            'estado': estado_nueva_cita # Devuelve el estado de la cita creada.
        }), 201 # 201 Created.
    except Exception as e:
        if conn and mysql.connection.open: # Verifica si la conexión está activa.
             mysql.connection.rollback() # Revierte en caso de error.
        print(f"Error en reservar_cita: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

# --- Bloque de Ejecución Principal (si se ejecuta como standalone) ---
if __name__ == '__main__':
    """
    Punto de entrada para ejecutar esta API Flask de forma independiente.

    Útil para desarrollo o si esta API funciona como un microservicio separado.
    - `debug=True`: Activa el modo de depuración. ¡No usar en producción!
    - `port=5001`: Especifica el puerto en el que correrá la aplicación (diferente del 5000 usual).
    """
    app.run(debug=True, port=5001) # Corre en el puerto 5001.

