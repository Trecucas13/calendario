from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.config import mysql # Objeto para la conexión a la base de datos.

# Lógica para insertar nuevos registros de calendario.

insercion_calendario_bp = Blueprint('insercion_calendario', __name__, template_folder='templates')
# Se renombra el Blueprint a insercion_calendario_bp para mayor claridad y consistencia.

@insercion_calendario_bp.route('/insertar_calendario', methods=['GET', 'POST'])
# Asumo que esta ruta debería estar protegida por @login_required y @role_required.
# Ejemplo:
# @login_required
# @role_required(1) # O el rol que corresponda para crear calendarios.
def insertar_calendario():
    """
    Maneja la inserción de un nuevo calendario en la base de datos.

    Este endpoint se activa mediante una solicitud POST (cuando se envía el formulario).
    Recoge los datos del calendario desde el formulario, incluyendo detalles como nombre,
    municipio, fechas, horas, y configuración de descansos.
    Inserta el nuevo registro en la tabla 'calendarios'.
    La lógica comentada para insertar citas automáticamente parece estar incompleta o
    ser experimental y no se ejecuta actualmente.

    Args:
        None (obtiene los datos del `request.form` y `session`).

    Returns:
        Response: Redirige a la página '/index' después de la inserción exitosa.
                  Muestra un mensaje flash de éxito.
                  Si el método es GET, implícitamente renderizaría una plantilla
                  (aunque la plantilla no se especifica aquí, Flask lo buscaría
                  basado en el nombre del endpoint o se definiría con render_template).
    """
    if request.method == 'POST': # Solo procesa si la solicitud es de tipo POST.
        # --- Recolección de datos del formulario ---
        nombre = request.form['nombreCalendario'] # Nombre del calendario.
        id_municipio = request.form['id_municipio'] # ID del municipio asociado.
        fecha_inicio = request.form['fechaInicio'] # Fecha de inicio del calendario.
        fecha_fin = request.form['fechaFin'] # Fecha de fin del calendario.
        id_procedimiento = request.form['procedimiento'] # ID del procedimiento asociado.
        hora_inicio = request.form['horaInicio'] # Hora de inicio de la jornada.
        hora_fin = request.form['horaFin'] # Hora de fin de la jornada.
        espacio_citas = request.form['espacioCitas'] # Duración o espacio entre citas.
        tiempo_fuera = request.form['tiempoFuera'] # Indica si hay tiempo de descanso ('si' o 'no').
        
        # Manejo del tiempo de descanso basado en la selección del usuario.
        if tiempo_fuera == "no":
            inicio_descanso = None # Si no hay tiempo fuera, los valores de descanso son nulos.
            fin_descanso = None
        else:
            # Si hay tiempo fuera, se recogen las horas de inicio y fin del descanso.
            inicio_descanso = request.form['inicioHoraDescanso']
            fin_descanso = request.form['finHoraDescanso']

        # Obtiene el ID del usuario de la sesión actual para asociarlo al calendario.
        id_usuario = session.get('id')

        conn = None # Inicializa conn para asegurar que exista en un posible bloque finally (aunque no hay uno aquí).
        try:
            conn = mysql.connection.cursor() # Crea un cursor para la base de datos.
            # --- Inserción en la tabla 'calendarios' ---
            conn.execute("""
                INSERT INTO calendarios
                (nombre_calendario, id_usuario, id_municipio, id_procedimiento, fecha_inicio, fecha_fin, hora_inicio,
                hora_fin, espacio_citas, tiempo_fuera, inicio_hora_descanso,
                fin_hora_descanso)
                VALUES (%s ,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nombre, id_usuario, id_municipio, id_procedimiento, fecha_inicio, fecha_fin, hora_inicio,
                 hora_fin, espacio_citas, tiempo_fuera, inicio_descanso, fin_descanso))
            mysql.connection.commit() # Confirma la transacción en la base de datos.

            # --- Lógica comentada para inserción de citas (experimental/incompleta) ---
            # El siguiente bloque de código está comentado en el original y parece ser un intento
            # de generar citas automáticamente al crear un calendario. Esta lógica es compleja
            # y parece incompleta (ej. variables no definidas, condiciones no claras).
            # Se mantiene comentado como en el original.

            # id_calendario = conn.lastrowid # Obtendría el ID del calendario recién insertado.


            # conn.execute("""
            #     SELECT * FROM calendarios
            # """)
            # datos_calendario = conn.fetchall()

            # conn.execute("""
            #     SELECT * FROM citas
            #     """)
            # datos = conn.fetchall()

            # if datos["fecha"] == datos_calendario[""] or fecha_fin:
            #     if datos["hora"] == hora_inicio or hora_fin:
            #         flash("Ya existe una cita en ese horario", "danger")
            #     else:
            #         conn.execute("""
            #             INSERT INTO citas
            #             (id_calendario, fecha, hora)
            #             VALUES (%s, %s, %s, %s)
            #         """, (id_calendario, fecha_inicio, hora_inicio))
            #         mysql.connection.commit()
            #         flash("Cita insertada correctamente", "success")
            # else:
            #     conn.execute("""
            #             INSERT INTO citas
            #             (id_calendario, fecha, hora)
            #             VALUES (%s, %s, %s, %s)
            #         """, (id_calendario, fecha_inicio, hora_inicio))
            #     mysql.connection.commit()
            #     flash("Cita insertada correctamente", "success")

            flash("Calendario insertado correctamente.", "success") # Mensaje de éxito.
        except Exception as e:
            # Manejo básico de excepciones.
            flash(f"Error al insertar el calendario: {str(e)}", "danger")
            if conn and mysql.connection.open:
                 mysql.connection.rollback() # Revierte en caso de error.
            print(f"Error en insertar_calendario: {e}") # Log del error.
            traceback.print_exc()
        finally:
            if conn:
                conn.close() # Cierra el cursor.
        
        return redirect(url_for('index')) # Redirige a la página de inicio. El original era redirect('/index').

    # Si el método es GET, se debería renderizar el formulario de inserción.
    # Esta parte no está explícita en el código original para el método GET,
    # pero es el comportamiento usual de un endpoint que maneja GET y POST.
    # Ejemplo: return render_template("formulario_calendario.html")
    return "Formulario para insertar calendario (GET request)" # Placeholder para la respuesta GET.
