# Archivo principal de la aplicación Flask (frontend).

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
# from jinja2 import Template # Template no se usa directamente.
from database.config import db_conexion, mysql # Para la configuración de la BD y el objeto mysql.
from espacios import espacios_api # Blueprint para la API de espacios.

# --- Importación de Blueprints de Vistas ---
from models.vistas.calendario import vista_calendario_bp as tabla_calendarios # Renombrado en origen
from models.vistas.calendario import calendarios_creados_bp as calendarios_creados # Renombrado en origen
from models.vistas.calendario import datos_calendario, csv_calendario_bp as csv_calendario # Renombrado en origen
from models.vistas.usuarios import vista_usuarios_bp as vista_usuarios # Renombrado en origen
from models.vistas.gestiones import vista_gestiones_bp as vista_gestiones # Renombrado en origen
from models.vistas.gestiones import gestion_bd_bp as gestion_bd # Renombrado en origen
from models.vistas.gestiones import gestionar_bp as gestionar # Renombrado en origen

# --- Importación de Blueprints de Inserciones ---
from models.inserciones.insert_citas import insertar_citas_bp as insertar_citas # Renombrado en origen
from models.inserciones.insert_calendario import insercion_calendario_bp as insercion_calendario # Renombrado en origen
from models.inserciones.insert_usuario import insertar_usuario_bp as insertar_usuario # Renombrado en origen
from models.inserciones.insert_pacientes import insertar_pacientes_bp as insertar_pacientes # Renombrado en origen
from models.inserciones.insert_gestionar import insertar_gestiones_bp as insertar_gestiones # Renombrado en origen

# --- Importación de Blueprints de Eliminaciones ---
from models.eliminar.eliminar_usuario import delete_usuarios_bp as delete_usuarios # Renombrado en origen
from models.eliminar.eliminar_calendario import delete_calendario_bp as delete_calendario # Renombrado en origen

# --- Importación de Blueprints de Actualizaciones ---
from models.actualizar.actualizarUsuario import actualizar_usuario_bp as actualizar_usuario # Renombrado en origen
from models.actualizar.actualizarForm import actualizar_calendario_bp as actualizar_calendario # Renombrado en origen
from models.actualizar.actualizarPacientes import actualizar_pacientes_bp as actualizar_pacientes # Renombrado en origen

# --- Importación de Autenticación y Decoradores ---
from auth.auth_login import auth # Blueprint para autenticación.
from auth.decorators import login_required, role_required # Decoradores.
# from auth.decorators import * # Segunda importación redundante.

# --- Inicialización de la Aplicación Flask ---
app = Flask(__name__) # Creación de la instancia de la aplicación Flask.

# --- Configuración de la Base de Datos ---
db_conexion(app) # Llama a la función de `database.config` para configurar la conexión a la BD.

# --- Registro de Blueprints ---
# Un Blueprint es un conjunto de rutas y vistas que pueden ser registradas en la aplicación.
# Esto ayuda a organizar la aplicación en componentes modulares.

# Blueprints de funcionalidades generales y vistas principales
app.register_blueprint(espacios_api) # API relacionada con 'espacios'.
app.register_blueprint(tabla_calendarios) # Vista de tabla de calendarios.
app.register_blueprint(csv_calendario) # Funcionalidad para exportar calendarios a CSV.
app.register_blueprint(calendarios_creados) # Vista de calendarios creados.
app.register_blueprint(auth) # Rutas de autenticación (login, logout).
app.register_blueprint(vista_usuarios) # Vista para la gestión de usuarios.

# Blueprints para vistas de gestiones
app.register_blueprint(vista_gestiones) # Histórico de gestiones.
app.register_blueprint(gestion_bd) # Vista "Gestión BD".
app.register_blueprint(gestionar) # Vista principal de "Gestionar".

# Blueprints para operaciones de inserción
app.register_blueprint(insercion_calendario) # Para insertar calendarios.
app.register_blueprint(insertar_usuario) # Para insertar usuarios.
app.register_blueprint(insertar_citas) # Para insertar citas.
app.register_blueprint(insertar_pacientes) # Para insertar pacientes.
app.register_blueprint(insertar_gestiones) # Para insertar gestiones/interacciones.

# Blueprints para operaciones de eliminación
app.register_blueprint(delete_usuarios) # Para eliminar usuarios.
app.register_blueprint(delete_calendario) # Para eliminar calendarios.

# Blueprints para operaciones de actualización
app.register_blueprint(actualizar_usuario) # Para actualizar usuarios.
app.register_blueprint(actualizar_calendario) # Para actualizar calendarios (formularios).
app.register_blueprint(actualizar_pacientes) # Para actualizar pacientes.

# Comentarios de Blueprints no usados o por revisar:
# app.register_blueprint(citas_bp) # Estaba comentado.
# app.register_blueprint(datos_citas) # Estaba comentado, y 'datos_citas' no parece ser un Blueprint.


# --- Rutas Definidas Directamente en app.py ---

