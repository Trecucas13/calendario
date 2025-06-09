from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, session # Flask y render_template no se usan directamente aquí. datetime no se usa.
from database.config import mysql # Objeto para la conexión a la base de datos.
import traceback # Para un logging de errores más detallado.
# from datetime import datetime # Importado pero no usado directamente en este snippet.

# Lógica para insertar nuevas citas.

insertar_citas_bp = Blueprint('insertar_citas', __name__, template_folder='templates')
# Se renombra el Blueprint para consistencia.

@insertar_citas_bp.route("/insertar_citas", methods=["POST"])
# Asumo que esta ruta debería estar protegida por @login_required.
# Ejemplo:
# @login_required
def insertar_cita():
    """
    Maneja la inserción de una nueva cita en la base de datos.

    Este endpoint se activa mediante una solicitud POST. Recoge los datos de la cita
    y del paciente desde el formulario.
    Primero, verifica si el paciente ya existe en la base de datos usando su número de documento.
    - Si el paciente existe, utiliza su ID existente.
    - Si el paciente no existe, lo crea primero en la tabla 'pacientes'.
    Luego, inserta la nueva cita en la tabla 'citas', asociándola con el ID del paciente
    (existente o recién creado), el ID del calendario, el ID del usuario actual en sesión,
    y el ID del procedimiento (examen).

    Args:
        None (obtiene los datos del `request.form` y `session`).

    Returns:
        Response: Redirige a la página del calendario específico (`/calendario/<id_calendario>`)
                  después de la operación. Muestra mensajes flash para indicar éxito o error.
    """
    # El bloque `if request.method == "POST":` es redundante aquí porque la ruta solo acepta POST.
    # Sin embargo, se mantiene la estructura original.
    conn = None # Inicializa conn para el bloque finally.
    id_calendario = request.form.get("id_calendario") # Obtener id_calendario al inicio para usarlo en redirect de error.

    try:
        # --- Recolección de datos del formulario ---
        # id_calendario ya se obtuvo.
        nombre_paciente = request.form["nombre"]
        apellido_paciente = request.form["apellido"]
        fecha_cita = request.form["fecha_cita"]
        hora_cita = request.form["hora_cita"]
        tipo_documento_paciente = request.form["tipo_documento"]
        numero_documento_paciente = request.form["documento"]
        telefono_paciente = request.form["telefono"]
        direccion_paciente = request.form["direccion"]
        fecha_nacimiento_paciente = request.form["fecha_nacimiento"]
        id_procedimiento_examen = request.form["examen"] # ID del procedimiento o examen.

        # ID del usuario que está registrando la cita, obtenido de la sesión.
        id_usuario_actual = session.get('id')

        conn = mysql.connection.cursor(dictionary=True) # Usar dictionary=True para acceder a campos por nombre. Es obsoleto en mysqlclient > 2, usar MySQLCursorDict.

        # --- Verificación y/o creación del paciente ---
        conn.execute("SELECT id FROM pacientes WHERE numero_documento = %s", (numero_documento_paciente,))
        paciente_existente_row = conn.fetchone() # Obtiene la fila del paciente si existe.

        if paciente_existente_row:
            # Si el paciente ya existe, se usa su ID.
            id_paciente = paciente_existente_row["id"]
        else:
            # Si el paciente no existe, se inserta en la tabla 'pacientes'.
            conn.execute("""INSERT INTO pacientes (
                            nombre, apellido, tipo_documento, numero_documento,
                            telefono, direccion, fecha_nacimiento
                           ) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                           (nombre_paciente, apellido_paciente, tipo_documento_paciente,
                            numero_documento_paciente, telefono_paciente, direccion_paciente,
                            fecha_nacimiento_paciente))
            # No es necesario un commit aquí si se hará uno después de insertar la cita.
            # mysql.connection.commit() # Comentado para agrupar commits.
            id_paciente = conn.lastrowid # Obtiene el ID del paciente recién insertado.

        # --- Inserción de la cita ---
        # Nota: La columna 'estado' no estaba en la lista de VALUES en el INSERT original para paciente_existente.
        # Se asume un estado por defecto o se añade si es necesario. Aquí se omite como en el original para esa rama.
        # Para la rama de nuevo paciente, el INSERT original tenía 6 placeholders para 7 columnas. Corregido.
        sql_insert_cita = """
            INSERT INTO citas (
                id_paciente, id_usuario, id_calendario, id_procedimiento, fecha, hora, estado
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """ # Asumo un estado por defecto, ej. 'Programada'
        # El estado de la cita no se provee desde el formulario, se podría poner un valor por defecto.
        # Ejemplo: estado_cita = "Programada"
        # La consulta original para paciente_existente tenía 5 VALUES y 7 columnas, lo cual es un error.
        # La consulta original para nuevo paciente tenía 6 VALUES y 6 columnas (estado faltaba).
        # Se unifica y se asume que 'estado' debe ser provisto o tener un default en BD.
        # Aquí, para el ejemplo, se añade un placeholder para estado.
        estado_cita_default = "Programada" # Ejemplo de estado por defecto.

        conn.execute(sql_insert_cita,
                     (id_paciente, id_usuario_actual, id_calendario,
                      id_procedimiento_examen, fecha_cita, hora_cita, estado_cita_default))

        mysql.connection.commit() # Confirma la transacción (paciente nuevo si aplica, y la cita).

        flash("Cita insertada correctamente.", "success")

    except Exception as e:
        # Manejo de excepciones.
        traceback.print_exc() # Imprime el traceback completo para depuración.
        flash(f"Error al insertar la cita: {str(e)}", "danger")
        if conn and mysql.connection.open: # Verifica si la conexión está activa.
            mysql.connection.rollback() # Revierte los cambios.
    finally:
        if conn:
            conn.close() # Cierra el cursor.

    # Redirige a la página del calendario, independientemente de si hubo éxito o error manejado con flash.
    # Si id_calendario no se pudo obtener al inicio (ej. error de formulario), esta redirección podría fallar o ser incorrecta.
    if id_calendario:
        return redirect(url_for('calendario_vistas.ver_calendario', id_calendario=id_calendario)) # Asumiendo que 'calendario_vistas.ver_calendario' es la ruta correcta.
    else:
        return redirect(url_for('index')) # Redirección genérica si id_calendario no está disponible.
