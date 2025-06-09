# Importaciones necesarias de Flask
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    session,
    Response,
    flash,
)

# Importación de functools para crear decoradores
import functools

# Docstring a nivel de módulo
"""
Este módulo contiene decoradores personalizados para la aplicación Flask.
Estos decoradores se utilizan principalmente para proteger rutas, verificando
si un usuario ha iniciado sesión (login_required) o si tiene un rol específico
necesario para acceder a ciertas funcionalidades (role_required).
"""

# ---------------------- Decoradores para control de acceso ---------------------- #

def login_required(route):
    """
    Decorador que verifica si un usuario ha iniciado sesión.

    Este decorador se aplica a las funciones de vista (rutas) que requieren
    que el usuario esté autenticado. Si el usuario no ha iniciado sesión
    (es decir, la clave 'logueado' no está en la sesión o es False),
    se muestra un mensaje flash y se le redirige a la página de inicio de sesión.

    Args:
        route (function): La función de vista (ruta) que se va a decorar.

    Returns:
        function: La función decorada, que incluye la lógica de verificación
                  de inicio de sesión antes de ejecutar la ruta original.
    """
    @functools.wraps(route)  # Preserva metadatos de la función original como el nombre y docstring
    def router_wrapper(*args, **kwargs):
        # Verifica si la clave 'logueado' no está en la sesión o no es True
        if not session.get("logueado"):
            flash("Debe iniciar sesión para acceder a esta página") # Muestra un mensaje al usuario
            return redirect(url_for("login")) # Redirige a la página de login
        # Si el usuario está logueado, ejecuta la función de vista original
        return route(*args, **kwargs)

    return router_wrapper


def role_required(role):
    """
    Decorador que verifica si el usuario tiene el rol o roles requeridos para acceder a una ruta.

    Este decorador toma un argumento `role`, que puede ser un único rol (int) o una
    lista/tupla de roles permitidos. Comprueba el rol del usuario almacenado en la
    sesión. Si el usuario no tiene el rol adecuado, se muestra un mensaje flash y
    se le redirige a la página de inicio de sesión (o a una página de acceso denegado,
    según la implementación deseada, aquí se usa 'login').

    Args:
        role (int or list or tuple): El rol (o lista/tupla de roles) requerido
                                     para acceder a la ruta.

    Returns:
        function: Una función decoradora que, a su vez, decora la función de vista.
                  La función de vista decorada incluirá la lógica de verificación de roles.
    """
    def decorator(route):
        @functools.wraps(route)  # Preserva metadatos de la función original
        def wrapper(*args, **kwargs):
            # Obtiene el rol del usuario desde la sesión. Retorna None si no existe.
            user_role = session.get("rol")
            
            # Verifica si el 'role' proporcionado es una lista o tupla (múltiples roles permitidos)
            if isinstance(role, (list, tuple)):
                if user_role not in role: # Si el rol del usuario no está en la lista de roles permitidos
                    flash("No tiene permisos para acceder a esta página") # Muestra mensaje de error
                    return redirect(url_for("login")) # Redirige a login
            # Si 'role' es un valor único (un solo rol permitido)
            elif user_role != role: # Si el rol del usuario no coincide con el rol requerido
                flash("No tiene permisos para acceder a esta página") # Muestra mensaje de error
                return redirect(url_for("login")) # Redirige a login
                
            # Si el usuario tiene el rol requerido, permite el acceso a la ruta original
            return route(*args, **kwargs)

        return wrapper

    return decorator
