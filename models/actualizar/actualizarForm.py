from flask import Blueprint, render_template, request, redirect, url_for, flash
from auth.decorators import * 
from database.config import db
from sqlalchemy import text  # <-- Agrega esta importación
import traceback

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

        sql = text("""UPDATE calendarios SET 
                nombre_calendario = :nombre_calendario,
                id_municipio = :id_municipio,
                id_procedimiento = :id_procedimiento,
                fecha_inicio = :fecha_inicio,
                fecha_fin = :fecha_fin,
                hora_inicio = :hora_inicio,
                hora_fin = :hora_fin,
                espacio_citas = :espacio_citas,
                tiempo_fuera = :tiempo_fuera,
                inicio_hora_descanso = :inicio_hora_descanso,
                fin_hora_descanso = :fin_hora_descanso
                WHERE id_calendario = :id_calendario""")
        db.session.execute(sql, {
            "nombre_calendario": nombre_calendario,
            "id_municipio": id_municipio,
            "id_procedimiento": id_procedimiento,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "espacio_citas": espacio_citas,
            "tiempo_fuera": tiempo_fuera,
            "inicio_hora_descanso": inicio_hora_descanso,
            "fin_hora_descanso": fin_hora_descanso,
            "id_calendario": id_calendario
        })
        db.session.commit()

        # Mostrar mensaje de éxito
        flash("Calendario actualizado exitosamente", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar calendario: {str(e)}", "error")
        print(traceback.format_exc())

    # Redireccionar a la página de listado de clientes
    return redirect(url_for("index"))
