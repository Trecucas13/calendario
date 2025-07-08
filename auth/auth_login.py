# Importación de módulos necesarios
from flask import request, redirect, url_for, Blueprint, session, render_template, flash
from database.config import db
from sqlalchemy import text
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
        user = db.session.execute(
            text("SELECT * FROM usuarios WHERE documento = :documento AND password = :password"),
            {"documento": documento, "password": password},
        ).fetchone()

        # Si el usuario existe en la base de datos
        if user:
            # Establece las variables de sesión con la información del usuario
            session["logueado"] = True
            session["id"] = user[0]
            session["documento"] = user[1]
            session["rol"] = user[4]
            session["nombre"] = user[3]

            # Redirección según el rol y estado del usuario
            if user[4] == 1:  # Administrador
                    return redirect(url_for("index"))

            elif user[4] == 2:  # Usuario regular
                    return redirect(url_for("index"))
                    
            elif user[4] is None:
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
