# Importación de módulos necesarios
import os
from flask_mysqldb import MySQL


# Inicialización del objeto MySQL
mysql = MySQL()


def db_conexion(app):
    """
    Configura la conexión a la base de datos MySQL para la aplicación Flask.
    Utiliza variables de entorno para la configuración, con valores por defecto si no están definidas.
    """
    # Configuración básica de conexión
    # HOST: Dirección del servidor MySQL (por defecto: localhost)
    app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST", "localhost")
    # USER: Usuario de MySQL (por defecto: root)
    app.config["MYSQL_USER"] = os.getenv("MYSQL_USER", "root")
    # PASSWORD: Contraseña del usuario MySQL (por defecto: vacío)
    app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "")
    # DB: Nombre de la base de datos a utilizar (por defecto: kliiker)
    app.config["MYSQL_DB"] = os.getenv("MYSQL_DB", "savia_salud")

    # Configuración avanzada de MySQL
    # Puerto de conexión MySQL (por defecto: 3306)
    app.config["MYSQL_PORT"] = int(os.getenv("MYSQL_PORT", 3306))
    # Socket Unix para conexiones locales
    app.config["MYSQL_UNIX_SOCKET"] = None
    # Tiempo máximo de espera para la conexión en segundos
    app.config["MYSQL_CONNECT_TIMEOUT"] = int(os.getenv("MYSQL_CONNECT_TIMEOUT", 10))
    # Archivo de configuración MySQL adicional
    app.config["MYSQL_READ_DEFAULT_FILE"] = None
    # Soporte para caracteres Unicode
    app.config["MYSQL_USE_UNICODE"] = True
    # Codificación de caracteres (utf8mb4 soporta emojis y caracteres especiales)
    app.config["MYSQL_CHARSET"] = "utf8mb4"
    # Modo SQL personalizado
    app.config["MYSQL_SQL_MODE"] = None
    # Tipo de cursor (DictCursor retorna resultados como diccionarios)
    app.config["MYSQL_CURSORCLASS"] = "DictCursor"
    # Desactivar autocommit para control manual de transacciones
    app.config["MYSQL_AUTOCOMMIT"] = False
    # Modo SSL para conexiones seguras
    app.config["MYSQL_SSL_MODE"] = os.getenv("MYSQL_SSL_MODE", None)

    # Clave secreta para sesiones y tokens CSRF (por defecto: 1234567890)
    app.secret_key = os.getenv("SECRET_KEY", "1234567890")

    # Inicialización de la extensión MySQL con la configuración establecida
    mysql.init_app(app)


mysql = MySQL()