# Importación de módulos necesarios
from flask import request, redirect, url_for, Blueprint, session, render_template, flash
from database.config import mysql
from auth.decorators import *

# Creación del Blueprint para la autenticación
auth = Blueprint("auth", __name__) # Define un Blueprint para agrupar rutas de autenticación

# Docstring a nivel de módulo
"""
Este módulo maneja la lógica de autenticación de usuarios, incluyendo el inicio de sesión.
Utiliza Flask para gestionar las rutas y sesiones, y se conecta a una base de datos MySQL
para verificar las credenciales de los usuarios.
"""

@auth.route("/login", methods=["POST", "GET"])
def auth_login():
    """
    Maneja el proceso de inicio de sesión de los usuarios.

    Esta función se encarga de mostrar el formulario de inicio de sesión (método GET)
    y de procesar las credenciales enviadas por el usuario (método POST).
    Verifica las credenciales contra la base de datos y, si son válidas,
    establece una sesión para el usuario y lo redirige a la página principal
    según su rol.

    Args:
        None (aunque internamente accede a `request.form` para obtener
        'documento' y 'password' en una solicitud POST).

    Returns:
        Flask.Response: Redirige al usuario a la página de inicio (`index`)
                        si la autenticación es exitosa.
                        Renderiza nuevamente la plantilla `login.html` con un mensaje
                        de error si la autenticación falla o si es una solicitud GET.
    """
    # Verifica si se enviaron credenciales del usuario mediante POST
    if (
        request.method == "POST" # Comprueba si la solicitud es de tipo POST
        and "documento" in request.form # Verifica que el campo 'documento' esté en el formulario
        and "password" in request.form # Verifica que el campo 'password' esté en el formulario
    ):
        # Obtiene las credenciales del formulario
        documento = request.form["documento"] # Extrae el documento del formulario
        password = request.form["password"] # Extrae la contraseña del formulario

        # Consulta a la base de datos para verificar las credenciales
        cur = mysql.connection.cursor() # Crea un cursor para interactuar con la base de datos
        cur.execute(
            "SELECT * FROM usuarios WHERE documento = %s AND password = %s", # Query SQL para buscar el usuario
            (documento, password), # Parámetros para la consulta SQL
        )
        user = cur.fetchone() # Obtiene el primer resultado de la consulta

        # Código comentado para consultar acceso al sistema (se mantiene comentado)
        # cur.execute(
        #     "SELECT accesoSistema FROM empleado WHERE idEmpleado = %s",
        #     (user["idEmpleado"])
        # )
        # acceso = cur.fetchone()

        cur.close() # Cierra el cursor de la base de datos

        # Si el usuario existe en la base de datos
        if user:
            # Establece las variables de sesión con la información del usuario
            session["logueado"] = True # Indica que el usuario ha iniciado sesión
            session["id"] = user["id"] # Almacena el ID del usuario en la sesión
            session["documento"] = user["documento"] # Almacena el documento del usuario
            session["rol"] = user["rol"] # Almacena el rol del usuario
            session["nombre"] = user["nombre"] # Almacena el nombre del usuario

            # session["nombre"] = user.get("nombre", "Usuario")  # Manejo de nombre por si no existe (se mantiene comentado)
            # session["accesoSistema"] = acceso["accesoSistema"] # (se mantiene comentado)

            # Redirección según el rol y estado del usuario
            if user["rol"] == 1:  # Si el rol es Administrador
                    return redirect(url_for("index")) # Redirige a la página principal

            elif user["rol"] == 2:  # Si el rol es Usuario regular
                    return redirect(url_for("index")) # Redirige a la página principal
                    
            elif user["rol"] is None: # Si el usuario no tiene un rol asignado
                flash("Usuario no registrado") # Muestra un mensaje de error
                return redirect(url_for("auth_login.login")) # Redirige a la página de login
        else:
            # Mensaje de error si las credenciales son incorrectas
            flash("Usuario o contraseña incorrectos") # Muestra un mensaje de error
            return render_template("login.html") # Renderiza nuevamente la página de login
            
    # Si es una petición GET o no se enviaron credenciales, muestra el formulario de login
    return render_template("login.html") # Muestra el formulario de login por defecto


@auth.route("/logout")
def logout():
    """
    Cierra la sesión del usuario actualmente logueado.

    Esta función elimina todas las variables almacenadas en la sesión del usuario,
    efectivamente cerrando su sesión. Luego redirige al usuario a la página
    de inicio de sesión.

    Args:
        None

    Returns:
        Flask.Response: Redirige al usuario a la página de inicio de sesión (`auth.auth_login`).
    """
    # Elimina todas las variables de sesión
    session.clear() # Limpia todas las claves y valores de la sesión actual
    return redirect(url_for("auth.auth_login")) # Redirige a la ruta de login
