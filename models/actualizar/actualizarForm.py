from flask import Blueprint, render_template, request, redirect, url_for
from database.config import mysql

actualizar_calendario = Blueprint("actualizar_calendario", __name__)

@actualizar_calendario.route("/actualizar_calendario", methods=["POST"])
@login_required  
@role_required(1)  
def update_calendario():
    """
    Función que maneja la actualización de datos de un calendario en la base de datos.
    
    Esta ruta procesa el formulario de actualización de calendario, valida los datos
    y actualiza la información en la base de datos.
    
    Returns:
        Response: Redirección a la página de listado de calendario
    """
    
    try:
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
        params = (nombre_calendario, id_municipio, id_procedimiento, 
                  fecha_inicio, fecha_fin, hora_inicio, hora_fin, espacio_citas, tiempo_fuera,
                  inicio_hora_descanso, fin_hora_descanso, id_calendario)
         
        # Ejecutar la consulta SQL
        cur = mysql.connection.cursor()
        cur.execute(sql, params)
        mysql.connection.commit()
        
        # Mostrar mensaje de éxito
        flash("Calendario actualizado exitosamente", "success")
    
    except ValueError as e:
        # Capturar errores de tipo de datos
        flash(f"Error en tipos de datos: {str(e)}", "error")
        mysql.connection.rollback()  # Revertir cambios en caso de error
    except Exception as e:
        # Capturar cualquier otro error
        flash(f"Error al actualizar: {str(e)}", "error")
        mysql.connection.rollback()  # Revertir cambios en caso de error
    finally:
        # Cerrar el cursor si fue creado
        cur.close() if 'cur' in locals() else None
    
    # Redireccionar a la página de listado de clientes
    return redirect(url_for("index"))