@app.route("/")
def login():
    """
    Ruta raíz de la aplicación. Renderiza la página de inicio de sesión.

    Returns:
        Response: El contenido HTML de la página 'login.html'.
    """
    return render_template("login.html")


@app.route("/index")
@login_required # Requiere que el usuario esté logueado.
@role_required([1, 2]) # Permite acceso a usuarios con rol 1 (Admin) o 2 (Usuario normal).
def index():
    """
    Ruta para la página principal o dashboard después del login.

    Obtiene los datos de los calendarios y los pasa a la plantilla 'index.html'.

    Returns:
        Response: El contenido HTML de la página 'index.html' con los datos de calendarios.
    """
    calendarios = datos_calendario() # Llama a la función de `models.vistas.calendario`.
    return render_template("index.html", calendarios=calendarios)


def datos_municipio():
    """
    Función auxiliar para obtener la lista de municipios y procedimientos.

    Realiza consultas directas a la base de datos para obtener estos listados.
    Esta función es llamada por la ruta `/formulario`.

    Returns:
        dict: Un diccionario conteniendo dos claves: 'municipios' y 'procedimientos',
              cada una con una lista de resultados de la base de datos.
              Retorna None implícitamente si hay un error antes de cerrar la conexión (aunque no hay manejo de errores explícito).
    """
    conn = None # Inicializa conn para el bloque finally.
    try:
        conn = mysql.connection.cursor(dictionary=True) # Usar DictCursor para resultados como diccionarios.
        conn.execute("SELECT * FROM municipios")
        municipios = conn.fetchall()

        conn.execute("SELECT * FROM procedimientos")
        procedimientos = conn.fetchall()

        return {"municipios": municipios, "procedimientos": procedimientos}
    except Exception as e:
        print(f"Error en datos_municipio: {e}")
        traceback.print_exc()
        return {"municipios": [], "procedimientos": []} # Devolver listas vacías en caso de error.
    finally:
        if conn:
            conn.close()


@app.route("/formulario")
@login_required
@role_required([1, 2])
def formulario():
    """
    Ruta para mostrar el formulario de creación de calendarios.

    Obtiene la lista de municipios y procedimientos usando `datos_municipio()`
    y los pasa a la plantilla 'formularios/creacion_calendario.html'.

    Returns:
        Response: El contenido HTML del formulario de creación de calendarios.
    """
    datos = datos_municipio() # Obtiene datos para poblar selectores en el formulario.
    # print(datos) # Para depuración.
    return render_template("formularios/creacion_calendario.html", datos=datos)


@app.route("/actualizarCalendario/<int:id>", methods=["GET"]) # Asumo que POST se maneja en el Blueprint 'actualizar_calendario_bp'
@login_required
@role_required([1, 2])
def formularioActualizar(id):
    """
    Ruta para mostrar el formulario de actualización de un calendario específico.

    Obtiene los datos del calendario con el ID proporcionado, así como las listas
    de municipios y procedimientos. Pasa estos datos a la plantilla
    'formularios/actualizarform.html'.

    Args:
        id (int): El ID del calendario a actualizar, obtenido de la URL.

    Returns:
        Response: El contenido HTML del formulario de actualización de calendarios.
                  Puede devolver None implícitamente si hay un error de BD y no se maneja.
    """
    cursor = None # Inicializa cursor.
    try:
        cursor = mysql.connection.cursor(dictionary=True) # Usar DictCursor.
        # Obtiene los datos del calendario específico.
        cursor.execute("SELECT * FROM calendarios WHERE id_calendario = %s", (id,))
        calendario = cursor.fetchone()

        if not calendario:
            flash(f"Calendario con ID {id} no encontrado.", "warning")
            return redirect(url_for("index")) # O a donde sea apropiado.

        # Obtiene listas para los selectores del formulario.
        cursor.execute("SELECT * FROM municipios")
        municipios = cursor.fetchall()

        cursor.execute("SELECT * FROM procedimientos")
        procedimientos = cursor.fetchall()

        form_id = id # Pasa el ID al formulario, podría ser útil.
        # print(form_id)
        return render_template("formularios/actualizarform.html",
                               form_id=form_id, calendario=calendario,
                               municipios=municipios, procedimientos=procedimientos)
    except Exception as e:
        print(f"Error en formularioActualizar (ID: {id}): {e}")
        traceback.print_exc()
        flash("Error al cargar el formulario de actualización.", "danger")
        return redirect(url_for("index"))
    finally:
        if cursor:
            cursor.close()


