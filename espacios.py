from flask import Flask, jsonify, request
from flask_cors import CORS
from flask.blueprints import Blueprint
from database.config import db_conexion, db
from sqlalchemy import text
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)
db_conexion(app)

espacios_api = Blueprint('espacios_api', __name__)

# ------------------------------ #
# RUTA 1: Verificar espacios disponibles del calendario
# ------------------------------ #
@espacios_api.route('/api/espacios-disponibles', methods=['GET'])
def verificar_espacio():
    id_calendario = request.args.get('id_calendario')
    fecha = request.args.get('fecha')
    hora = request.args.get('hora')

    if not id_calendario or not fecha or not hora:
        return jsonify({'success': False, 'error': 'Faltan parámetros'}), 400

    query = """
        SELECT estado FROM citas 
        WHERE id_calendario = :id_calendario AND fecha = :fecha AND hora = :hora
    """
    resultado = db.session.execute(text(query), {
        'id_calendario': id_calendario,
        'fecha': fecha,
        'hora': hora
    }).fetchone()

    estado = 'ocupado' if resultado else 'disponible'

    return jsonify({
        'success': True,
        'estado': estado,
        'fecha': fecha,
        'hora': hora,
        'id_calendario': id_calendario
    }), 200


# ------------------------------ #
# RUTA 2: Espacios disponibles por fecha
# ------------------------------ #
@espacios_api.route('/api/espacios-por-fecha', methods=['GET'])
def espacios_por_fecha():
    id_calendario = request.args.get('id_calendario')
    fecha = request.args.get('fecha')

    if not id_calendario or not fecha:
        return jsonify({'success': False, 'error': 'Faltan parámetros'}), 400

    # 1. Obtener datos del calendario
    query_cal = """
        SELECT hora_inicio, hora_fin, inicio_hora_descanso, fin_hora_descanso, espacio_citas
        FROM calendarios WHERE id_calendario = :id_calendario
    """
    cal = db.session.execute(text(query_cal), {'id_calendario': id_calendario}).fetchone()
    if not cal:
        return jsonify({'success': False, 'error': 'Calendario no encontrado'}), 404

    hora_inicio, hora_fin, inicio_descanso, fin_descanso, espacio_citas = cal

    # 2. Obtener horas ocupadas para esa fecha
    query_citas = """
        SELECT hora FROM citas WHERE id_calendario = :id_calendario AND fecha = :fecha
    """
    ocupadas = db.session.execute(text(query_citas), {'id_calendario': id_calendario, 'fecha': fecha}).fetchall()
    ocupadas_set = set(h.strftime('%H:%M') for (h,) in ocupadas)

    # 3. Generar todas las horas posibles para esa fecha
    espacios_disponibles = []
    hora_actual = datetime.combine(datetime.today(), hora_inicio)
    hora_limite = datetime.combine(datetime.today(), hora_fin)
    while hora_actual <= hora_limite:
        hora_str = hora_actual.time().strftime('%H:%M')
        # Excluir horario de descanso y ocupados
        if not (inicio_descanso <= hora_actual.time() < fin_descanso):
            if hora_str not in ocupadas_set:
                espacios_disponibles.append(hora_str)
        hora_actual += timedelta(minutes=espacio_citas)

    return jsonify({
        'success': True,
        'id_calendario': id_calendario,
        'fecha': fecha,
        'horas_disponibles': espacios_disponibles
    }), 200

# ------------------------------ #
# RUTA 3: Reservar una cita
# ------------------------------ #
@espacios_api.route('/api/reservar-cita', methods=['POST'])
def reservar_cita():
    if not request.is_json:
        return jsonify({'success': False, 'error': 'El cuerpo debe ser JSON'}), 400

    data = request.get_json()
    print(f"Datos recibidos: {data}")
    print("Headers:", dict(request.headers))
    print("Raw data:", request.data)
    print("is_json:", request.is_json)

    required = ['id_calendario', 'fecha', 'hora', 'id_paciente', 'id_usuario', 'id_procedimiento']
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({'success': False, 'error': f'Faltan parámetros: {", ".join(missing)}', 'data_recibida': data}), 400

    id_calendario = data['id_calendario']
    fecha = data['fecha']
    hora = data['hora']
    id_paciente = data['id_paciente']
    id_usuario = data['id_usuario']
    id_procedimiento = data['id_procedimiento']

    # Verifica si el espacio ya está ocupado
    query_check = """
        SELECT 1 FROM citas
        WHERE id_calendario = :id_calendario AND fecha = :fecha AND hora = :hora
    """
    existe = db.session.execute(text(query_check), {
        'id_calendario': id_calendario,
        'fecha': fecha,
        'hora': hora
    }).fetchone()

    if existe:
        return jsonify({'success': False, 'error': 'El espacio ya no está disponible', 'data_recibida': data}), 409

    estado = "false"
    query_insert = """
        INSERT INTO citas (id_calendario, fecha, hora, id_paciente, estado, id_usuario, id_procedimiento)
        VALUES (:id_calendario, :fecha, :hora, :id_paciente, :estado, :id_usuario, :id_procedimiento)
    """
    result = db.session.execute(text(query_insert), {
        'id_calendario': id_calendario,
        'fecha': fecha,
        'hora': hora,
        'id_paciente': id_paciente,
        'estado': estado,
        'id_usuario': id_usuario,
        'id_procedimiento': id_procedimiento
    })
    db.session.commit()
    id_cita = result.lastrowid if hasattr(result, 'lastrowid') else None

    return jsonify({
        'success': True,
        'mensaje': 'Cita agendada exitosamente',
        'id_cita': id_cita,
        'estado': estado,
        'data_recibida': data
    }), 201

