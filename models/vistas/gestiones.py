from flask import Flask, Blueprint, render_template, flash # Flask, flash no se usan directamente.
# from database.config import mysql # mysql no se usa directamente en este archivo.
from auth.decorators import login_required, role_required # Decoradores para control de acceso.
# from auth.decorators import * # La segunda importación de auth.decorators es redundante.
import requests # Para realizar solicitudes HTTP a la API backend.
from datetime import datetime # Para manipulación de fechas (aunque el formateo está comentado).
import traceback # Para logging de errores.

# Lógica para generar vistas de gestiones o interacciones.
# Este módulo consume datos de una API (presumiblemente el backend FastAPI de este proyecto)
# para renderizar diferentes vistas relacionadas con las gestiones.

# --- Blueprints ---
# Blueprint para la vista del histórico de gestiones.
vista_gestiones_bp = Blueprint('vista_gestiones', __name__, template_folder='templates')
# Blueprint para la vista de "Gestión BD".
gestion_bd_bp = Blueprint('gestion_bd', __name__, template_folder='templates')
# Blueprint para la vista principal de "Gestionar".
gestionar_bp = Blueprint('gestionar', __name__, template_folder='templates')


# --- Funciones Auxiliares para Obtener Datos de la API ---

def obtener_historico_gestiones():
    """
    Obtiene el historial de gestiones desde el endpoint de la API `/registros/listar_historico/`.

    Returns:
        list: Una lista de gestiones obtenidas de la API.
              Retorna una lista vacía si hay un error en la solicitud o la API no responde correctamente.
    """
    try:
        # Realiza una solicitud GET al endpoint de la API que lista el histórico de registros/gestiones.
        response = requests.get('http://127.0.0.1:8000/registros/listar_historico/')
        if response.status_code == 200: # Si la solicitud fue exitosa.
            datos = response.json() # Convierte la respuesta JSON en un objeto Python (lista de diccionarios).
            # La conversión de fechas está comentada en el original, se mantiene así.
            # Podría ser útil si las fechas necesitan ser objetos datetime en la plantilla.
            # for item in datos:
            #     if 'fecha_gestion' in item and item['fecha_gestion']:
            #         try:
            #             item['fecha_gestion'] = datetime.strptime(item['fecha_gestion'], '%Y-%m-%d %H:%M:%S')
            #         except ValueError as e:
            #             print(f"Error al convertir fecha: {e}")
            #             item['fecha_gestion'] = None
            return datos
        else:
            # Si la API devuelve un código de estado de error.
            print(f"Error al obtener histórico de gestiones desde API: Status code {response.status_code}")
            return []
    except requests.exceptions.RequestException as e: # Captura errores de conexión o de la solicitud.
        print(f"Error de conexión al obtener histórico de gestiones: {e}")
        traceback.print_exc()
        return []
    except Exception as e: # Captura cualquier otro error inesperado.
        print(f"Error inesperado en obtener_historico_gestiones: {e}")
        traceback.print_exc()
        return []


def obtener_total_gestiones():
    """
    Obtiene los datos completos de registros/gestiones desde el endpoint `/registros/completo/`.

    Returns:
        list: Una lista de datos de registros/gestiones.
              Retorna una lista vacía en caso de error.
    """
    try:
        response = requests.get('http://127.0.0.1:8000/registros/completo/')
        if response.status_code == 200:
            datos = response.json()
            # print(f"Datos recibidos en obtener_total_gestiones: {len(datos)} registros") # Log útil.
            # Conversión de fechas comentada en el original, se respeta.
            for item in datos: # Este bucle se ejecuta aunque la conversión esté comentada.
                if 'fecha_gestion' in item and item['fecha_gestion']:
                    try:
                        # Si se necesitara la conversión:
                        # item['fecha_gestion'] = datetime.strptime(item['fecha_gestion'], '%Y-%m-%d %H:%M:%S')
                        pass # Manteniendo la lógica original de no convertir aquí.
                    except ValueError as e:
                        print(f"Error al convertir fecha en obtener_total_gestiones: {e}")
                        item['fecha_gestion'] = None # Asigna None si la conversión falla.
            return datos
        else:
            print(f"Error al obtener total de gestiones desde API: Status code {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión al obtener total de gestiones: {e}")
        traceback.print_exc()
        return []
    except Exception as e:
        print(f"Error inesperado en obtener_total_gestiones: {e}")
        traceback.print_exc()
        return []


