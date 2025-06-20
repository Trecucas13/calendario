from flask import Blueprint, flash, render_template, request, redirect, url_for, session
from database.config import mysql
import traceback
from tiempo_funcion import benchmark_guardado

# Creación del Blueprint para las rutas de inserción de usuarios
insertar_gestiones = Blueprint("insertar_gestiones", __name__)

@insertar_gestiones.route("/insertar_gestiones", methods=["POST", "GET"])
def insert_gestiones():
    if request.method == "POST":
        nombre_asesor = session.get("nombre")
        cur = mysql.connection.cursor()
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
            cur.execute("SELECT tipo_id, num_id, proceso FROM registro_base WHERE id = %s", (registro_id,))
            registro = cur.fetchone()

            if not registro:
                flash("No se encontró el registro en registro_base", "error")
                return redirect("/gestionar")

            llave_compuesta = f"{registro['tipo_id']}-{registro['num_id']}-{registro['proceso']}"

            if not motivo:
                cur.execute(
                    """INSERT INTO gestion (
                        registro_id,
                        tipificacion,
                        id_llamada,
                        comentario,
                        usuario,
                        llave_compuesta
                    ) VALUES (%s, %s, %s, %s, %s, %s)""",
                    (registro_id, tipificacion, idLlamada, comentario, nombre_asesor, llave_compuesta)
                )
            else:
                cur.execute(
                    """INSERT INTO gestion (
                        registro_id,
                        tipificacion,
                        id_llamada,
                        comentario,
                        usuario,
                        motivo,
                        llave_compuesta
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (registro_id, tipificacion, idLlamada, comentario, nombre_asesor, motivo, llave_compuesta)
                )

            mysql.connection.commit()
            print("Gestión insertada exitosamente")
            flash("Gestión insertada exitosamente", "success")
            # benchmark_guardado(lambda: cur.fetchall(), repeticiones=1000)  # Benchmarking de la inserción

        except KeyError as e:
            mysql.connection.rollback()
            flash(f"Error: Campo requerido no encontrado: {str(e)}", "error")
            print(f"Error: Campo requerido no encontrado: {str(e)}")
            print(traceback.format_exc())
        except ValueError as e:
            mysql.connection.rollback()
            flash(f"Error en tipos de datos: {str(e)}", "error")
            print(f"Error en tipos de datos: {str(e)}")
            print(traceback.format_exc())
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al insertar: {str(e)}", "error")
            print(f"Error al insertar: {str(e)}")
            print(traceback.format_exc())
        finally:
            if cur:
                cur.close()

    return redirect("/gestionar")