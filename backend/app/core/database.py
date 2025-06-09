from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Docstring a nivel de módulo
"""
Este módulo contiene la configuración de la base de datos y la gestión de sesiones para SQLAlchemy.

Define la URL de conexión a la base de datos, crea el motor (engine) de SQLAlchemy,
establece una fábrica de sesiones (SessionLocal) para interactuar con la base de datos,
y define la clase base (Base) para los modelos declarativos de SQLAlchemy.
"""

# --- Configuración de la Conexión a la Base de Datos ---
# IMPORTANTE: Reemplaza con tus datos reales si es necesario, aunque idealmente esto vendría de variables de entorno.
DB_USER = "root"  # Usuario de la base de datos
DB_PASSWORD = ""  # Contraseña del usuario de la base de datos
DB_PORT = 3306  # Puerto donde la base de datos está escuchando
DB_HOST = "localhost"  # Host de la base de datos (ej. 'localhost' o una IP)
DB_NAME = "savia_salud"  # Nombre de la base de datos. Asegúrate que el nombre coincide exactamente.

# Construcción de la URL de la base de datos para SQLAlchemy.
# Formato: dialecto+driver://usuario:contraseña@host:puerto/nombre_base_de_datos
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- Creación del Motor y Sesión de SQLAlchemy ---

# Creación del motor (engine) de SQLAlchemy.
# El motor es el punto de partida para cualquier aplicación SQLAlchemy.
# Gestiona las conexiones a la base de datos y la ejecución de SQL.
engine = create_engine(DATABASE_URL)

# Creación de una fábrica de sesiones (SessionLocal).
# SessionLocal se utilizará para crear instancias de sesión de base de datos.
# - autocommit=False: Las transacciones no se confirman automáticamente.
# - autoflush=False: Los cambios no se envían automáticamente a la base de datos antes de las consultas.
# - bind=engine: Asocia esta fábrica de sesiones con nuestro motor de base de datos.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creación de la clase base para modelos declarativos (Base).
# Todos los modelos de la base de datos (tablas) heredarán de esta clase.
Base = declarative_base()

# Nota: La función get_db() para inyección de dependencias en FastAPI no está presente en este archivo.
# Si es necesaria, generalmente se define aquí o en un archivo de dependencias.
# Ejemplo de cómo se vería get_db:
#
# def get_db():
#     """
#     Función de dependencia para obtener una sesión de base de datos.
#
#     Esta función crea una nueva sesión de base de datos para cada solicitud
#     que la necesite y se asegura de que la sesión se cierre correctamente
#     después de que la solicitud haya terminado, incluso si ocurren errores.
#
#     Yields:
#         sqlalchemy.orm.Session: Una instancia de sesión de SQLAlchemy.
#     """
#     db = SessionLocal()
#     try:
#         yield db  # Proporciona la sesión a la operación de ruta
#     finally:
#         db.close() # Asegura que la sesión se cierre
