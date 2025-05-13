from flask import Flask, jsonify, request
from database.config import db_conexion, mysql

app = Flask(__name__)
db_conexion(app)

@app.route('/api/espacios-disponibles', methods=['GET'])
def verificar_espacio():
    id_calendario = request.args.get('id_calendario')
    fecha = request.args.get('fecha')      # formato: 'YYYY-MM-DD'
    hora = request.args.get('hora')        # formato: 'HH:MM'

    if not id_calendario or not fecha or not hora:
        return jsonify({'error': 'Faltan parámetros'}), 400

    conn = mysql.connection.cursor()
    query = """
        SELECT COUNT(*) FROM citas 
        WHERE id_calendario = %s AND fecha = %s AND hora = %s
    """
    conn.execute(query, (id_calendario, fecha, hora))
    resultado = conn.fetchone()
    conn.close()

    ocupado = resultado[0] > 0

    return jsonify({
        'disponible': not ocupado,
        'fecha': fecha,
        'hora': hora,
        'id_calendario': id_calendario
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # corre en otro puerto si es separado
