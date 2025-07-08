from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify
from database.config import db
from sqlalchemy import text
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
    try:
        usuario = db.session.execute(
            text("""
                SELECT id, documento, nombre, rol
                FROM usuarios 
                WHERE id = :id
            """), {"id": id}
        ).fetchone()
        if usuario:
            # Acceso por índice, ya que fetchone() devuelve una tupla
            return jsonify({
                'id': usuario[0],
                'documento': usuario[1],
                'nombre': usuario[2],
                'rol': usuario[3]
            }), 200
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@actualizar_usuario.route("/actualizar_usuario", methods=["POST"])
def update_usuario():
    """
    Función que maneja la actualización de datos de un usuario en la base de datos.
    No actualiza la contraseña.
    """
    try:
        # Obtener datos del formulario
        id_usuario = request.form["id"]
        documento = request.form["documento"]
        nombre = request.form["nombre"]
        rol = request.form["rol"]

        # Actualizar usuario sin modificar la contraseña
        sql = text("""UPDATE usuarios SET 
                 documento = :documento,
                 nombre = :nombre,
                 rol = :rol
                 WHERE id = :id_usuario""")
        params = {
            "documento": documento,
            "nombre": nombre,
            "rol": rol,
            "id_usuario": id_usuario
        }

        db.session.execute(sql, params)
        db.session.commit()

        # Mostrar mensaje de éxito
        flash("Usuario actualizado exitosamente", "success")

    except Exception as e:
        # Capturar cualquier error
        db.session.rollback()
        flash(f"Error al actualizar: {str(e)}", "error")
        traceback.print_exc()

    # Redireccionar a la página de listado de usuarios
    return redirect(url_for("vista_usuarios.tabla_usuarios"))