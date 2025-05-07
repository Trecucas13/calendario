from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify
from database.config import mysql
import traceback

# Creación del Blueprint para actualizar usuarios
actualizar_pacientes = Blueprint("actualizar_pacientes", __name__)


@actualizar_pacientes.route("/actualizar_pacientes", methods=["POST"])
def update_paciente():
    """
    Función que maneja la actualización de datos de un usuario en la base de datos.
    No actualiza la contraseña.
    """
    cur = None
    
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
        
        # Iniciar conexión a la base de datos
        cur = mysql.connection.cursor() 
        
        # Actualizar usuario sin modificar la contraseña
        sql = """UPDATE pacientes SET 
                 nombre = %s,
                 apellido = %s,
                 tipo_documento = %s,
                 numero_documento = %s,
                 telefono = %s,
                 direccion = %s,
                 fecha_nacimiento = %s
                 WHERE id = %s"""
        params = (nombre, apellido, tipo_documento, documento, telefono, direccion, fecha_nacimiento, id_paciente)
        
        # Ejecutar la consulta SQL
        cur.execute(sql, params)
        mysql.connection.commit()
        
        # Mostrar mensaje de éxito
        flash("Usuario actualizado exitosamente", "success")
    
    except Exception as e:
        # Capturar cualquier error
        flash(f"Error al actualizar: {str(e)}", "error")
        traceback.print_exc()
        if mysql.connection:
            mysql.connection.rollback()
    finally:
        # Cerrar el cursor si fue creado
        if cur:
            cur.close()
    
    # Redireccionar a la página de listado de usuarios
    return redirect("/pacientes")