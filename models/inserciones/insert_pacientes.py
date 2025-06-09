from flask import Blueprint, flash, render_template, request, redirect, url_for # render_template no se usa aquí.
from database.config import mysql # Objeto para la conexión a la base de datos.
import traceback # Para un logging de errores más detallado.

# Lógica para insertar nuevos registros de pacientes.

# Creación del Blueprint para las rutas de inserción de pacientes.
insertar_pacientes_bp = Blueprint("insertar_pacientes", __name__, template_folder='templates')
# Se renombra el Blueprint para consistencia.

@insertar_pacientes_bp.route("/insertar_pacientes", methods=["POST", "GET"])
# Asumo que esta ruta debería estar protegida por @login_required.
# Ejemplo:
# @login_required
# @role_required(ROL_ADECUADO) # Definir el rol que puede insertar pacientes.
def insert_pacientes():
    """
    Maneja la inserción de un nuevo paciente en la base de datos.

    Este endpoint se activa principalmente mediante una solicitud POST (al enviar un formulario).
    Recoge los datos del paciente desde el formulario y los inserta en la tabla 'pacientes'.
    Maneja varios tipos de excepciones (KeyError, ValueError, Exception general) y
    muestra mensajes flash al usuario.

    Si la solicitud es GET, simplemente redirige a la página de listado de pacientes.

    Args:
        None (obtiene los datos del `request.form`).

    Returns:
        Response: Redirige a la página "/pacientes" después de la operación o en caso de error.
                  Muestra mensajes flash para indicar éxito o diferentes tipos de error.
    """
    cur = None # Inicializa cur para el bloque finally.
    if request.method == "POST": # Procesa solo si el método es POST.
        try:
            # --- Recolección de datos del formulario ---
            # Se asume que los nombres de los campos en el formulario coinciden con las claves usadas aquí.
            nombre = request.form["nombre"]
            apellido = request.form["apellido"]
            tipo_documento = request.form["tipo_documento"]
            numero_documento = request.form["numero_documento"]
            telefono = request.form["telefono"]
            direccion = request.form["direccion"]
            fecha_nacimiento = request.form["fecha_nacimiento"]
           
            # print("Datos recibidos: ", request.form) # Útil para depuración, se puede mantener comentado.

            # --- Inserción en la tabla 'pacientes' ---
            cur = mysql.connection.cursor() # Crea un cursor para la base de datos.
            cur.execute(
                """INSERT INTO pacientes(
                    nombre, apellido, tipo_documento, numero_documento,
                    telefono, direccion, fecha_nacimiento
                   ) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    nombre, apellido, tipo_documento, numero_documento,
                    telefono, direccion, fecha_nacimiento
                ), 
            )

            mysql.connection.commit() # Confirma la transacción.
            flash("Paciente insertado exitosamente.", "success") # Mensaje de éxito.

        except KeyError as ke:
            # Error si falta un campo esperado en el formulario.
            if cur and mysql.connection.open: mysql.connection.rollback() # Revierte los cambios.
            error_msg = f"Error: Campo requerido no encontrado en el formulario: {str(ke)}"
            flash(error_msg, "danger")
            print(error_msg)
            traceback.print_exc()

        except ValueError as ve:
            # Error si un campo tiene un tipo de dato incorrecto.
            if cur and mysql.connection.open: mysql.connection.rollback()
            error_msg = f"Error en el tipo de datos proporcionado: {str(ve)}"
            flash(error_msg, "danger")
            print(error_msg)
            traceback.print_exc()

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            if cur and mysql.connection.open: mysql.connection.rollback()
            error_msg = f"Error inesperado al insertar el paciente: {str(e)}"
            flash(error_msg, "danger")
            print(error_msg)
            traceback.print_exc()

        finally:
            # Asegura que el cursor se cierre si fue abierto.
            if cur:
                cur.close()

    # Redirige al usuario a la página de listado de pacientes.
    # Esta redirección ocurre tanto si es POST (después del try-except-finally) como si es GET.
    return redirect(url_for("pacientes.pacientes")) # El original era redirect("/pacientes").
                                                 # Ajustar "pacientes.pacientes" al endpoint correcto del listado de pacientes.