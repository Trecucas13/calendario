from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, session
from database.config import db
import traceback
from datetime import datetime
from tiempo_funcion import benchmark_guardado
from sqlalchemy import text

insertar_citas = Blueprint('insertar_citas', __name__)

@insertar_citas.route("/insertar_citas", methods=["POST"])
def insertar_cita():
    try:
        if request.method == "POST":
            id_calendario = request.form["id_calendario"]
            nombre = request.form["nombre"]
            apellido = request.form["apellido"]
            fecha = request.form["fecha_cita"]
            hora = request.form["hora_cita"]
            tipo_documento = request.form["tipo_documento"]
            numero_documento = request.form["documento"]
            telefono = request.form["telefono"]
            direccion = request.form["direccion"]
            fecha_nacimiento = request.form["fecha_nacimiento"]
            examen = request.form["examen"]
            usuario_actual = session.get('id')
        
            # print("Datos recibidos:", id_calendario, nombre, apellido, fecha, hora, tipo_documento, numero_documento, telefono, direccion, fecha_nacimiento, examen)
            # print("Usuario actual:", usuario_actual)
            paciente_existente = db.session.execute(
                text("SELECT * FROM pacientes WHERE numero_documento = :numero_documento"),
                {"numero_documento": numero_documento}
            ).mappings().fetchone()

            if paciente_existente:
                id_paciente = paciente_existente["id"]
            else:
                try:
                    db.session.execute(text("""INSERT INTO pacientes (
                        nombre,
                        apellido,
                        tipo_documento, 
                        numero_documento, 
                        telefono, 
                        direccion, 
                        fecha_nacimiento) 
                        VALUES (:nombre, :apellido, :tipo_documento, :numero_documento, :telefono, :direccion, :fecha_nacimiento)"""),
                        {"nombre": nombre, "apellido": apellido, "tipo_documento": tipo_documento, "numero_documento": numero_documento, "telefono": telefono, "direccion": direccion, "fecha_nacimiento": fecha_nacimiento})
                    db.session.commit()

                    paciente_existente = db.session.execute(
                        text("SELECT * FROM pacientes WHERE numero_documento = :numero_documento"),
                        {"numero_documento": numero_documento}
                    ).mappings().fetchone()
                    id_paciente = paciente_existente["id"]
                except Exception as e:
                    db.session.rollback()
                    print(traceback.format_exc())
                    flash(f"Error al insertar paciente: {str(e)}", "error")
                    return redirect(f'/calendario/{id_calendario}')

            db.session.execute(text("""
                INSERT INTO citas (
                    id_calendario, 
                    id_usuario,
                    id_paciente, 
                    id_procedimiento, 
                    fecha, 
                    hora,
                    estado
                ) 
                VALUES (:id_calendario, :id_usuario, :id_paciente, :id_procedimiento, :fecha, :hora, :estado)"""),
                {
                    "id_calendario": id_calendario,
                    "id_usuario": usuario_actual,
                    "id_paciente": id_paciente,
                    "id_procedimiento": examen,
                    "fecha": fecha,
                    "hora": hora,
                    "estado": True  # o False según tu lógica
                })

            db.session.commit()
            flash("Cita insertada exitosamente", "success")
            return redirect(f'/calendario/{id_calendario}')

    except Exception as e:
        db.session.rollback()
        print(traceback.format_exc())
        flash(f"Error al insertar cita: {str(e)}", "error")
        return redirect(f'/calendario/{id_calendario}')
