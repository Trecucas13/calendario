from flask import Blueprint, request, redirect, url_for, flash
from database.config import db
from sqlalchemy import text

# Blueprint para las rutas de eliminación de pacientes
borrar_pacientes = Blueprint('borrar_pacientes', __name__)

@borrar_pacientes.route('/eliminar_paciente', methods=['POST'])
def delete_paciente():
    try:
        paciente_id = request.form.get('id')
        if not paciente_id:
            flash('ID de paciente no proporcionado', 'error')
            return redirect(url_for('pacientes'))

        # Eliminar citas asociadas al paciente
        db.session.execute(
            text("DELETE FROM citas WHERE id_paciente = :id"),
            {"id": paciente_id}
        )
        db.session.commit()

        # Eliminar el paciente
        db.session.execute(
            text("DELETE FROM pacientes WHERE id = :id"),
            {"id": paciente_id}
        )
        db.session.commit()

        flash('Paciente eliminado correctamente', 'success')
        return redirect(url_for('pacientes'))

    except Exception as e:
        print(f"Error al eliminar paciente: {e}")
        db.session.rollback()
        return 'Error al eliminar paciente', 500
