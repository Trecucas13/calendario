from flask import Blueprint, render_template, request, redirect, url_for, flash # Se añade flash para los mensajes
from auth.decorators import login_required, role_required # Decoradores para control de acceso
from database.config import mysql # Objeto para la conexión a la base de datos
import traceback # Para obtener detalles de excepciones

# Lógica para actualizar datos de formularios (posiblemente calendarios o citas).

# Creación del Blueprint para las rutas de actualización de calendario.
actualizar_calendario_bp = Blueprint("actualizar_calendario", __name__, template_folder='templates')
# Nota: El nombre del Blueprint ha sido cambiado a actualizar_calendario_bp para seguir convenciones y evitar confusión con el nombre de la función.

@actualizar_calendario_bp.route("/actualizar_calendario", methods=["POST"]) # Ruta para la actualización, solo acepta POST.
@login_required  # Requiere que el usuario haya iniciado sesión.
@role_required(1)  # Requiere que el usuario tenga el rol 1 (administrador).
def update_calendario():
    """
    Maneja la actualización de los datos de un calendario existente en la base de datos.

    Esta función se activa mediante una solicitud POST a la ruta '/actualizar_calendario'.
    Recoge los datos enviados desde un formulario, construye una consulta SQL de actualización
    y la ejecuta. Maneja posibles errores durante el proceso y muestra mensajes flash
    al usuario indicando el resultado de la operación. Finalmente, redirige al usuario
    a la página de inicio ('index').

    Los datos esperados del formulario son:
    - id_calendario: Identificador del calendario a actualizar.
    - nombreCalendario: Nuevo nombre para el calendario.
    - id_municipio: Nuevo ID del municipio asociado.
    - procedimiento: Nuevo ID del procedimiento asociado.
    - fechaInicio: Nueva fecha de inicio del calendario.
    - fechaFin: Nueva fecha de fin del calendario.
    - horaInicio: Nueva hora de inicio.
    - horaFin: Nueva hora de fin.
    - espacioCitas: Nuevo intervalo de tiempo entre citas.
    - tiempoFuera: Nuevo tiempo de descanso o fuera de servicio.
    - inicioHoraDescanso: Nueva hora de inicio del descanso.
    - finHoraDescanso: Nueva hora de fin del descanso.

    Returns:
        Response: Una redirección a la página principal ('index') de la aplicación.
                  Se muestran mensajes flash para indicar éxito o error.
    """
    cur = None # Inicializa cur a None para asegurar que exista en el bloque finally.
    try:
        # Recoge los datos del formulario enviado por el método POST.
        id_calendario = request.form['id_calendario']
        nombre_calendario = request.form['nombreCalendario']
        id_municipio = request.form['id_municipio']
        id_procedimiento = request.form['procedimiento']
        fecha_inicio = request.form['fechaInicio']
        fecha_fin = request.form['fechaFin']
        hora_inicio = request.form['horaInicio']
        hora_fin = request.form['horaFin']
        espacio_citas = request.form['espacioCitas']
        tiempo_fuera = request.form['tiempoFuera']
        inicio_hora_descanso = request.form['inicioHoraDescanso']
        fin_hora_descanso = request.form['finHoraDescanso']

        # Construcción de la consulta SQL para actualizar el registro en la tabla 'calendarios'.
        sql = """UPDATE calendarios SET 
                nombre_calendario = %s,
                id_municipio = %s,
                id_procedimiento = %s,
                fecha_inicio = %s,
                fecha_fin = %s,
                hora_inicio = %s,
                hora_fin = %s,
                espacio_citas = %s,
                tiempo_fuera = %s,
                inicio_hora_descanso = %s,
                fin_hora_descanso = %s
                WHERE id_calendario = %s"""
        # Parámetros para la consulta SQL, en el orden correspondiente a los placeholders %s.
        params = (nombre_calendario, id_municipio, id_procedimiento, 
                  fecha_inicio, fecha_fin, hora_inicio, hora_fin, espacio_citas, tiempo_fuera,
                  inicio_hora_descanso, fin_hora_descanso, id_calendario)

        # Ejecución de la consulta SQL.
        cur = mysql.connection.cursor() # Crea un cursor para la base de datos.
        cur.execute(sql, params) # Ejecuta la consulta con los parámetros.
        mysql.connection.commit() # Confirma los cambios en la base de datos.

        # Muestra un mensaje de éxito al usuario.
        flash("Calendario actualizado exitosamente.", "success") # El segundo argumento es la categoría del mensaje.

    except ValueError as ve: # Captura errores específicos de conversión de tipo de datos.
        error_details = traceback.format_exc() # Obtiene el traceback completo para logging.
        print(f"Error de ValueError al actualizar calendario: {str(ve)}")
        print(f"Detalles del error: {error_details}")
        flash(f"Error en los datos proporcionados: {str(ve)}. Por favor, verifique los formatos.", "danger") # Mensaje de error para el usuario.
        if mysql.connection.open: # Verifica si la conexión está abierta antes de hacer rollback.
            mysql.connection.rollback()  # Revierte los cambios en caso de error.
    except Exception as e: # Captura cualquier otra excepción general.
        error_details = traceback.format_exc() # Obtiene el traceback completo.
        print(f"Error general al actualizar calendario: {str(e)}") # Imprime el error en consola/log.
        print(f"Detalles del error: {error_details}")
        flash(f"Ocurrió un error al actualizar el calendario: {str(e)}", "danger") # Mensaje genérico de error para el usuario.
        if mysql.connection.open: # Verifica si la conexión está abierta.
            mysql.connection.rollback()  # Revierte los cambios.
    finally:
        # Asegura que el cursor se cierre, si fue abierto.
        if cur:
            cur.close()

    # Redirecciona al usuario a la página principal (index).
    return redirect(url_for("index"))
