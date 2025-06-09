from flask import Blueprint, flash, render_template, request, redirect, url_for, session # render_template y url_for no se usan directamente aquí.
from database.config import mysql # Objeto para la conexión a la base de datos.
import traceback # Para un logging de errores más detallado.

# Lógica para insertar nuevos registros de gestión o interacciones.

# Creación del Blueprint para las rutas de inserción de gestiones.
# El nombre original 'insertar_gestiones' es claro. Se añade _bp por convención.
insertar_gestiones_bp = Blueprint("insertar_gestiones", __name__, template_folder='templates')

@insertar_gestiones_bp.route("/insertar_gestiones", methods=["POST", "GET"])
# Asumo que esta ruta debería estar protegida por @login_required.
# Ejemplo:
# @login_required
def insert_gestiones():
    """
    Maneja la inserción de un nuevo registro de gestión en la base de datos.

    Este endpoint se activa principalmente mediante una solicitud POST (al enviar un formulario).
    Recoge datos como la tipificación, ID de llamada, comentario y el ID del registro base
    asociado. Obtiene el nombre del asesor/usuario de la sesión actual.
    Busca en la tabla `registro_base` para construir una `llave_compuesta` antes de
    insertar la gestión en la tabla `gestion`.
    Maneja varios tipos de excepciones (KeyError, ValueError, Exception general) y
    muestra mensajes flash al usuario.

    Si la solicitud es GET, simplemente redirige a "/gestionar".

    Args:
        None (obtiene los datos del `request.form` y `session`).

    Returns:
        Response: Redirige a la página "/gestionar" después de la operación o en caso de error.
                  Muestra mensajes flash para indicar éxito o diferentes tipos de error.
    """
    if request.method == "POST": # Procesa solo si el método es POST.
        nombre_asesor = session.get("nombre") # Obtiene el nombre del asesor/usuario desde la sesión.
        cur = None # Inicializa cur para el bloque finally.

        try:
            # --- Recolección de datos del formulario ---
            tipificacion = request.form["tipificacion"] # Tipo de gestión.
            idLlamada = request.form["idLlamada"] # ID de la llamada asociada.
            comentario = request.form["comentario"] # Comentarios sobre la gestión.
            registro_id = request.form["registro_id"] # ID del registro base al que se asocia esta gestión.

            # --- Obtención de datos para la llave compuesta ---
            cur = mysql.connection.cursor(dictionary=True) # Usar dictionary=True para acceder a campos por nombre.
                                                            # (Obsoleto en mysqlclient > 2, usar MySQLCursorDict)
            # Busca en la tabla `registro_base` para obtener los componentes de la llave compuesta.
            cur.execute("SELECT tipo_id, num_id, proceso FROM registro_base WHERE id = %s", (registro_id,))
            registro = cur.fetchone() # Obtiene el registro base.

            if not registro: # Si no se encuentra el registro base.
                flash("No se encontró el registro base asociado (ID: {}). No se puede crear la gestión.".format(registro_id), "danger")
                return redirect(url_for("gestionar.alguna_ruta_gestionar")) # Redirige a una página apropiada (el original era "/gestionar").
                                                                         # Asumo que "gestionar.alguna_ruta_gestionar" sería el endpoint del listado de gestiones.

            # Construye la llave compuesta.
            llave_compuesta = f"{registro['tipo_id']}-{registro['num_id']}-{registro['proceso']}"

            # --- Inserción en la tabla 'gestion' ---
            # El cursor ya está abierto.
            cur.execute(
                """INSERT INTO gestion (
                    registro_id, tipificacion, id_llamada, comentario, usuario, llave_compuesta
                   ) VALUES (%s, %s, %s, %s, %s, %s)""",
                (registro_id, tipificacion, idLlamada, comentario, nombre_asesor, llave_compuesta)
            )

            mysql.connection.commit() # Confirma la transacción.
            flash("Gestión insertada exitosamente.", "success")

        except KeyError as ke:
            # Error si falta un campo esperado en el formulario.
            mysql.connection.rollback() # Revierte los cambios.
            error_msg = f"Error: Campo requerido no encontrado en el formulario: {str(ke)}"
            flash(error_msg, "danger")
            print(error_msg)
            traceback.print_exc()

        except ValueError as ve:
            # Error si un campo tiene un tipo de dato incorrecto (ej. se esperaba int y se recibió string).
            mysql.connection.rollback()
            error_msg = f"Error en el tipo de datos proporcionado: {str(ve)}"
            flash(error_msg, "danger")
            print(error_msg)
            traceback.print_exc()

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            mysql.connection.rollback()
            error_msg = f"Error inesperado al insertar la gestión: {str(e)}"
            flash(error_msg, "danger")
            print(error_msg)
            traceback.print_exc()

        finally:
            # Asegura que el cursor se cierre si fue abierto.
            if cur:
                cur.close()

    # Redirige al usuario a la página de gestionar (o listado de gestiones).
    # Esta redirección ocurre tanto si es POST (después del try-except-finally) como si es GET.
    return redirect(url_for("gestionar.alguna_ruta_gestionar")) # El original era redirect("/gestionar").
                                                             # Ajustar "gestionar.alguna_ruta_gestionar" al endpoint correcto.