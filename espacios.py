from flask import Flask, jsonify, request
from flask.blueprints import Blueprint
from database.config import db_conexion, mysql

# app = Flask(__name__)
# db_conexion(app)

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
        estado = resultado[0]

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
    # Suponiendo que tienes una tabla de horarios disponibles o un rango de horas predefinido
    query = """
        SELECT hora, COALESCE(c.estado, 'disponible') as estado
        FROM horarios h
        LEFT JOIN citas c ON c.id_calendario = %s AND c.fecha = %s AND c.hora = h.hora
        WHERE h.id_calendario = %s
        ORDER BY h.hora
    """
    conn.execute(query, (id_calendario, fecha, id_calendario))
    resultados = conn.fetchall()
    conn.close()
    
    espacios = [{'hora': r[0], 'estado': r[1]} for r in resultados]
    
    return jsonify({
        'fecha': fecha,
        'id_calendario': id_calendario,
        'espacios': espacios
    }), 200

@espacios_api.route('/api/reservar-cita', methods=['POST'])
def reservar_cita():
    """Crea una nueva reserva de cita"""
    datos = request.json
    
    # Validar datos requeridos
    campos_requeridos = ['id_calendario', 'fecha', 'hora', 'nombre_paciente', 'documento_paciente']
    for campo in campos_requeridos:
        if campo not in datos:
            return jsonify({'error': f'Falta el campo {campo}'}), 400
    
    # Verificar disponibilidad
    conn = mysql.connection.cursor()
    query = """
        SELECT estado FROM citas 
        WHERE id_calendario = %s AND fecha = %s AND hora = %s
    """
    conn.execute(query, (datos['id_calendario'], datos['fecha'], datos['hora']))
    resultado = conn.fetchone()
    
    if resultado is not None and resultado[0] != 'disponible':
        conn.close()
        return jsonify({'error': 'El espacio ya no está disponible'}), 409
    
    # Crear la cita
    query = """
        INSERT INTO citas (id_calendario, fecha, hora, nombre_paciente, documento_paciente, estado)
        VALUES (%s, %s, %s, %s, %s, 'reservado')
    """
    conn.execute(query, (
        datos['id_calendario'], 
        datos['fecha'], 
        datos['hora'],
        datos['nombre_paciente'],
        datos['documento_paciente']
    ))
    mysql.connection.commit()
    id_cita = conn.lastrowid
    conn.close()
    
    return jsonify({
        'mensaje': 'Cita reservada exitosamente',
        'id_cita': id_cita,
        'estado': 'reservado'
    }), 201

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # corre en otro puerto si es separado

