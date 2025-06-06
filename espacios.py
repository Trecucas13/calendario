from flask import Flask, jsonify, request
from flask.blueprints import Blueprint
from database.config import db_conexion, mysql

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

    conn = mysql.connection.cursor()
    query = """
        SELECT estado FROM citas 
        WHERE id_calendario = %s AND fecha = %s AND hora = %s
    """
    conn.execute(query, (id_calendario, fecha, hora))
    resultado = conn.fetchone()
    conn.close()

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
        
    conn = mysql.connection.cursor()
    query = """
        SELECT hora, COALESCE(h.estado, 'disponible') as estado
        FROM citas h
        WHERE h.id_calendario = %s
        ORDER BY h.hora
    """
    
        
    conn.execute(query, (id_calendario,))
    resultados = conn.fetchall()
    conn.close()
    
    # Convert timedelta objects to string representation
    espacios = [{
        'hora': str(r["hora"]) if r["hora"] else None,  # Convert timedelta to string
        'estado': r["estado"]
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
    # documento_paciente = request.args.get('documento_paciente')
    
    # Asignar un valor por defecto si no se proporciona
    
    # Validar datos requeridos
    if not id_calendario or not fecha or not hora:
        return jsonify({'error': 'Faltan parámetros'}), 400
    
    # Verificar disponibilidad
    conn = mysql.connection.cursor()
    query = """
        SELECT estado FROM citas
        WHERE id_calendario = %s AND fecha = %s AND hora = %s
    """
    conn.execute(query, (id_calendario, fecha, hora))
    resultado = conn.fetchone()
    
    if resultado is not None:
        # estado_finañ
        conn.close()
        return jsonify({'error': 'El espacio ya no está disponible'}), 409
    
    
    resultado = "ocupado"
    # Crear la cita
    query = """
        INSERT INTO citas (id_calendario, fecha, hora, id_paciente, estado, id_usuario)
        VALUES (%s, %s, %s, %s, %s, %s )
    """
    conn.execute(query, (
        id_calendario, 
        fecha, 
        hora,
        id_paciente,
        resultado,  # Estado inicial de la cita
        id_usuario
    ))
    mysql.connection.commit()
    id_cita = conn.lastrowid
    conn.close()
    
    return jsonify({
        'mensaje': 'Cita agendada exitosamente',
        'id_cita': id_cita,
        'estado': 'ocupado'
    }), 201

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # corre en otro puerto si es separado