def obtener_tipificaciones():
    """
    Obtiene la lista de tipificaciones desde el endpoint `/tipificaciones/lista_tipificaciones/`.

    Returns:
        list: Una lista de tipificaciones.
              Retorna una lista vacía en caso de error.
    """
    try:
        response = requests.get('http://127.0.0.1:8000/tipificaciones/lista_tipificaciones/')
        if response.status_code == 200:
            datos = response.json()
            # print(f"Tipificaciones recibidas: {len(datos)} registros") # Log útil.
            return datos
        else:
            print(f"Error al obtener tipificaciones desde API: Status code {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión al obtener tipificaciones: {e}")
        traceback.print_exc()
        return []
    except Exception as e:
        print(f"Error inesperado en obtener_tipificaciones: {e}")
        traceback.print_exc()
        return []


def obtener_gestiones_bd(): # El nombre sugiere que obtiene gestiones de "BD", pero llama a un endpoint.
    """
    Obtiene datos de gestiones desde el endpoint `/gestiones/gestion_bd/`.
    El nombre de la función "obtener_gestiones_bd" podría ser confuso ya que interactúa
    con una API, no directamente con una BD desde este módulo.

    Returns:
        list: Una lista de datos de gestiones.
              Retorna una lista vacía en caso de error.
    """
    try:
        response = requests.get('http://127.0.0.1:8000/gestiones/gestion_bd/')
        if response.status_code == 200:
            datos = response.json()
            # print(f"Datos de gestion_bd recibidos: {len(datos)} registros") # Log útil.
            return datos
        else:
            print(f"Error al obtener gestiones_bd desde API: Status code {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión al obtener gestiones_bd: {e}")
        traceback.print_exc()
        return []
    except Exception as e:
        print(f"Error inesperado en obtener_gestiones_bd: {e}")
        traceback.print_exc()
        return []

# --- Rutas y Vistas ---

@vista_gestiones_bp.route("/Historico_gestiones")
@login_required # Requiere que el usuario haya iniciado sesión.
@role_required([1 , 2]) # Permite acceso a roles 1 (Admin) y 2 (Usuario).
def mostrar_historico_gestiones(): # Nombre de función cambiado para evitar colisión.
    """
    Renderiza la página del historial de gestiones.

    Obtiene el historial de gestiones y la lista de tipificaciones llamando
    a las funciones auxiliares que consumen la API. Pasa estos datos a la
    plantilla 'historico_gestiones.html'.

    Returns:
        Response: El contenido HTML renderizado de la página del historial de gestiones.
    """
    historial = obtener_historico_gestiones() # Llama a la función auxiliar.
    tipificaciones = obtener_tipificaciones() # Llama a la función auxiliar.
    # print(f"Historial para plantilla: {historial}") # Log para depuración.
    return render_template("historico_gestiones.html", historico=historial, tipificaciones=tipificaciones)

    
@gestion_bd_bp.route("/gestion_bd")
@login_required
@role_required([1 , 2])
def mostrar_gestion_bd(): # Nombre de función cambiado.
    """
    Renderiza la página de "Gestión BD".

    Obtiene los datos de gestiones llamando a `obtener_gestiones_bd()` y los
    pasa a la plantilla 'gestion_bd.html'.

    Returns:
        Response: El contenido HTML renderizado de la página de Gestión BD.
    """
    historial = obtener_gestiones_bd() # Llama a la función auxiliar.
    # print(f"Datos para gestion_bd.html: {historial}") # Log para depuración.
    return render_template("gestion_bd.html", historico=historial)


@gestionar_bp.route("/gestionar")
@login_required
@role_required([1 , 2])
def mostrar_pagina_gestionar(): # Nombre de función cambiado.
    """
    Renderiza la página principal para "Gestionar".

    Obtiene el total de gestiones (o registros completos) y la lista de tipificaciones
    llamando a las funciones auxiliares. Pasa estos datos a la plantilla 'gestionar.html'.

    Returns:
        Response: El contenido HTML renderizado de la página de gestionar.
    """
    gestiones = obtener_total_gestiones() # Llama a la función auxiliar.
    tipificaciones = obtener_tipificaciones() # Llama a la función auxiliar.
    # print(f"Tipificaciones para gestionar.html: {tipificaciones}") # Log para depuración.
    return render_template("gestionar.html", gestiones=gestiones, tipificaciones=tipificaciones)


