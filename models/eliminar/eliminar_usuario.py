from flask import Blueprint, request, redirect, url_for
from database.config import mysql

delete_usuarios= Blueprint('delete_usuarios', __name__)

@delete_usuarios.route("/eliminar_usuario", methods=['POST'])
def delete_usuario():
    try:
        id = request.form.get('id')  # Usar get() en lugar de ['id'] para evitar KeyError
        if not id:
            return 'ID de usuario no proporcionado', 400
            
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        
        return redirect(url_for('ruta_de_listado_usuarios'))  # Redirigir a la lista de usuarios
        
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        mysql.connection.rollback()
        return 'Error al eliminar usuario', 500