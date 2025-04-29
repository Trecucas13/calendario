from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify
from database.config import mysql
import traceback

# Creación del Blueprint para actualizar usuarios
actualizar_usuario = Blueprint("actualizar_usuario", __name__)

@actualizar_usuario.route("/obtener_usuario/<int:id>", methods=["GET"])
def obtener_usuario(id):
    """
    Función que obtiene los datos de un usuario específico por su ID.
    
    Args:
        id (int): ID del usuario a consultar
        
    Returns:
        Response: Datos del usuario en formato JSON
    """
    cur = None
    try:
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute("""
            SELECT id, documento, nombre, rol
            FROM usuarios 
            WHERE id = %s
        """, (id,))
        usuario = cur.fetchone()
        
        if usuario:
            return jsonify({
                'id': usuario['id'],
                'documento': usuario['documento'],
                'nombre': usuario['nombre'],
                'rol': usuario['rol']
            }), 200
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()

@actualizar_usuario.route("/actualizar_usuario", methods=["POST"])
def update_usuario():
    """
    Función que maneja la actualización de datos de un usuario en la base de datos.
    No actualiza la contraseña.
    """
    cur = None
    
    try:
        # Obtener datos del formulario
        id_usuario = request.form["id"]
        documento = request.form["documento"]
        nombre = request.form["nombre"]
        rol = request.form["rol"]
        
        # Iniciar conexión a la base de datos
        cur = mysql.connection.cursor() 
        
        # Actualizar usuario sin modificar la contraseña
        sql = """UPDATE usuarios SET 
                 documento = %s,
                 nombre = %s,
                 rol = %s
                 WHERE id = %s"""
        params = (documento, nombre, rol, id_usuario)
        
        # Ejecutar la consulta SQL
        cur.execute(sql, params)
        mysql.connection.commit()
        
        # Mostrar mensaje de éxito
        flash("Usuario actualizado exitosamente", "success")
    
    except Exception as e:
        # Capturar cualquier error
        flash(f"Error al actualizar: {str(e)}", "error")
        traceback.print_exc()
        if mysql.connection:
            mysql.connection.rollback()
    finally:
        # Cerrar el cursor si fue creado
        if cur:
            cur.close()
    
    # Redireccionar a la página de listado de usuarios
    return redirect(url_for("vista_usuarios.tabla_usuarios"))