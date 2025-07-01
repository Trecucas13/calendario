from flask import Blueprint, request, redirect, url_for, flash
from database.config import db
from sqlalchemy import text  # Importa text para consultas SQL

delete_usuarios= Blueprint('delete_usuarios', __name__)

@delete_usuarios.route("/eliminar_usuario", methods=['POST'])
def delete_usuario():
    try:
        id = request.form.get('id')  # Usar get() en lugar de ['id'] para evitar KeyError
        if not id:
            flash('ID de usuario no proporcionado', 'error')
            return redirect(url_for('vista_usuarios.tabla_usuarios'))  # Redirigir a la lista de usuarios
        
        db.session.execute(text("DELETE FROM citas WHERE id_usuario = :id"), {"id": id})
        db.session.commit()
        
        db.session.execute(text("DELETE FROM calendarios WHERE id_usuario = :id"), {"id": id})
        db.session.commit()
        
        db.session.execute(text("DELETE FROM usuarios WHERE id = :id"), {"id": id})
        db.session.commit()
        
        return redirect(url_for('vista_usuarios.tabla_usuarios'))  # Redirigir a la lista de usuarios
        
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        db.session.rollback()
        return 'Error al eliminar usuario', 500