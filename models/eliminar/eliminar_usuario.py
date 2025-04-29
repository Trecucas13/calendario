from flask import Blueprint, request, redirect, url_for, flash
from database.config import mysql

delete_usuarios= Blueprint('delete_usuarios', __name__)

@delete_usuarios.route("/eliminar_usuario", methods=['POST'])
def delete_usuario():
    try:
        id = request.form.get('id')  # Usar get() en lugar de ['id'] para evitar KeyError
        if not id:
            flash('ID de usuario no proporcionado', 'error')
            return redirect(url_for('vista_usuarios.tabla_usuarios'))  # Redirigir a la lista de usuarios
        #     return 'ID de usuario no proporcionado', 400
        
        cursor = mysql.connection.cursor()
        
        cursor.execute("DELETE FROM citas WHERE id_usuario = %s", (id,))
        mysql.connection.commit()
        
        cursor.execute("DELETE FROM calendarios WHERE id_usuario = %s", (id,))
        mysql.connection.commit()
        # usuario = cursor.fetchone()
        
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        
        return redirect(url_for('vista_usuarios.tabla_usuarios'))  # Redirigir a la lista de usuarios
        
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        mysql.connection.rollback()
        return 'Error al eliminar usuario', 500