from flask import Blueprint, flash, render_template, request, redirect, url_for # render_template no se usa aquí.
from database.config import mysql # Objeto para la conexión a la base de datos.
import traceback # Para un logging de errores más detallado.

# Lógica para insertar nuevos registros de usuarios.

# Creación del Blueprint para las rutas de inserción de usuarios.
insertar_usuario_bp = Blueprint("insertar_usuario", __name__, template_folder='templates')
# Se renombra el Blueprint para consistencia.

@insertar_usuario_bp.route("/insertar_usuario", methods=["POST", "GET"])
# Asumo que esta ruta debería estar protegida por @login_required y @role_required (solo admin puede crear usuarios).
# Ejemplo:
# @login_required
# @role_required(1) # Rol de Administrador
def insert_usuario():
    """
    Maneja la inserción de un nuevo usuario en la base de datos.

    Este endpoint se activa principalmente mediante una solicitud POST (al enviar un formulario de creación de usuario).
    Recoge el nombre, documento y rol del usuario desde el formulario.
    Importante: Asigna una contraseña predeterminada ("saviaSalud*2025_") a todos los usuarios nuevos.
    Esto es una práctica de seguridad muy pobre y debería cambiarse idealmente por un sistema
    de generación de contraseñas seguras o un flujo de establecimiento de contraseña por el usuario.

    Maneja varios tipos de excepciones (KeyError, ValueError, Exception general) y
    muestra mensajes flash al usuario.

    Si la solicitud es GET, simplemente redirige a la tabla de usuarios.

    Args:
        None (obtiene los datos del `request.form`).

    Returns:
        Response: Redirige a la tabla de usuarios (endpoint 'vista_usuarios.tabla_usuarios')
                  después de la operación o en caso de error.
                  Muestra mensajes flash para indicar éxito o diferentes tipos de error.
    """
    cur = None # Inicializa cur para el bloque finally.
    # Solo procesar si es una solicitud POST.
    if request.method == "POST":
        try:
            # --- Recolección de datos del formulario ---
            nombre = request.form["nombre"] # Nombre completo del usuario.
            documento = request.form["documento"] # Número de documento del usuario.
            rol = request.form["rol"] # Rol asignado al usuario.
            
            # --- Asignación de contraseña predeterminada ---
            # ¡ADVERTENCIA DE SEGURIDAD! Usar una contraseña predeterminada y hardcodeada es inseguro.
            # Considerar mecanismos para que el usuario establezca su contraseña o generar una aleatoria y segura.
            password_predeterminada = "saviaSalud*2025_"
           
            # print("Datos recibidos: ", request.form) # Útil para depuración.

            # --- Inserción en la tabla 'usuarios' ---
            cur = mysql.connection.cursor() # Crea un cursor para la base de datos.
            cur.execute(
                """INSERT INTO usuarios(nombre, documento, password, rol)
                   VALUES (%s, %s, %s, %s)""",
                (nombre, documento, password_predeterminada, rol),
            )

            mysql.connection.commit() # Confirma la transacción.
            flash("Usuario insertado exitosamente. Recuerde la contraseña predeterminada.", "success") # Mensaje de éxito.

        except KeyError as ke:
            # Error si falta un campo esperado en el formulario.
            if cur and mysql.connection.open: mysql.connection.rollback()
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
            # Es importante verificar si la conexión y el cursor existen antes de intentar rollback o close.
            if cur and mysql.connection.open: mysql.connection.rollback()
            error_msg = f"Error inesperado al insertar el usuario: {str(e)}"
            flash(error_msg, "danger")
            print(error_msg)
            traceback.print_exc()

        finally:
            # Asegura que el cursor se cierre si fue abierto.
            if cur:
                cur.close()

    # Redirige al usuario a la página de listado de usuarios.
    # Esta redirección ocurre tanto si es POST (después del try-except-finally) como si es GET.
    return redirect(url_for("vista_usuarios.tabla_usuarios"))