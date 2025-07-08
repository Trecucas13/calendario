from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.config import db
from sqlalchemy import text

insercion_calendario = Blueprint('insercion_calendario', __name__)

@insercion_calendario.route('/insertar_calendario', methods=['GET', 'POST'])
def insertar_calendario():
    if request.method == 'POST':
        nombre = request.form['nombreCalendario']
        id_municipio = request.form['id_municipio']
        fecha_inicio = request.form['fechaInicio']
        fecha_fin = request.form['fechaFin']
        id_procedimiento = request.form['procedimiento']
        hora_inicio = request.form['horaInicio']
        hora_fin = request.form['horaFin']
        espacio_citas = request.form['espacioCitas']
        tiempo_fuera = request.form['tiempoFuera']
        
        if tiempo_fuera == "no":
            inicio_descanso = None
            fin_descanso = None
        else:
            inicio_descanso = request.form['inicioHoraDescanso']
            fin_descanso = request.form['finHoraDescanso']
        id_usuario = session.get('id')

        db.session.execute(text("""
            INSERT INTO calendarios 
            (nombre_calendario, id_usuario, id_municipio, id_procedimiento, fecha_inicio, fecha_fin, hora_inicio, 
            hora_fin, espacio_citas, tiempo_fuera, inicio_hora_descanso, 
            fin_hora_descanso)
            VALUES (:nombre, :id_usuario, :id_municipio, :id_procedimiento, :fecha_inicio, :fecha_fin, :hora_inicio, 
             :hora_fin, :espacio_citas, :tiempo_fuera, :inicio_descanso, :fin_descanso)
        """), {
            "nombre": nombre,
            "id_usuario": id_usuario,
            "id_municipio": id_municipio,
            "id_procedimiento": id_procedimiento,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "espacio_citas": espacio_citas,
            "tiempo_fuera": tiempo_fuera,
            "inicio_descanso": inicio_descanso,
            "fin_descanso": fin_descanso
        })
        db.session.commit()

        flash("Calendario insertado correctamente", "success")
        return redirect('/index')
