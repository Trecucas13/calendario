from flask import Flask, request, Blueprint, redirect, url_for
from database.config import mysql

eliminar_usuarios = Blueprint('eliminar_usuarios', __name__)

@eliminar_usuarios.route('/eliminar_usuario/<int:id>', methods=['POST'])
def eliminar_usuario(id):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))  # Use the id from URL
        mysql.connection.commit()
        cur.close()
        
    return redirect(url_for('vista_usuarios.tabla_usuarios'))  # Fixed indentation