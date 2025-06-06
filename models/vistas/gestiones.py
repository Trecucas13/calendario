from flask import Flask, Blueprint, render_template, flash
from database.config import mysql
from auth.decorators import *
from auth.decorators import *
import requests
from datetime import datetime

#Ruta para hISTORICO DE GESTIONES
vista_gestiones = Blueprint('vista_gestiones', __name__)


def obtener_historico_gestiones():
    try:
        response = requests.get('http://127.0.0.1:8000/registros/listar_historico/')
        if response.status_code == 200:
            datos = response.json()
            # print(f"Datos recibidos: {len(datos)} registros")
            # Convertir string a datetime
            # for item in datos:
            #     if 'fecha_gestion' in item and item['fecha_gestion']:
            #         try:
            #             item['fecha_gestion'] = datetime.strptime(item['fecha_gestion'], '%Y-%m-%d %H:%M:%S')
            #         except ValueError as e:
            #             print(f"Error al convertir fecha: {e}")
            #             item['fecha_gestion'] = None
            return datos
        else:
            print(f"Error en la API: Status code {response.status_code}")
            return []
    except Exception as e:
        print(f"Error en la conexión: {e}")
        return []


def obtener_total_gestiones():
    try:
        response = requests.get('http://127.0.0.1:8000/registros/completo/')
        if response.status_code == 200:
            datos = response.json()
            print(f"Datos recibidos: {len(datos)} registros")
            # Convertir string a datetime
            for item in datos:
                if 'fecha_gestion' in item and item['fecha_gestion']:
                    try:
                        item['fecha_gestion'] = datetime.strptime(item['fecha_gestion'], '%Y-%m-%d %H:%M:%S')
                    except ValueError as e:
                        print(f"Error al convertir fecha: {e}")
                        item['fecha_gestion'] = None
            return datos
        else:
            print(f"Error en la API: Status code {response.status_code}")
            return []
    except Exception as e:
        print(f"Error en la conexión: {e}")
        return []




def obtener_tipificaciones():
    try:
        response = requests.get('http://127.0.0.1:8000/tipificaciones/lista_tipificaciones/')
        if response.status_code == 200:
            datos = response.json()
            print(f"Datos recibidos: {len(datos)} registros")
            # Convertir string a datetime
            # for item in datos:
            #     if 'fecha_gestion' in item and item['fecha_gestion']:
            #         try:
            #             item['fecha_gestion'] = datetime.strptime(item['fecha_gestion'], '%Y-%m-%d %H:%M:%S')
            #         except ValueError as e:
            #             print(f"Error al convertir fecha: {e}")
            #             item['fecha_gestion'] = None
        return datos
    except Exception as e:
        print(f"Error en la conexión: {e}")
        return []



def obtener_gestiones_bd():
    try:
        response = requests.get('http://127.0.0.1:8000/gestiones/gestion_bd/')
        if response.status_code == 200:
            datos = response.json()
            
            print(f"Datos recibidos: {len(datos)} registros")
            # Convertir string a datetime
            # for item in datos:
            #     if 'fecha_gestion' in item and item['fecha_gestion']:
            #         try:
            #             item['fecha_gestion'] = datetime.strptime(item['fecha_gestion'], '%Y-%m-%d %H:%M:%S')
            #         except ValueError as e:
            #             print(f"Error al convertir fecha: {e}")
            #             item['fecha_gestion'] = None
            # print(datos)
            return datos
        else:
            print(f"Error en la API: Status code {response.status_code}")
            return []
    except Exception as e:
        print(f"Error en la conexión: {e}")
        return []


@vista_gestiones.route("/Historico_gestiones")
@login_required
@role_required([1 , 2])
def tabla_gestiones():
    historial = obtener_historico_gestiones()
    tipificaciones = obtener_tipificaciones()
    print(historial)
    return render_template("historico_gestiones.html", historico=historial, tipificaciones=tipificaciones)

    
#Ruta para Gestion BD
gestion_bd = Blueprint('gestion_bd', __name__)

@gestion_bd.route("/gestion_bd")
@login_required
@role_required([1 , 2])
def tabla_gestiones():
    historial = obtener_gestiones_bd()
    print(historial)
    return render_template("gestion_bd.html", historico = historial)

#Ruta para Gestionar
gestionar = Blueprint('gestionar', __name__)

@gestionar.route("/gestionar")
@login_required
@role_required([1 , 2])
def tabla_gestiones():
    gestiones = obtener_total_gestiones()
    tipificaciones = obtener_tipificaciones()
    
    
    print(tipificaciones)
    return render_template("gestionar.html", gestiones=gestiones, tipificaciones=tipificaciones)


