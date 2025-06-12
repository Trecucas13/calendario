from flask import Blueprint, flash, render_template, request, redirect, url_for, session
from database.config import mysql
import traceback

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

            # Obtener tipo_id, num_id y proceso desde la tabla registro_base
            cur.execute("SELECT tipo_id, num_id, proceso FROM registro_base WHERE id = %s", (registro_id,))
            registro = cur.fetchone()

            if not registro:
                flash("No se encontró el registro en registro_base", "error")
                return redirect("/gestionar")

            # tipo_id, num_id, proceso = registro
            llave_compuesta = f"{registro['tipo_id']}-{registro['num_id']}-{registro['proceso']}"

            # Insertar en tabla gestion
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

            # Confirmar los cambios en la base de datos
            mysql.connection.commit()
            flash("Gestión insertado exitosamente", "success")

        except KeyError as e:
            # Manejar errores de campos faltantes en el formulario
            mysql.connection.rollback()  # Revertir cambios en caso de error
            flash(f"Error: Campo requerido no encontrado: {str(e)}", "error")
            print(f"Error: Campo requerido no encontrado: {str(e)}")  # Log para depuración
            print(traceback.format_exc())  # Mostrar el stack trace completo

        except ValueError as e:
            # Manejar errores de tipo de datos
            mysql.connection.rollback()  # Revertir cambios en caso de error
            flash(f"Error en tipos de datos: {str(e)}", "error")
            print(f"Error en tipos de datos: {str(e)}")  # Log para depuración
            print(traceback.format_exc())  # Mostrar el stack trace completo

        except Exception as e:
            # Manejar otros errores inesperados
            mysql.connection.rollback()  # Revertir cambios en caso de error
            flash(f"Error al insertar: {str(e)}", "error")
            print(f"Error al insertar: {str(e)}")  # Log para depuración
            print(traceback.format_exc())  # Mostrar el stack trace completo

        finally:
            # Cerrar el cursor si fue creado
            if cur:
                cur.close()

    # Redirigir al usuario a la página de usuarios
    return redirect("/gestionar")