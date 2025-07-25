from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from jinja2 import Template
from database.config import db_conexion, db  # Cambia mysql por db
from sqlalchemy import text
from espacios import espacios_api
from models.vistas.calendario import tabla_calendarios
from models.vistas.calendario import calendarios_creados
from models.vistas.calendario import datos_calendario, csv_calendario
from models.vistas.usuarios import vista_usuarios
from models.vistas.gestiones import vista_gestiones
from models.vistas.gestiones import gestion_bd
from models.vistas.gestiones import gestionar
import math  # Necesario para math.ceil

# from models.vistas.index import datos_citas
from tiempo_funcion import benchmark_guardado  # Importa la función de benchmarking

from models.inserciones.insert_citas import insertar_citas
from models.inserciones.insert_calendario import insercion_calendario
from models.inserciones.insert_usuario import insertar_usuario
from models.inserciones.insert_pacientes import insertar_pacientes
from models.inserciones.insert_gestionar import insertar_gestiones
from models.inserciones.carga_gestion_bd import gestion_bp as carga_gestion
# from models.vistas.calendario import obtener_citas
from models.eliminar.eliminar_usuario import delete_usuarios
from models.eliminar.eliminar_calendario import delete_calendario
from models.eliminar.eliminar_municipio import delete_municipios
from models.eliminar.eliminar_procedimiento import delete_procedimientos

from models.actualizar.actualizarUsuario import actualizar_usuario
from models.actualizar.actualizarForm import actualizar_calendario
from models.actualizar.actualizarPacientes import actualizar_pacientes
# from models.vistas.citas import citas_bp

from models.vistas.descargas import datos_citas
from models.vistas.descarga_gestionados import datos_gestionados

from auth.auth_login import auth
from auth.decorators import login_required, role_required

app = Flask(__name__)
db_conexion(app)

app.register_blueprint(espacios_api)
app.register_blueprint(tabla_calendarios)
app.register_blueprint(csv_calendario)

app.register_blueprint(calendarios_creados)
app.register_blueprint(insercion_calendario)
app.register_blueprint(auth)
# app.register_blueprint(citas_bp)
app.register_blueprint(insertar_usuario)
app.register_blueprint(insertar_citas)
app.register_blueprint(insertar_pacientes)
app.register_blueprint(insertar_gestiones)
app.register_blueprint(carga_gestion)

app.register_blueprint(vista_usuarios)
app.register_blueprint(vista_gestiones)
app.register_blueprint(gestion_bd)
app.register_blueprint(gestionar)
# app.register_blueprint(datos_citas)


app.register_blueprint(delete_usuarios)
app.register_blueprint(delete_calendario)
app.register_blueprint(delete_municipios)
app.register_blueprint(delete_procedimientos)
app.register_blueprint(actualizar_usuario)
app.register_blueprint(actualizar_calendario)
app.register_blueprint(actualizar_pacientes)

app.register_blueprint(datos_gestionados)
app.register_blueprint(datos_citas)
@app.route("/")
def login():
    return render_template("login.html")


@app.route("/index")
@login_required
@role_required([1, 2])
def index():
    calendarios = datos_calendario()
    # benchmark_guardado(lambda: gestion_bd, repeticiones=1)  # Ejecuta el benchmark para la función gestion_bd
    # Obtener municipios y procedimientos para los modales
    datos = datos_municipio()
    municipios = datos.get('municipios', [])
    procedimientos = datos.get('procedimientos', [])
    return render_template(
        "index.html",
        calendarios=calendarios,
        municipios=municipios,
        procedimientos=procedimientos
    )


def datos_municipio():
    municipios = db.session.execute(text("SELECT * FROM municipios")).fetchall()
    procedimientos = db.session.execute(text("SELECT * FROM procedimientos")).fetchall()
    return {"municipios": municipios, "procedimientos": procedimientos}



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
    calendario = db.session.execute(
        text("SELECT * FROM calendarios WHERE id_calendario = :id"), {"id": id}
    ).fetchone()
    municipios = db.session.execute(text("SELECT * FROM municipios")).fetchall()
    procedimientos = db.session.execute(text("SELECT * FROM procedimientos")).fetchall()
    form_id = id
    # print(form_id)  # Agrega esta línea para imprimir el valor de form_id en el servido
    return render_template(
        "formularios/actualizarform.html",
        form_id=form_id,
        calendario=calendario,
        municipios=municipios,
        procedimientos=procedimientos,
    )

# Clase de Paginación (asegúrate de que esté definida antes de usarla)
class Pagination:
    def __init__(self, page, per_page, total):
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = math.ceil(total / per_page)
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_num = page - 1 if self.has_prev else None
        self.next_num = page + 1 if self.has_next else None
    
    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
                (num > self.page - left_current - 1 and num < self.page + right_current) or \
                num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num



def obtener_pacientes():
    pacientes = db.session.execute(text("""
        SELECT p.*, p.id as id_paciente , c.fecha, c.hora, c.id, c.id_calendario, c.id_procedimiento, 
        pr.nombre AS nombre_procedimiento
        FROM pacientes p 
        LEFT JOIN citas c ON p.id = c.id_paciente
        LEFT JOIN procedimientos pr ON c.id_procedimiento = pr.id_procedimiento
    """)).fetchall()
    return pacientes

def procedimientos():
    procedimientos = db.session.execute(text("SELECT * FROM procedimientos")).fetchall()
    return procedimientos

@app.route("/pacientes")
def pacientes():
    pacientes = obtener_pacientes()
    print(pacientes)
    procedimientos_list = procedimientos()
    # Paginación
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total = len(pacientes)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_historial = pacientes[start:end]
    pagination = Pagination(page, per_page, total)
    return render_template("pacientes.html", 
                    pacientes=paginated_historial, pagination=pagination,
                    procedimientos=procedimientos_list)



# PROCEDIMIENTO
def obtener_procedimiento():
    conn = mysql.connection.cursor()
    conn.execute("SELECT * FROM procedimientos")
    procedimiento = conn.fetchall()

    return procedimiento

@app.route("/insertar-municipio", methods=["POST"])
def insertar_municipio():
    if request.method == "POST":
        nombre = request.form["nombre"]
        db.session.execute(text("INSERT INTO municipios (nombre) VALUES (:nombre)"), {"nombre": nombre})
        db.session.commit()
        flash("Municipio agregado correctamente", "success")
        return redirect('/index')

@app.route("/insertar-procedimiento", methods=["POST"])
def insertar_procedimiento():
    if request.method == "POST":
        nombre = request.form["nombre"]
        db.session.execute(text("INSERT INTO procedimientos (nombre) VALUES (:nombre)"), {"nombre": nombre})
        db.session.commit()
        flash("Procedimiento agregado correctamente", "success")
        return redirect('/index')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
