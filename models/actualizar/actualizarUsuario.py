from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify # render_template no se usa aquí.
from database.config import mysql # Objeto para la conexión a la base de datos.
import traceback # Para imprimir detalles de excepciones.

# Lógica para actualizar datos de usuarios.

# Creación del Blueprint para las rutas de actualización de usuarios.
actualizar_usuario_bp = Blueprint("actualizar_usuario", __name__, template_folder='templates')
# Nota: Se renombró el Blueprint a 'actualizar_usuario_bp' para consistencia.

@actualizar_usuario_bp.route("/obtener_usuario/<int:id>", methods=["GET"])
# Asumo que esta ruta también debería estar protegida por @login_required.
# Ejemplo:
# @login_required
def obtener_usuario(id):
    """
    Obtiene los datos de un usuario específico por su ID.

    Esta función es un endpoint GET que espera el ID del usuario como parte de la URL.
    Consulta la base de datos para encontrar el usuario y devuelve sus datos
    (id, documento, nombre, rol) en formato JSON.

    Args:
        id (int): El ID del usuario a consultar, extraído de la ruta URL.

    Returns:
        Response: Un objeto JSON con los datos del usuario y código de estado 200 si se encuentra.
                  Un JSON con mensaje de error y código 404 si el usuario no se encuentra.
                  Un JSON con mensaje de error y código 500 si ocurre otra excepción.
    """
    cur = None # Inicializa cur para asegurar su existencia en el bloque finally.
    try:
        # Crea un cursor que devuelve filas como diccionarios.
        cur = mysql.connection.cursor(dictionary=True) # Usar dictionary=True es obsoleto en versiones más nuevas de mysqlclient, se usa MySQLCursorDict
        # Consulta SQL para seleccionar campos específicos del usuario por ID.
        cur.execute("""
            SELECT id, documento, nombre, rol
            FROM usuarios 
            WHERE id = %s
        """, (id,)) # El ID se pasa como tupla para la consulta parametrizada.
        usuario = cur.fetchone() # Obtiene el primer (y único esperado) resultado.
        
        if usuario: # Si se encontró el usuario.
            # Devuelve los datos del usuario en formato JSON con estado HTTP 200 (OK).
            return jsonify({
                'id': usuario['id'],
                'documento': usuario['documento'],
                'nombre': usuario['nombre'],
                'rol': usuario['rol']
            }), 200
        else: # Si no se encontró el usuario.
            # Devuelve un mensaje de error en JSON con estado HTTP 404 (Not Found).
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
    except Exception as e: # Captura cualquier excepción durante la consulta.
        # Devuelve un mensaje de error en JSON con estado HTTP 500 (Internal Server Error).
        return jsonify({'error': f"Error al obtener usuario: {str(e)}"}), 500
    finally:
        # Asegura que el cursor se cierre si fue abierto.
        if cur:
            cur.close()

@actualizar_usuario_bp.route("/actualizar_usuario", methods=["POST"])
# Asumo que esta ruta también debería estar protegida por @login_required y @role_required.
# Ejemplo:
# @login_required
# @role_required(1) # O el rol apropiado para actualizar usuarios.
def update_usuario():
    """
    Maneja la actualización de los datos de un usuario existente en la base de datos.

    Esta función se activa mediante una solicitud POST. Recoge los datos del usuario
    (documento, nombre, rol) desde el formulario y actualiza el registro correspondiente
    en la tabla 'usuarios' usando el ID del usuario.
    Importante: esta función NO actualiza la contraseña del usuario.
    Maneja errores y muestra mensajes flash al usuario. Finalmente, redirige al
    listado de usuarios.

    Datos esperados del formulario:
    - id: Identificador único del usuario a actualizar.
    - documento: Nuevo número de documento del usuario.
    - nombre: Nuevo nombre completo del usuario.
    - rol: Nuevo rol asignado al usuario.

    Returns:
        Response: Una redirección a la vista de la tabla de usuarios
                  (endpoint 'vista_usuarios.tabla_usuarios').
                  Se muestran mensajes flash para indicar éxito o error.
    """
    cur = None # Inicializa cur.
    
    try:
        # Obtención de los datos del formulario.
        id_usuario = request.form["id"]
        documento = request.form["documento"]
        nombre = request.form["nombre"]
        rol = request.form["rol"] # Asumo que el rol es un valor que se puede guardar directamente.
        
        # Creación del cursor para la base de datos.
        cur = mysql.connection.cursor() 
        
        # Consulta SQL para actualizar los datos del usuario (sin modificar la contraseña).
        sql = """UPDATE usuarios SET 
                 documento = %s,
                 nombre = %s,
                 rol = %s
                 WHERE id = %s""" # Condición para actualizar el usuario correcto.
        # Parámetros para la consulta SQL.
        params = (documento, nombre, rol, id_usuario)
        
        # Ejecución de la consulta SQL.
        cur.execute(sql, params)
        mysql.connection.commit() # Confirma los cambios.
        
        # Muestra un mensaje de éxito.
        flash("Usuario actualizado exitosamente.", "success")
    
    except Exception as e: # Captura cualquier excepción.
        flash(f"Error al actualizar el usuario: {str(e)}", "danger")
        traceback.print_exc() # Imprime el traceback para depuración.
        if mysql.connection and mysql.connection.open: # Verifica si la conexión está activa.
            mysql.connection.rollback() # Revierte los cambios en caso de error.
    finally:
        # Asegura que el cursor se cierre.
        if cur:
            cur.close()
    
    # Redirecciona a la página de listado de usuarios.
    return redirect(url_for("vista_usuarios.tabla_usuarios")) # Asume que 'vista_usuarios' es el nombre de otro Blueprint.