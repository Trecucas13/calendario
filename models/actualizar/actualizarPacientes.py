from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify
from database.config import db
from sqlalchemy import text
import traceback

# Creación del Blueprint para actualizar usuarios
actualizar_pacientes = Blueprint("actualizar_pacientes", __name__)


@actualizar_pacientes.route("/actualizar_pacientes", methods=["POST"])
def update_paciente():
    """
    Función que maneja la actualización de datos de un usuario en la base de datos.
    No actualiza la contraseña.
    """
    try:
        # Obtener datos del formulario
        id_paciente = request.form["id"]
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        tipo_documento = request.form["tipo_documento"]
        documento = request.form["documento"]
        telefono = request.form["telefono"]
        direccion = request.form["direccion"]
        fecha_nacimiento = request.form["fecha_nacimiento"]
        procedimiento = request.form["examen_realizar"]
        
        # Actualizar usuario sin modificar la contraseña
        sql = text("""UPDATE pacientes SET 
                 nombre = :nombre,
                 apellido = :apellido,
                 tipo_documento = :tipo_documento,
                 numero_documento = :documento,
                 telefono = :telefono,
                 direccion = :direccion,
                 fecha_nacimiento = :fecha_nacimiento
                 WHERE id = :id_paciente""")
        db.session.execute(sql, {
            "nombre": nombre,
            "apellido": apellido,
            "tipo_documento": tipo_documento,
            "documento": documento,
            "telefono": telefono,
            "direccion": direccion,
            "fecha_nacimiento": fecha_nacimiento,
            "id_paciente": id_paciente
        })
        db.session.commit()
        
        flash("Paciente actualizado exitosamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar paciente: {str(e)}", "error")
        print(traceback.format_exc())
    
    # Redireccionar a la página de listado de usuarios
    return redirect("/pacientes")