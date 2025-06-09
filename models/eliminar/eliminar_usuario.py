from flask import Blueprint, request, redirect, url_for, flash
from database.config import mysql # Objeto para la conexión a la base de datos.
import traceback # Para un logging de errores más detallado si fuera necesario.

# Lógica para eliminar registros de usuarios.

delete_usuarios_bp = Blueprint('delete_usuarios', __name__)
# Se renombra el Blueprint a delete_usuarios_bp para consistencia y claridad.

@delete_usuarios_bp.route("/eliminar_usuario", methods=['POST'])
# Asumo que esta ruta debería estar protegida por @login_required y @role_required.
# Ejemplo:
# @login_required
# @role_required(1) # Solo administradores pueden eliminar usuarios.
def delete_usuario():
    """
    Maneja la eliminación de un usuario y sus datos asociados (citas y calendarios).

    Este endpoint se activa mediante una solicitud POST. Espera un 'id' del usuario
    en los datos del formulario. Procede a eliminar:
    1. Todas las citas ('citas') asociadas con el 'id_usuario'.
    2. Todos los calendarios ('calendarios') asociados con el 'id_usuario'.
    3. Finalmente, el registro del usuario ('usuarios') mismo.

    Si no se proporciona un ID, muestra un mensaje de error y redirige.
    Maneja excepciones generales durante el proceso de base de datos, realizando un rollback
    en caso de error.

    Args:
        None (obtiene 'id' del `request.form`).

    Returns:
        Response: Redirige a la tabla de usuarios (endpoint 'vista_usuarios.tabla_usuarios')
                  después de la operación.
                  Muestra mensajes flash para indicar éxito (implícito por redirección) o error.
                  En caso de excepción, puede devolver un string 'Error al eliminar usuario' y código 500.
    """
    cur = None # Inicializa cur para asegurar su existencia en el bloque finally.
    try:
        # Obtiene el 'id' del usuario del formulario.
        id_usuario_a_eliminar = request.form.get('id')  # Usar .get() es más seguro.

        if not id_usuario_a_eliminar: # Verifica si se proporcionó el ID.
            flash('ID de usuario no proporcionado para la eliminación.', 'danger') # Mensaje de error.
            return redirect(url_for('vista_usuarios.tabla_usuarios'))  # Redirige a la lista de usuarios.

        cur = mysql.connection.cursor() # Crea un cursor para la base de datos.
        
        # Eliminar las citas asociadas al usuario.
        # Es importante hacer esto antes de eliminar el usuario si hay restricciones FK.
        cur.execute("DELETE FROM citas WHERE id_usuario = %s", (id_usuario_a_eliminar,))
        mysql.connection.commit() # Confirma la eliminación de las citas.
        
        # Eliminar los calendarios asociados al usuario.
        # Similarmente, esto debería hacerse antes de eliminar el usuario si hay dependencias.
        cur.execute("DELETE FROM calendarios WHERE id_usuario = %s", (id_usuario_a_eliminar,))
        mysql.connection.commit() # Confirma la eliminación de los calendarios.
        
        # (El código original tenía un comentario '# usuario = cursor.fetchone()', que no es relevante para DELETE).
        
        # Finalmente, eliminar el usuario de la tabla 'usuarios'.
        cur.execute("DELETE FROM usuarios WHERE id = %s", (id_usuario_a_eliminar,))
        mysql.connection.commit() # Confirma la eliminación del usuario.
        
        flash('Usuario y datos asociados eliminados exitosamente.', 'success')
        # Redirige a la lista de usuarios.
        return redirect(url_for('vista_usuarios.tabla_usuarios'))
        
    except Exception as e:
        # Manejo de cualquier excepción durante el proceso.
        error_message = f"Error al eliminar el usuario: {str(e)}"
        print(error_message) # Imprime el error en la consola.
        traceback.print_exc() # Imprime el traceback completo para depuración.
        flash(error_message, 'danger') # Muestra un mensaje de error al usuario.
        if mysql.connection and mysql.connection.open: # Verifica si la conexión está activa.
            mysql.connection.rollback() # Revierte los cambios en caso de error.
        # Devuelve una respuesta de error genérica.
        return 'Error al eliminar usuario y/o sus datos asociados.', 500
    finally:
        # Asegura que el cursor se cierre, si fue abierto.
        if cur:
            cur.close()