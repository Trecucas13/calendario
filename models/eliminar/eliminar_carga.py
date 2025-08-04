from flask import Blueprint, flash, redirect, url_for
from database.config import db
from auth.decorators import login_required, role_required
from sqlalchemy import text

# Blueprint para eliminar registros de la tabla registro_base
delete_carga = Blueprint('delete_carga', __name__)

@delete_carga.route('/gestion_bd/delete', methods=['POST'])
@login_required
@role_required([1, 2])
def delete_registro_base():
    """Eliminar todos los registros de registro_base"""
    try:
        db.session.execute(text("DELETE FROM registro_base"))
        db.session.commit()
        flash('Todos los registros base han sido eliminados.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar registros: {e}', 'danger')
    return redirect(url_for('gestion_bd.tabla_gestiones_bd'))

eliminar_carga = Blueprint('eliminar_carga', __name__)

@eliminar_carga.route('/gestion_bd/delete_base', methods=['POST'])
@login_required
@role_required([1, 2])
def delete_registro_base():
    """Eliminar todos los registros de registro_base"""
    try:
        db.session.execute(text("DELETE FROM registro_base"))
        db.session.commit()
        flash('Todos los registros base han sido eliminados.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar registros: {e}', 'danger')
    return redirect(url_for('gestion_bd.tabla_gestiones_bd'))