# ------------------------------ #
# NUEVA RUTA 4: Info completa del calendario
# ------------------------------ #
@espacios_api.route('/api/calendario/<int:id_calendario>', methods=['GET'])
def obtener_info_calendario(id_calendario):
    query = """
        SELECT 
            id_calendario, nombre_calendario, fecha_inicio, fecha_fin, hora_inicio, hora_fin, estado,
            id_procedimiento, id_municipio, espacio_citas AS espacio_entre_citas, inicio_hora_descanso, fin_hora_descanso
        FROM calendarios
        WHERE id_calendario = :id_calendario
    """
    resultado = db.session.execute(text(query), {'id_calendario': id_calendario}).fetchone()

    if not resultado:
        return jsonify({'success': False, 'error': 'Calendario no encontrado'}), 404

    columnas = [
        'id_calendario', 'nombre_calendario', 'fecha_inicio', 'fecha_fin', 'hora_inicio', 'hora_fin',
        'estado', 'id_procedimiento', 'id_municipio', 'espacio_entre_citas', 'inicio_hora_descanso', 'fin_hora_descanso'
    ]

    # Convierte los campos de hora a string
    resultado = list(resultado)
    for idx, col in enumerate(columnas):
        if 'hora' in col and resultado[idx] is not None:
            resultado[idx] = str(resultado[idx])

    return jsonify({
        'success': True,
        'calendarios': dict(zip(columnas, resultado))
    })


@espacios_api.route('/api/calendario', methods=['GET'])
def obtener_info_calendarios():
    query = """
        SELECT 
            id_calendario, nombre_calendario, fecha_inicio, fecha_fin, hora_inicio, hora_fin, estado,
            id_procedimiento, id_municipio, espacio_citas, inicio_hora_descanso, fin_hora_descanso
        FROM calendarios
    """
    resultados = db.session.execute(text(query)).fetchall()

    if not resultados:
        return jsonify({'success': False, 'error': 'Calendario no encontrado'}), 404

    columnas = [
        'id_calendario', 'nombre_calendario', 'fecha_inicio', 'fecha_fin', 'hora_inicio', 'hora_fin',
        'estado', 'id_procedimiento', 'id_municipio', 'espacio_citas', 'inicio_hora_descanso', 'fin_hora_descanso'
    ]

    calendarios = []
    for fila in resultados:
        fila = list(fila)
        for idx, col in enumerate(columnas):
            if 'hora' in col and fila[idx] is not None:
                fila[idx] = str(fila[idx])
        calendarios.append(dict(zip(columnas, fila)))

    return jsonify({
        'success': True,
        'calendarios': calendarios
    })



# ------------------------------ #
# NUEVA RUTA 5: Info de pacientes con citas
# ------------------------------ #
@espacios_api.route('/api/pacientes', methods=['GET'])
def obtener_info_pacientes():
    query = """
        SELECT 
            p.id, p.nombre, p.apellido, p.tipo_documento, p.numero_documento,
            c.id_calendario, c.fecha, c.hora, c.id_procedimiento, c.estado
        FROM pacientes p
        JOIN citas c ON p.id = c.id_paciente
        ORDER BY c.fecha, c.hora
    """
    resultados = db.session.execute(text(query)).fetchall()

    pacientes = []
    for row in resultados:
        pacientes.append({
            'id': row[0],
            'nombre': row[1],
            'apellido': row[2],
            'tipo_documento': row[3],
            'numero_documento': row[4],
            'id_calendario': row[5],
            'fecha': str(row[6]),
            'hora': str(row[7]),
            'procedimiento': row[8],
            'estado_cita': row[9]
        })

    return jsonify({
        'success': True,
        'pacientes': pacientes
    })




@espacios_api.route('/api/pacientes/<int:numero_documento>', methods=['GET'])
def obtener_info_paciente(numero_documento):
    
    query = """
        SELECT 
            p.id, p.nombre, p.apellido, p.tipo_documento, p.numero_documento,
            c.id_calendario, c.fecha, c.hora, c.id_procedimiento, c.estado
        FROM pacientes p
        JOIN citas c ON p.id = c.id_paciente
        WHERE p.numero_documento = :numero_documento
        ORDER BY c.fecha, c.hora
    """
    row = db.session.execute(text(query), {'numero_documento': numero_documento}).fetchone()

    if not row:
        return jsonify({'success': False, 'error': 'Paciente no encontrado'}), 404

    paciente = {
        'id': row[0],
        'nombre': row[1],
        'apellido': row[2],
        'tipo_documento': row[3],
        'numero_documento': row[4],
        'id_calendario': row[5],
        'fecha': str(row[6]),
        'hora': str(row[7]),
        'procedimiento': row[8],
        'estado_cita': row[9]
    }

    return jsonify({
        'success': True,
        'paciente': paciente
    })


# ------------------------------ #
# REGISTRO FINAL DEL BLUEPRINT
# ------------------------------ #
app.register_blueprint(espacios_api)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
