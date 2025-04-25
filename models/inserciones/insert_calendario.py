from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.config import mysql

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
        inicio_descanso = request.form['inicioHoraDescanso']
        fin_descanso = request.form['finHoraDescanso']
        id_usuario = session.get('id')

        conn = mysql.connection.cursor()
        conn.execute("""
            INSERT INTO calendarios 
            (nombre_calendario, id_usuario, id_municipio, id_procedimiento, fecha_inicio, fecha_fin, hora_inicio, 
            hora_fin, espacio_citas, tiempo_fuera, inicio_hora_descanso, 
            fin_hora_descanso)
            VALUES (%s ,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre, id_usuario, id_municipio, id_procedimiento, fecha_inicio, fecha_fin, hora_inicio, 
             hora_fin, espacio_citas, tiempo_fuera, inicio_descanso, fin_descanso))
        mysql.connection.commit()

        # id_calendario = conn.lastrowid


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
        
        conn.close()
        
        flash("Calendario insertado correctamente", "success")
        return redirect(url_for('tabla_calendarios.calendario'))
