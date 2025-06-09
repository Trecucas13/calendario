from flask import Flask, Blueprint, render_template # Flask no se usa directamente aquí.
from database.config import mysql # Objeto para la conexión a la base de datos.
from auth.decorators import login_required, role_required # Decoradores para control de acceso.
# from auth.decorators import * # La importación duplicada de decoradores es redundante.
import traceback # Para un logging de errores más detallado.

# Lógica para generar vistas relacionadas con la gestión de usuarios.

def datos_usuarios():
    """
    Obtiene todos los datos de los usuarios de la tabla `usuarios`.

    Returns:
        list: Una lista de tuplas (o diccionarios, dependiendo de la configuración del cursor por defecto)
              donde cada elemento representa un usuario.
              Retorna None en caso de error (aunque idealmente debería retornar una lista vacía o propagar la excepción).
    """
    conn = None # Inicializa conn para el bloque finally.
    try:
        conn = mysql.connection.cursor() # Crea un cursor para la base de datos.
        conn.execute("SELECT * FROM usuarios") # Ejecuta la consulta para obtener todos los usuarios.
        datos = conn.fetchall() # Recupera todas las filas.
        # print(datos) # Comentado, útil para depuración.
        return datos
    except Exception as e:
        # Manejo básico de excepciones.
        print(f"Error al obtener datos de usuarios: {e}")
        traceback.print_exc() # Imprime el traceback para un mejor diagnóstico.
        return None # Considerar retornar [] para consistencia de tipo.
    finally:
        if conn:
            conn.close() # Asegura que la conexión se cierre.
        

# Creación del Blueprint para las vistas de usuarios.
vista_usuarios_bp = Blueprint('vista_usuarios', __name__, template_folder='templates')
# Se renombra el Blueprint a vista_usuarios_bp para mayor claridad y consistencia.

@vista_usuarios_bp.route("/usuarios")
@login_required # Requiere que el usuario haya iniciado sesión.
@role_required(1) # Requiere que el usuario tenga el rol 1 (presumiblemente Administrador).
def tabla_usuarios():
    """
    Renderiza la página que muestra la tabla de usuarios.

    Obtiene los datos de todos los usuarios llamando a la función `datos_usuarios()`
    y los pasa a la plantilla 'usuarios.html' para su visualización.

    Returns:
        Response: El contenido HTML renderizado de la página de listado de usuarios.
    """
    usuarios = datos_usuarios() # Llama a la función auxiliar para obtener los datos.
    # Pasa la lista de usuarios a la plantilla.
    return render_template("usuarios.html", usuarios=usuarios)