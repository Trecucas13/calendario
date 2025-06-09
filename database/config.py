# Importación de módulos necesarios
import os # Para acceder a variables de entorno.
from flask_mysqldb import MySQL # Extensión Flask para la integración con MySQL.

# Docstring a nivel de módulo
"""
Este archivo maneja la configuración de la conexión a la base de datos MySQL
para la aplicación Flask.

Utiliza la extensión Flask-MySQLDB y configura los parámetros de conexión
leyendo variables de entorno, con valores por defecto proporcionados
en caso de que las variables de entorno no estén definidas. También inicializa
el objeto `mysql` que será utilizado por la aplicación para interactuar con
la base de datos.
"""

# Inicialización del objeto MySQL.
# Esta instancia de `MySQL` será configurada y asociada con la aplicación Flask
# dentro de la función `db_conexion`.
mysql = MySQL()


def db_conexion(app):
    """
    Configura la conexión a la base de datos MySQL para la aplicación Flask.

    Esta función toma una instancia de la aplicación Flask y establece
    varias opciones de configuración para Flask-MySQLDB. Lee los valores de
    las variables de entorno para parámetros como el host, usuario, contraseña,
    nombre de la base de datos y puerto. Si las variables de entorno no están
    disponibles, se utilizan valores por defecto. Finalmente, inicializa
    la extensión `mysql` con la aplicación Flask configurada.

    Args:
        app (Flask): La instancia de la aplicación Flask.

    Returns:
        None: La función modifica el objeto `app` directamente y el objeto global `mysql`.
    """
    # --- Configuración básica de conexión ---
    # HOST: Dirección del servidor MySQL.
    app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST", "localhost") # Valor por defecto: 'localhost'
    # USER: Usuario de MySQL.
    app.config["MYSQL_USER"] = os.getenv("MYSQL_USER", "root") # Valor por defecto: 'root'
    # PASSWORD: Contraseña del usuario MySQL.
    app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "") # Valor por defecto: cadena vacía
    # DB: Nombre de la base de datos a utilizar.
    app.config["MYSQL_DB"] = os.getenv("MYSQL_DB", "savia_salud") # Valor por defecto: 'savia_salud' (anteriormente 'kliiker')

    # --- Configuración avanzada de MySQL ---
    # Puerto de conexión MySQL.
    app.config["MYSQL_PORT"] = int(os.getenv("MYSQL_PORT", 3306)) # Valor por defecto: 3306
    # Socket Unix para conexiones locales (generalmente None si se usa HOST y PORT).
    app.config["MYSQL_UNIX_SOCKET"] = None
    # Tiempo máximo de espera para la conexión en segundos.
    app.config["MYSQL_CONNECT_TIMEOUT"] = int(os.getenv("MYSQL_CONNECT_TIMEOUT", 10)) # Valor por defecto: 10 segundos
    # Archivo de configuración MySQL adicional (ej. my.cnf).
    app.config["MYSQL_READ_DEFAULT_FILE"] = None
    # Habilitar soporte para caracteres Unicode.
    app.config["MYSQL_USE_UNICODE"] = True
    # Codificación de caracteres (utf8mb4 es recomendada para soporte completo de Unicode).
    app.config["MYSQL_CHARSET"] = "utf8mb4"
    # Modo SQL personalizado (ej. 'TRADITIONAL', 'STRICT_TRANS_TABLES').
    app.config["MYSQL_SQL_MODE"] = None
    # Tipo de cursor. 'DictCursor' devuelve filas como diccionarios Python.
    app.config["MYSQL_CURSORCLASS"] = "DictCursor"
    # Desactivar autocommit para permitir control manual de transacciones (BEGIN, COMMIT, ROLLBACK).
    app.config["MYSQL_AUTOCOMMIT"] = False
    # Modo SSL para conexiones seguras (ej. "PREFERRED", "REQUIRED").
    app.config["MYSQL_SSL_MODE"] = os.getenv("MYSQL_SSL_MODE", None) # Valor por defecto: None

    # Clave secreta para la aplicación Flask, utilizada para sesiones, cookies seguras, tokens CSRF, etc.
    # Es crucial que sea un valor fuerte y secreto en producción.
    app.secret_key = os.getenv("SECRET_KEY", "1234567890") # Valor por defecto: '1234567890' (cambiar en producción)

    # Inicialización de la extensión MySQL con la configuración de la aplicación establecida.
    mysql.init_app(app)

# Nota: La línea `mysql = MySQL()` al final del archivo original es redundante
# porque `mysql` ya se inicializa al principio del archivo.
# Se mantiene si es una convención específica del proyecto, pero usualmente una sola inicialización es suficiente.
# Si esta segunda inicialización es intencional y tiene un propósito específico no obvio,
# merecería un comentario explicando su razón de ser. De lo contrario, podría eliminarse.
mysql = MySQL() # Esta línea es redundante, la instancia `mysql` ya fue creada arriba.