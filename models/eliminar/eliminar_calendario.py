from flask import Blueprint, request, redirect, url_for, flash
from database.config import db
from sqlalchemy import text  # Agrega la importación de text

delete_calendario= Blueprint('delete_calendario', __name__)

@delete_calendario.route("/eliminar_calendario", methods=['POST'])
def delete_usuario():
    try:
        id = request.form.get('id')  # Usar get() en lugar de ['id'] para evitar KeyError
        if not id:
            flash('ID de usuario no proporcionado', 'error')
            return redirect(url_for('vista_usuarios.tabla_usuarios'))  # Redirigir a la lista de usuarios
        db.session.execute(text("DELETE FROM citas WHERE id_calendario = :id"), {"id": id})
        db.session.commit()
        db.session.execute(text("DELETE FROM calendarios WHERE id_calendario = :id"), {"id": id})
        db.session.commit()
        return redirect('/index')  # Redirigir a la lista de usuarios
    except Exception as e:
        print(f"Error al eliminar calendario: {e}")
        db.session.rollback()
        return 'Error al eliminar calendario', 500