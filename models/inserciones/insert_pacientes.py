from flask import Blueprint, flash, render_template, request, redirect, url_for
from database.config import db
from sqlalchemy import text
import traceback

# Creación del Blueprint para las rutas de inserción de usuarios
insertar_pacientes = Blueprint("insertar_pacientes", __name__)

@insertar_pacientes.route("/insertar_pacientes", methods=["POST", "GET"])
def insert_pacientes():
    """
    Función que maneja la inserción de nuevos pacientes.
    Recibe los datos del formulario y guarda el pacientes en la base de datos.
    """
    # Solo procesar si es una solicitud POST
    if request.method == "POST":
        try:
            # Obtener datos del formulario - corregido para usar 'nombre' en lugar de 'nombreCompleto'
            nombre = request.form["nombre"]
            apellido = request.form["apellido"]
            tipo_documento = request.form["tipo_documento"]
            numero_documento = request.form["numero_documento"]
            telefono = request.form["telefono"]
            direccion = request.form["direccion"]
            fecha_nacimiento = request.form["fecha_nacimiento"]
           
            print("Datos recibidos: ", request.form)

            # Insertar el nuevo usuario en la base de datos
            db.session.execute(
                text("""INSERT INTO pacientes(
                    nombre,
                    apellido,
                    tipo_documento,
                    numero_documento,
                    telefono,
                    direccion,
                    fecha_nacimiento
                    )
                    VALUES (:nombre, :apellido, :tipo_documento, :numero_documento, :telefono, :direccion, :fecha_nacimiento)
                """),
                {
                    "nombre": nombre,
                    "apellido": apellido,
                    "tipo_documento": tipo_documento,
                    "numero_documento": numero_documento,
                    "telefono": telefono,
                    "direccion": direccion,
                    "fecha_nacimiento": fecha_nacimiento
                },
            )

            db.session.commit()
            flash("Paciente insertado exitosamente", "success")

        except KeyError as e:
            db.session.rollback()  # Revertir cambios en caso de error
            flash(f"Error: Campo requerido no encontrado: {str(e)}", "error")
            print(f"Error: Campo requerido no encontrado: {str(e)}")  # Log para depuración
            print(traceback.format_exc())  # Mostrar el stack trace completo

        except ValueError as e:
            db.session.rollback()  # Revertir cambios en caso de error
            flash(f"Error en tipos de datos: {str(e)}", "error")
            print(f"Error en tipos de datos: {str(e)}")  # Log para depuración
            print(traceback.format_exc())  # Mostrar el stack trace completo

        except Exception as e:
            db.session.rollback()  # Revertir cambios en caso de error
            flash(f"Error al insertar: {str(e)}", "error")
            print(f"Error al insertar: {str(e)}")  # Log para depuración
            print(traceback.format_exc())  # Mostrar el stack trace completo

    # Redirigir al usuario a la página de usuarios
    return redirect("/pacientes")