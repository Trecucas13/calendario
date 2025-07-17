from flask import Blueprint, request, redirect, url_for, flash
from database.config import db
from sqlalchemy import text  # Importa text para consultas SQL

# Blueprint para la eliminación de procedimientos
delete_procedimientos = Blueprint('delete_procedimientos', __name__)

@delete_procedimientos.route('/eliminar_procedimiento', methods=['GET','POST'])
def delete_procedimiento():
    if request.method == 'GET':
        # Si se accede por GET, redirigir a la página principal
        return redirect(url_for('index'))
    try:
        procedimiento_id = request.form.get('procedimiento_id')
        if not procedimiento_id:
            flash('ID de procedimiento no proporcionado', 'error')
            return redirect(url_for('index'))

        # Eliminar citas asociadas al procedimiento para respetar FK
        db.session.execute(text("DELETE FROM citas WHERE id_procedimiento = :id"), {"id": procedimiento_id})
        db.session.commit()

        # Eliminar calendarios asociados al procedimiento
        db.session.execute(text("DELETE FROM calendarios WHERE id_procedimiento = :id"), {"id": procedimiento_id})
        db.session.commit()

        # Eliminar el procedimiento
        db.session.execute(text("DELETE FROM procedimientos WHERE id_procedimiento = :id"), {"id": procedimiento_id})
        db.session.commit()

        flash('Procedimiento eliminado correctamente', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        print(f"Error al eliminar procedimiento: {e}")
        db.session.rollback()
        flash(f"Error al eliminar procedimiento: {e}", 'error')
        return redirect(url_for('index'))
