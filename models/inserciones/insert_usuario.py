from flask import Blueprint, flash, render_template, request, redirect, url_for
from database.config import mysql
import traceback

# Creación del Blueprint para las rutas de inserción de usuarios
insertar_usuario = Blueprint("insertar_usuario", __name__)

@insertar_usuario.route("/insertar_usuario", methods=["POST", "GET"])
def insert_usuario():
    """
    Función que maneja la inserción de nuevos usuarios.
    Recibe los datos del formulario y guarda el usuario en la base de datos.
    """
    # Solo procesar si es una solicitud POST
    if request.method == "POST":
        # Inicializar el cursor para la conexión a la base de datos
        cur = mysql.connection.cursor()
        
        try:
            # Obtener datos del formulario - corregido para usar 'nombre' en lugar de 'nombreCompleto'
            nombre = request.form["nombre"]
            documento = request.form["documento"]
            rol = request.form["rol"]
            
            # Contraseña predeterminada para todos los usuarios
            password = "saviaSalud*2025_"
           
            print("Datos recibidos: ", request.form)

            # Insertar el nuevo usuario en la base de datos
            cur.execute(
                """INSERT INTO usuarios(
                    nombre,
                    documento,
                    password,
                    rol
                    )
                    VALUES (%s, %s, %s, %s)
                """,
                (
                    nombre,
                    documento,
                    password,
                    rol,
                ), 
            )

            # Confirmar los cambios en la base de datos
            mysql.connection.commit()
            flash("Usuario insertado exitosamente", "success")

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
    return redirect(url_for("vista_usuarios.tabla_usuarios"))