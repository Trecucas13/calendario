from flask import Blueprint, request, redirect, url_for, flash
from database.config import db
from sqlalchemy import text  # Importa text para consultas SQL

# Blueprint para la eliminación de municipios
delete_municipios = Blueprint('delete_municipios', __name__)

@delete_municipios.route('/eliminar_municipio', methods=['POST'])
def delete_municipio():
    try:
        municipio_id = request.form.get('municipio_id')
        if not municipio_id:
            flash('ID de municipio no proporcionado', 'error')
            return redirect(url_for('index'))

        # Eliminar calendarios asociados al municipio (si aplica)
        db.session.execute(text("DELETE FROM calendarios WHERE id_municipio = :id"), {"id": municipio_id})
        db.session.commit()

        # Eliminar el municipio
        db.session.execute(text("DELETE FROM municipios WHERE id_municipio = :id"), {"id": municipio_id})
        db.session.commit()

        flash('Municipio eliminado correctamente', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        print(f"Error al eliminar municipio: {e}")
        db.session.rollback()
        return 'Error al eliminar municipio', 500
