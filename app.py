from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from jinja2 import Template
from database.config import db_conexion, mysql

from models.vistas.calendario import tabla_calendarios
from models.vistas.calendario import calendarios_creados
from models.vistas.calendario import datos_calendario
from models.vistas.usuarios import vista_usuarios

from models.inserciones.insert_citas import insertar_citas
from models.inserciones.insert_calendario import insercion_calendario
from models.inserciones.insert_usuario import insertar_usuario

# from models.vistas.calendario import obtener_citas
from models.eliminar.eliminar_usuario import delete_usuarios
from models.eliminar.eliminar_calendario import delete_calendario

from models.actualizar.actualizarUsuario import actualizar_usuario
from models.actualizar.actualizarForm import actualizar_calendario
# from models.vistas.citas import citas_bp

from auth.auth_login import auth
from auth.decorators import *

app = Flask(__name__)
db_conexion(app)


app.register_blueprint(tabla_calendarios)
app.register_blueprint(calendarios_creados)
app.register_blueprint(insercion_calendario)
app.register_blueprint(auth)
# app.register_blueprint(citas_bp)
app.register_blueprint(insertar_usuario)
app.register_blueprint(insertar_citas)
app.register_blueprint(vista_usuarios)

app.register_blueprint(delete_usuarios)
app.register_blueprint(delete_calendario)
app.register_blueprint(actualizar_usuario)
app.register_blueprint(actualizar_calendario)

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/index")
@login_required
@role_required([1, 2])
def index():
    calendarios = datos_calendario()
    return render_template("index.html", calendarios=calendarios)


def datos_municipio():
    conn = mysql.connection.cursor()
    conn.execute("SELECT * FROM municipios")
    municipios = conn.fetchall()

    conn.execute("SELECT * FROM procedimientos")
    procedimientos = conn.fetchall()
    conn.close()

    return {"municipios": municipios, "procedimientos": procedimientos}

def obtener_pacientes():
    conn = mysql.connection.cursor()
    conn.execute("SELECT * FROM pacientes")
    pacientes = conn.fetchall()

    return{"pacientes": pacientes}

@app.route("/formulario")
@login_required
@role_required([1, 2])
def formulario():
    datos = datos_municipio()
    # print(datos)
    return render_template("formularios/creacion_calendario.html", datos=datos)


@app.route("/actualizarCalendario/<int:id>", methods=["GET", "POST"])
@login_required
@role_required([1, 2])
def formularioActualizar(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM calendarios WHERE id_calendario = %s", (id,))
    calendario = cursor.fetchone()
    
    cursor.execute("SELECT * FROM municipios")
    municipios = cursor.fetchall()

    cursor.execute("SELECT * FROM procedimientos")
    procedimientos = cursor.fetchall()
    cursor.close()
    form_id = id
    # print(form_id)  # Agrega esta línea para imprimir el valor de form_id en el servido
    return render_template("formularios/actualizarform.html", form_id=form_id, calendario = calendario, municipios=municipios, procedimientos=procedimientos)




@app.route("/pacientes")
def pacientes():
    pacientes = obtener_pacientes()
    return render_template("pacientes.html", pacientes=pacientes)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
