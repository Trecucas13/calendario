from flask import Flask, Blueprint, render_template
from database.config import mysql
from auth.decorators import *

def datos_usuarios():
    try:
        conn = mysql.connection.cursor()
        conn.execute("SELECT * FROM usuarios")
        datos = conn.fetchall()

        # print(datos)
        conn.close()
        return datos
    except Exception as e:
        print(f"Error: {e}")
        

vista_usuarios = Blueprint('vista_usuarios', __name__)

@vista_usuarios.route("/usuarios")
@login_required
@role_required(1)
def tabla_usuarios():
    usuarios = datos_usuarios()
    return render_template("usuarios.html", usuarios=usuarios)

    