from flask import Flask, jsonify, request
from flask.blueprints import Blueprint
from database.config import db_conexion, db
from sqlalchemy import text

app = Flask(__name__)
db_conexion(app)

espacios_api = Blueprint('espacios_api', __name__)

@espacios_api.route('/api/espacios-disponibles', methods=['GET'])
def verificar_espacio():
    id_calendario = request.args.get('id_calendario')
    fecha = request.args.get('fecha')
    hora = request.args.get('hora')

    if not id_calendario or not fecha or not hora:
        return jsonify({'error': 'Faltan parámetros'}), 400

    query = """
        SELECT estado FROM citas 
        WHERE id_calendario = :id_calendario AND fecha = :fecha AND hora = :hora
    """
    resultado = db.session.execute(text(query), {
        'id_calendario': id_calendario,
        'fecha': fecha,
        'hora': hora
    }).fetchone()

    if resultado is None:
        estado = 'disponible'
    else:
        estado = 'ocupado'

    return jsonify({
        'estado': estado,
        'fecha': fecha,
        'hora': hora,
        'id_calendario': id_calendario
    }), 200

@espacios_api.route('/api/espacios-por-fecha', methods=['GET'])
def espacios_por_fecha():
    """Obtiene todos los espacios disponibles para una fecha específica"""
    id_calendario = request.args.get('id_calendario')
    fecha = request.args.get('fecha')
    
    if not id_calendario or not fecha:
        return jsonify({'error': 'Faltan parámetros'}), 400
    
    query = """
        SELECT hora, COALESCE(h.estado, true) as estado
        FROM citas h
        WHERE h.id_calendario = :id_calendario
        ORDER BY h.hora
    """
    resultados = db.session.execute(text(query), {'id_calendario': id_calendario}).fetchall()
    
    espacios = [{
        'hora': str(r[0]) if r[0] else None,
        'estado': r[1]
    } for r in resultados]
    
    return jsonify({
        'fecha': fecha,
        'id_calendario': id_calendario,
        'espacios': espacios
    }), 200

@espacios_api.route('/api/reservar-cita', methods=['POST'])
def reservar_cita():
    """Crea una nueva reserva de cita"""
    id_calendario = request.args.get('id_calendario')
    fecha = request.args.get('fecha')
    hora = request.args.get('hora')
    id_paciente = request.args.get('id_paciente')
    id_usuario = request.args.get('id_usuario')
    id_procedimiento = request.args.get('id_procedimiento')
    
    if not id_calendario or not fecha or not hora:
        return jsonify({'error': 'Faltan parámetros'}), 400
    
    query = """
        SELECT estado FROM citas
        WHERE id_calendario = :id_calendario AND fecha = :fecha AND hora = :hora
    """
    resultado = db.session.execute(text(query), {
        'id_calendario': id_calendario,
        'fecha': fecha,
        'hora': hora
    }).fetchone()
    
    if resultado is not None:
        return jsonify({'error': 'El espacio ya no está disponible'}), 409
    
    resultado_estado = "false"
    query = """
        INSERT INTO citas (id_calendario, fecha, hora, id_paciente, estado, id_usuario, id_procedimiento)
        VALUES (:id_calendario, :fecha, :hora, :id_paciente, :estado, :id_usuario, :id_procedimiento)
    """
    result = db.session.execute(text(query), {
        'id_calendario': id_calendario,
        'fecha': fecha,
        'hora': hora,
        'id_paciente': id_paciente,
        'estado': resultado_estado,
        'id_usuario': id_usuario,
        'id_procedimiento': id_procedimiento
    })
    db.session.commit()
    id_cita = result.lastrowid if hasattr(result, 'lastrowid') else None
    
    return jsonify({
        'mensaje': 'Cita agendada exitosamente',
        'id_cita': id_cita,
        'estado': false
    }), 201

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # corre en otro puerto si es separado

