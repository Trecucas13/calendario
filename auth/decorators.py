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

# ---------------------- Decoradores para control de acceso ---------------------- #

def login_required(route):
    """
    Decorador que verifica si el usuario ha iniciado sesión.
    
    Este decorador se aplica a rutas que requieren autenticación.
    Si el usuario no ha iniciado sesión, será redirigido a la página de login.
    
    Args:
        route (function): La función de ruta a decorar
        
    Returns:
        function: La función decorada que verifica la autenticación
    """
    @functools.wraps(route)  # Preserva los metadatos de la función original
    def router_wrapper(*args, **kwargs):
        # Verifica si el usuario NO está logueado
        if not session.get("logueado"):
            flash("Debe iniciar sesión para acceder a esta página")
            return redirect(url_for("login"))
        # Si está logueado, permite el acceso a la ruta
        return route(*args, **kwargs)

    return router_wrapper


def role_required(role):
    """
    Decorador que verifica si el usuario tiene el rol requerido para acceder a una ruta.
    
    Este decorador se aplica a rutas que requieren permisos específicos.
    Puede recibir un rol único o una lista de roles permitidos.
    
    Args:
        role (int o list): El rol o lista de roles permitidos para acceder a la ruta
        
    Returns:
        function: Un decorador que verifica el rol del usuario
    """
    def decorator(route):
        @functools.wraps(route)  # Preserva los metadatos de la función original
        def wrapper(*args, **kwargs):
            # Obtiene el rol del usuario desde la sesión
            user_role = session.get("rol")
            
            # Si role es una lista o tupla, verificar si el rol del usuario está en la lista
            if isinstance(role, (list, tuple)):
                if user_role not in role:
                    flash("No tiene permisos para acceder a esta página")
                    return redirect(url_for("login"))
            # Si role es un valor único, verificar si coincide con el rol del usuario
            elif user_role != role:
                flash("No tiene permisos para acceder a esta página")
                return redirect(url_for("login"))
                
            # Si el usuario tiene el rol requerido, permite el acceso a la ruta
            return route(*args, **kwargs)

        return wrapper

    return decorator