def obtener_pacientes():
    """
    Función auxiliar para obtener la lista de todos los pacientes y algunos detalles de sus citas.

    Realiza un LEFT JOIN con `citas` y `procedimientos`.
    Esta función es llamada por la ruta `/pacientes`.

    Returns:
        list: Una lista de diccionarios (si el cursor por defecto es DictCursor) o tuplas,
              representando los pacientes y datos de citas.
              Retorna None implícitamente si hay un error.
    """
    conn = None
    try:
        conn = mysql.connection.cursor(dictionary=True) # Usar DictCursor.
        # La consulta obtiene todos los pacientes y, si tienen citas, algunos datos de ellas.
        conn.execute("""SELECT p.*, c.fecha AS fecha_cita, c.hora AS hora_cita,
                        c.id AS id_cita, c.id_calendario, c.id_procedimiento,
                        pr.nombre AS nombre_procedimiento
                        FROM pacientes p
                        LEFT JOIN citas c ON p.id = c.id_paciente
                        LEFT JOIN procedimientos pr ON c.id_procedimiento = pr.id_procedimiento
                     """)
        pacientes = conn.fetchall()
        return pacientes
    except Exception as e:
        print(f"Error en obtener_pacientes: {e}")
        traceback.print_exc()
        return [] # Devolver lista vacía en caso de error.
    finally:
        if conn:
            conn.close()

@app.route("/pacientes")
# @login_required # Debería estar protegido si muestra información sensible.
# @role_required([1, 2])
def pacientes():
    """
    Ruta para mostrar la lista de pacientes.

    Obtiene los datos de los pacientes usando `obtener_pacientes()` y los pasa
    a la plantilla 'pacientes.html'.

    Returns:
        Response: El contenido HTML de la página de listado de pacientes.
    """
    lista_pacientes = obtener_pacientes() # Llama a la función auxiliar.
    return render_template("pacientes.html", pacientes=lista_pacientes)


# La función obtener_procedimiento() es idéntica a la de models/vistas/calendario.py
# Se podría centralizar para evitar duplicación.
def obtener_procedimiento():
    """
    Función auxiliar para obtener todos los procedimientos.
    (Duplicada de `models.vistas.calendario.py`)

    Returns:
        list: Lista de procedimientos. Retorna None implícitamente en caso de error.
    """
    conn = None
    try:
        conn = mysql.connection.cursor(dictionary=True) # Usar DictCursor.
        conn.execute("SELECT * FROM procedimientos")
        procedimiento = conn.fetchall()
        return procedimiento
    except Exception as e:
        print(f"Error en obtener_procedimiento (app.py): {e}")
        traceback.print_exc()
        return []
    finally:
        if conn:
            conn.close()

# Las siguientes rutas (/insertar-municipio, /insertar-procedimiento) realizan inserciones directas.
# Sería más estructurado mover esta lógica a sus propios Blueprints o módulos CRUD.
@app.route("/insertar-municipio", methods=["POST"])
# @login_required # Debería estar protegido.
# @role_required(1) # Solo Admin debería poder insertar municipios.
def insertar_municipio():
    """
    Ruta para insertar un nuevo municipio directamente desde un formulario.
    (Considerar mover a un Blueprint de administración).
    """
    # El if request.method == "POST": es redundante ya que la ruta solo acepta POST.
    conn = None
    try:
        nombre = request.form["nombre"] # Nombre del nuevo municipio.
        # print(nombre) # Para depuración.
        conn = mysql.connection.cursor()
        conn.execute("INSERT INTO municipios (nombre) VALUES (%s)", (nombre,))
        mysql.connection.commit()
        flash("Municipio agregado correctamente.", "success")
    except Exception as e:
        if conn and mysql.connection.open: mysql.connection.rollback()
        flash(f"Error al agregar municipio: {str(e)}", "danger")
        traceback.print_exc()
    finally:
        if conn: conn.close()
    return redirect(url_for('index')) # El original era redirect('/index').

@app.route("/insertar-procedimiento", methods=["POST"])
# @login_required
# @role_required(1)
def insertar_procedimiento():
    """
    Ruta para insertar un nuevo procedimiento directamente desde un formulario.
    (Considerar mover a un Blueprint de administración).
    """
    conn = None
    try:
        nombre = request.form["nombre"] # Nombre del nuevo procedimiento.
        # print(nombre) # Para depuración.
        conn = mysql.connection.cursor()
        conn.execute("INSERT INTO procedimientos (nombre) VALUES (%s)", (nombre,))
        mysql.connection.commit()
        flash("Procedimiento agregado correctamente.", "success")
    except Exception as e:
        if conn and mysql.connection.open: mysql.connection.rollback()
        flash(f"Error al agregar procedimiento: {str(e)}", "danger")
        traceback.print_exc()
    finally:
        if conn: conn.close()
    return redirect(url_for('index')) # El original era redirect('/index').

# --- Bloque de Ejecución Principal ---
if __name__ == "__main__":
    """
    Punto de entrada para ejecutar la aplicación Flask directamente.

    Esto es útil para el desarrollo. `app.run()` inicia el servidor de desarrollo de Flask.
    - `debug=True`: Activa el modo de depuración, que recarga la aplicación
      automáticamente con los cambios y proporciona un depurador en el navegador en caso de error.
      ¡No usar en producción!
    - `host="0.0.0.0"`: Hace que el servidor sea accesible desde cualquier dirección IP,
      no solo localhost. Útil para pruebas en red local o en contenedores.
    """
    app.run(debug=True, host="0.0.0.0")
