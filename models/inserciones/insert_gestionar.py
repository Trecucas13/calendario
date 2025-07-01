from flask import Blueprint, flash, render_template, request, redirect, url_for, session
from database.config import db
from sqlalchemy import text
import traceback
from tiempo_funcion import benchmark_guardado

# Creación del Blueprint para las rutas de inserción de usuarios
insertar_gestiones = Blueprint("insertar_gestiones", __name__)

@insertar_gestiones.route("/insertar_gestiones", methods=["POST", "GET"])
def insert_gestiones():
    if request.method == "POST":
        nombre_asesor = session.get("nombre")
        try:
            # Datos del formulario
            tipificacion = request.form["tipificacion"]
            idLlamada = request.form["idLlamada"]
            comentario = request.form["comentario"]
            registro_id = request.form["registro_id"]
            motivo = request.form.get("motivo")
            
            # Debug: imprimir datos recibidos
            print("Datos recibidos:", tipificacion, idLlamada, comentario, registro_id, motivo)
            
            # Obtener datos del registro_base
            registro = db.session.execute(text("SELECT tipo_id, num_id, proceso FROM registro_base WHERE id = :registro_id"), {"registro_id": registro_id}).fetchone()

            if not registro:
                flash("No se encontró el registro en registro_base", "error")
                return redirect("/gestionar")

            llave_compuesta = f"{registro['tipo_id']}-{registro['num_id']}-{registro['proceso']}"

            if not motivo:
                db.session.execute(
                    text("""INSERT INTO gestion (
                        registro_id,
                        tipificacion,
                        id_llamada,
                        comentario,
                        usuario,
                        llave_compuesta
                    ) VALUES (:registro_id, :tipificacion, :idLlamada, :comentario, :nombre_asesor, :llave_compuesta)"""),
                    {"registro_id": registro_id, "tipificacion": tipificacion, "idLlamada": idLlamada, "comentario": comentario, "nombre_asesor": nombre_asesor, "llave_compuesta": llave_compuesta}
                )
            else:
                db.session.execute(
                    text("""INSERT INTO gestion (
                        registro_id,
                        tipificacion,
                        id_llamada,
                        comentario,
                        usuario,
                        motivo,
                        llave_compuesta
                    ) VALUES (:registro_id, :tipificacion, :idLlamada, :comentario, :nombre_asesor, :motivo, :llave_compuesta)"""),
                    {"registro_id": registro_id, "tipificacion": tipificacion, "idLlamada": idLlamada, "comentario": comentario, "nombre_asesor": nombre_asesor, "motivo": motivo, "llave_compuesta": llave_compuesta}
                )

            db.session.commit()
            print("Gestión insertada exitosamente")
            flash("Gestión insertada exitosamente", "success")
            # benchmark_guardado(lambda: cur.fetchall(), repeticiones=1000)  # Benchmarking de la inserción

        except KeyError as e:
            db.session.rollback()
            flash(f"Error: Campo requerido no encontrado: {str(e)}", "error")
            print(f"Error: Campo requerido no encontrado: {str(e)}")
            print(traceback.format_exc())
        except ValueError as e:
            db.session.rollback()
            flash(f"Error en tipos de datos: {str(e)}", "error")
            print(f"Error en tipos de datos: {str(e)}")
            print(traceback.format_exc())
        except Exception as e:
            db.session.rollback()
            flash(f"Error al insertar: {str(e)}", "error")
            print(f"Error al insertar: {str(e)}")
            print(traceback.format_exc())

    return redirect("/gestionar")