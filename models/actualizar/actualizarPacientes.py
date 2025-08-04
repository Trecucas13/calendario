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
        if not id_paciente or id_paciente == "None":
            flash("ID de paciente no proporcionado. No se puede actualizar.", "error")
            print("ID de paciente no proporcionado. No se puede actualizar.")
            return redirect("/pacientes")
        id_paciente = int(id_paciente)
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        tipo_documento = request.form["tipo_documento"]
        documento = request.form["documento"]
        telefono = request.form["telefono"]
        direccion = request.form["direccion"]
        fecha_nacimiento = request.form["fecha_nacimiento"]
        # Obtener el nuevo procedimiento seleccionado
        examen_realizar = request.form.get("examen_realizar")
        
        # Actualizar usuario sin modificar la contraseña
        sql = text("""UPDATE pacientes SET 
                 nombre = :nombre,
                 apellido = :apellido,
                 tipo_documento = :tipo_documento,
                 numero_documento = :documento,
                 telefono = :telefono,
                 direccion = :direccion,
                 fecha_nacimiento = :fecha_nacimiento,
                 
                 WHERE id = :id_paciente""")
        result = db.session.execute(sql, {
            "nombre": nombre,
            "apellido": apellido,
            "tipo_documento": tipo_documento,
            "documento": documento,
            "telefono": telefono,
            "direccion": direccion,
            "fecha_nacimiento": fecha_nacimiento,
            "id_paciente": id_paciente
        })
        print(f"Filas actualizadas en pacientes: {result.rowcount}")
        # Actualizar procedimiento en citas para este paciente
        if examen_realizar:
            sql_cita = text("""UPDATE citas SET id_procedimiento = :examen_realizar WHERE id_paciente = :id_paciente""")
            cita_result = db.session.execute(sql_cita, {"examen_realizar": examen_realizar, "id_paciente": id_paciente})
            print(f"Filas actualizadas en citas: {cita_result.rowcount}")
        # Confirmar cambios en ambas tablas
        db.session.commit()
        
        flash("Paciente actualizado exitosamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar paciente: {str(e)}", "error")
        print(traceback.format_exc())
    
    # Redireccionar a la página de listado de usuarios
    return redirect("/pacientes")