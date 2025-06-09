from flask import Blueprint, request, redirect, url_for, flash
from database.config import mysql # Objeto para la conexión a la base de datos.
import traceback # Para un logging de errores más detallado si fuera necesario.

# Lógica para eliminar registros de calendario o citas.
# Nota: El nombre de la función 'delete_usuario' en este archivo es engañoso,
# ya que la lógica se centra en eliminar calendarios y citas asociadas, no usuarios.

delete_calendario_bp = Blueprint('delete_calendario', __name__)
# Se renombra el Blueprint a delete_calendario_bp para consistencia y claridad.

@delete_calendario_bp.route("/eliminar_calendario", methods=['POST'])
# Asumo que esta ruta debería estar protegida por @login_required y @role_required.
# Ejemplo:
# @login_required
# @role_required(1) # O el rol apropiado para eliminar calendarios.
def delete_calendario_entries(): # Nombre de la función cambiado de delete_usuario a delete_calendario_entries para reflejar su acción.
    """
    Maneja la eliminación de un calendario y sus citas asociadas.

    Este endpoint se activa mediante una solicitud POST. Espera un 'id' en los datos del formulario,
    que se interpreta como el 'id_calendario'. Primero elimina todas las citas ('citas')
    asociadas con este 'id_calendario', y luego elimina el calendario ('calendarios') en sí.
    Si no se proporciona un ID, muestra un mensaje de error. Maneja excepciones generales
    durante el proceso de base de datos.

    Args:
        None (obtiene 'id' del `request.form`).

    Returns:
        Response: Redirige a la página '/index' después de la operación.
                  Muestra mensajes flash para indicar éxito (implícito por redirección) o error.
                  En caso de excepción, puede devolver un string 'Error al eliminar...' y código 500.
    """
    cur = None # Inicializa cur para asegurar su existencia en el bloque finally.
    try:
        # Obtiene el 'id' del calendario del formulario. Es crucial que el formulario envíe 'id'.
        id_calendario_a_eliminar = request.form.get('id')  # Usar .get() es más seguro que ['id'] para evitar KeyError.
        
        if not id_calendario_a_eliminar: # Verifica si se proporcionó el ID.
            flash('ID de calendario no proporcionado para la eliminación.', 'danger') # Mensaje de error.
            # Redirige a una página relevante, '/index' puede ser un placeholder.
            # Considerar redirigir a la página de listado de calendarios si existe.
            return redirect(url_for('index')) # El original era vista_usuarios.tabla_usuarios, lo cual parece incorrecto aquí.

        cur = mysql.connection.cursor() # Crea un cursor para la base de datos.
        
        # Primero, elimina las citas asociadas al calendario.
        # Esto es importante si hay una restricción de clave foránea (FOREIGN KEY)
        # que impida eliminar un calendario si todavía tiene citas asociadas.
        cur.execute("DELETE FROM citas WHERE id_calendario = %s", (id_calendario_a_eliminar,))
        mysql.connection.commit() # Confirma la eliminación de las citas.
        
        # Luego, elimina el calendario principal.
        cur.execute("DELETE FROM calendarios WHERE id_calendario = %s", (id_calendario_a_eliminar,))
        mysql.connection.commit() # Confirma la eliminación del calendario.
        
        # (El código original tenía un comentario '# usuario = cursor.fetchone()', que no tiene sentido aquí y se ha omitido).
        
        flash('Calendario y citas asociadas eliminados exitosamente.', 'success')
        # Redirige a la página de inicio (o idealmente, a la lista de calendarios).
        return redirect(url_for('index')) # El original era redirect('/index').
        
    except Exception as e:
        # Manejo de cualquier excepción durante el proceso.
        error_message = f"Error al eliminar el calendario: {str(e)}"
        print(error_message) # Imprime el error en la consola del servidor.
        traceback.print_exc() # Imprime el traceback completo para depuración.
        flash(error_message, 'danger') # Muestra un mensaje de error al usuario.
        if mysql.connection and mysql.connection.open: # Verifica si la conexión está activa.
            mysql.connection.rollback() # Revierte los cambios en caso de error.
        # Devuelve una respuesta de error genérica. Considerar una página de error dedicada.
        return 'Error al eliminar calendario y/o sus citas.', 500
    finally:
        # Asegura que el cursor se cierre, si fue abierto.
        if cur:
            cur.close()