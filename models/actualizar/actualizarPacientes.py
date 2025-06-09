from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify # jsonify no se usa actualmente.
from database.config import mysql # Objeto para la conexión a la base de datos.
import traceback # Para imprimir detalles de excepciones en el log/consola.

# Lógica para actualizar datos de pacientes.

# Creación del Blueprint para las rutas de actualización de pacientes.
actualizar_pacientes_bp = Blueprint("actualizar_pacientes", __name__, template_folder='templates')
# Nota: Se renombró el Blueprint a 'actualizar_pacientes_bp' para mayor claridad y consistencia.

@actualizar_pacientes_bp.route("/actualizar_pacientes", methods=["POST"])
# Asumo que esta ruta también debería estar protegida por @login_required y @role_required si maneja datos sensibles.
# Ejemplo:
# @login_required
# @role_required(1) # O el rol que corresponda
def update_paciente():
    """
    Maneja la actualización de los datos de un paciente existente en la base de datos.

    Esta función se activa mediante una solicitud POST. Recoge los datos del paciente
    desde el formulario, construye una consulta SQL de actualización para la tabla 'pacientes'
    y la ejecuta. Es importante destacar que esta función NO actualiza la contraseña
    del paciente (si la tuviera). Gestiona errores y muestra mensajes flash al usuario.
    Finalmente, redirige al listado de pacientes.

    Datos esperados del formulario:
    - id: Identificador único del paciente a actualizar.
    - nombre: Nuevo nombre del paciente.
    - apellido: Nuevo apellido del paciente.
    - tipo_documento: Nuevo tipo de documento.
    - documento: Nuevo número de documento.
    - telefono: Nuevo número de teléfono.
    - direccion: Nueva dirección.
    - fecha_nacimiento: Nueva fecha de nacimiento.

    Returns:
        Response: Una redirección a la ruta '/pacientes' (listado de pacientes).
                  Se muestran mensajes flash para indicar éxito o error.
    """
    cur = None # Inicializa cur a None para asegurar que esté definido en el bloque finally.
    
    try:
        # Obtención de los datos del formulario enviado por el método POST.
        id_paciente = request.form["id"]
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        tipo_documento = request.form["tipo_documento"]
        documento = request.form["documento"] # Asumo que este es el número de documento.
        telefono = request.form["telefono"]
        direccion = request.form["direccion"]
        fecha_nacimiento = request.form["fecha_nacimiento"]
        
        # Creación del cursor para interactuar con la base de datos.
        cur = mysql.connection.cursor() 
        
        # Consulta SQL para actualizar los datos del paciente en la tabla 'pacientes'.
        # La contraseña no se modifica en esta operación.
        sql = """UPDATE pacientes SET 
                 nombre = %s,
                 apellido = %s,
                 tipo_documento = %s,
                 numero_documento = %s,  -- Se asume que la columna se llama numero_documento
                 telefono = %s,
                 direccion = %s,
                 fecha_nacimiento = %s
                 WHERE id = %s""" # Condición para actualizar el paciente correcto.
        # Parámetros para la consulta SQL.
        params = (nombre, apellido, tipo_documento, documento, telefono, direccion, fecha_nacimiento, id_paciente)
        
        # Ejecución de la consulta SQL.
        cur.execute(sql, params)
        mysql.connection.commit() # Confirma los cambios en la base de datos.
        
        # Muestra un mensaje de éxito al usuario.
        flash("Paciente actualizado exitosamente.", "success") # Categoría 'success' para mensajes positivos.
    
    except Exception as e:
        # Captura cualquier excepción que ocurra durante el proceso.
        flash(f"Error al actualizar el paciente: {str(e)}", "danger") # Categoría 'danger' para errores.
        traceback.print_exc() # Imprime el traceback completo en la consola para depuración.
        if mysql.connection and mysql.connection.open: # Verifica si la conexión está activa.
            mysql.connection.rollback() # Revierte los cambios en la base de datos en caso de error.
    finally:
        # Asegura que el cursor se cierre, si fue abierto.
        if cur:
            cur.close()
    
    # Redirecciona al usuario a la página de listado de pacientes.
    return redirect(url_for("pacientes.pacientes")) # Asumiendo que el Blueprint de pacientes se llama 'pacientes' y la ruta 'pacientes'
                                                 # O directamente a "/pacientes" si es una ruta fija y no un endpoint de Blueprint.
                                                 # El original era redirect("/pacientes")