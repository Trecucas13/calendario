from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, session
from database.config import mysql
import traceback
from datetime import datetime


insertar_citas = Blueprint('insertar_citas', __name__)

@insertar_citas.route("/insertar_citas", methods=["POST"])
def insertar_cita():
    try:
        if request.method == "POST":
            id_calendario = request.form["id_calendario"]
            fecha = request.form["fecha_cita"]
            hora = request.form["hora_cita"]
            tipo_documento = request.form["tipo_documento"]
            numero_documento = request.form["documento"]
            telefono = request.form["telefono"]
            direccion = request.form["direccion"]
            fecha_nacimiento = request.form["fecha_nacimiento"]
            examen = request.form["examen"]
            usuario_actual = session.get('id')

            conn = mysql.connection.cursor()
            conn.execute("""INSERT INTO pacientes (
            tipo_documento, 
            numero_documento, 
            telefono, 
            direccion, 
            fecha_nacimiento, 
            examen_realizar) 
            VALUES (%s, %s, %s, %s, %s, %s)""", 
            (tipo_documento, numero_documento, telefono, direccion, fecha_nacimiento, examen))
            mysql.connection.commit()

            id_paciente = conn.lastrowid

            conn.execute("""
                INSERT INTO citas (
                id_paciente, 
                id_usuario,
                id_calendario, 
                fecha, 
                hora)
                VALUES (%s, %s, %s, %s, %s)""",
                (id_paciente, usuario_actual, id_calendario, fecha, hora))

            # flash("Cita insertada correctamente", "success")
            mysql.connection.commit()
            conn.close()

            flash("Cita insertada correctamente", "success")
            return redirect(f'/calendario/{id_calendario}')

    except Exception as e:
        traceback.print_exc()
        flash("Error al insertar la cita: " + str(e), "error")
        return redirect(f'/calendario/{id_calendario}')
