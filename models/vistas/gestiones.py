from flask import Flask, Blueprint, render_template
from database.config import mysql
from auth.decorators import *
from auth.decorators import *


#Ruta para hISTORICO DE GESTIONES
vista_gestiones = Blueprint('vista_gestiones', __name__)

@vista_gestiones.route("/Historico_gestiones")
@login_required
@role_required([1 , 2])
def tabla_gestiones():
    return render_template("historico_gestiones.html")


#Ruta para Gestion BD
gestion_bd = Blueprint('gestion_bd', __name__)

@gestion_bd.route("/gestion_bd")
@login_required
@role_required([1 , 2])
def tabla_gestiones():
    return render_template("gestion_bd.html")

#Ruta para Gestionar
gestionar = Blueprint('gestionar', __name__)

@gestionar.route("/gestionar")
@login_required
@role_required([1 , 2])
def tabla_gestiones():
    return render_template("gestionar.html")


