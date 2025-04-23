from flask import Blueprint, jsonify
from database.config import mysql

citas_bp = Blueprint('citas', __name__)

@citas_bp.route('/api/citas', methods=['GET'])
def obtener_citas():
    try:
        conn = mysql.connection.cursor()
        conn.execute("""
            SELECT id_cita, fecha, hora, estado 
            FROM citas 
            ORDER BY fecha DESC, hora ASC
        """)
        citas = conn.fetchall()
        conn.close()
        return jsonify({
            'success': True,
            'data': citas,
            'error': None
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'data': None,
            'error': str(e)
        }), 500