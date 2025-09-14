# Importación de módulos necesarios
from flask import request, redirect, url_for, Blueprint, session, render_template, flash
from database.config import mysql
from auth.decorators import *

# Creación del Blueprint para la autenticación
auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["POST", "GET"])
def auth_login():
    """
    Maneja el proceso de inicio de sesión de usuarios.
    
    Métodos:
        GET: Muestra el formulario de login
        POST: Procesa las credenciales enviadas y autentica al usuario
    
    Retorna:
        - Redirección a la página correspondiente según el rol si la autenticación es exitosa
        - Renderiza la página de login con mensajes de error si la autenticación falla
    """
    # Verifica si se enviaron credenciales del usuario mediante POST
    if (
        request.method == "POST"
        and "documento" in request.form
        and "password" in request.form
    ):
        # Obtiene las credenciales del formulario
        documento = request.form["documento"]
        password = request.form["password"]

        # Consulta a la base de datos para verificar las credenciales
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM usuarios WHERE documento = %s AND password = %s",
            (documento, password),
        )
        user = cur.fetchone()

        # Código comentado para consultar acceso al sistema
        # cur.execute(
        #     "SELECT accesoSistema FROM empleado WHERE idEmpleado = %s",
        #     (user["idEmpleado"])
        # )
        # acceso = cur.fetchone()

        cur.close()

        # Si el usuario existe en la base de datos
        if user:
            # Establece las variables de sesión con la información del usuario
            session["logueado"] = True
            session["id"] = user["id"]
            session["documento"] = user["documento"]
            session["rol"] = user["rol"]
            session["nombre"] = user["nombre"]

            # session["nombre"] = user.get("nombre", "Usuario")  # Manejo de nombre por si no existe
            # session["accesoSistema"] = acceso["accesoSistema"]

            # Redirección según el rol y estado del usuario
            if user["rol"] == 1:  # Administrador
                    return redirect(url_for("index"))

            elif user["rol"] == 2:  # Usuario regular
                    return redirect(url_for("index"))
                    
            elif user["rol"] is None:
                flash("Usuario no registrado")
                return redirect(url_for("auth_login.login"))
        else:
            # Mensaje de error si las credenciales son incorrectas
            flash("Usuario o contraseña incorrectos")
            return render_template("login.html")
            
    # Si es una petición GET o no se enviaron credenciales, muestra el formulario de login
    return render_template("login.html")


@auth.route("/logout")
def logout():
    """
    Cierra la sesión del usuario actual.
    
    Retorna:
        Redirección a la página de login
    """
    # Elimina todas las variables de sesión
    session.clear()
    return redirect(url_for("auth.auth_login"))
