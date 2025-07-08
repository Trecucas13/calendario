# Importación de módulos necesarios
import os
from flask_sqlalchemy import SQLAlchemy


# Inicialización del objeto SQLAlchemy
db = SQLAlchemy()


def db_conexion(app):
    """
    Configura la conexión a la base de datos PostgreSQL para la aplicación Flask.
    Utiliza variables de entorno para la configuración, con valores por defecto si no están definidas.
    """
    # Configuración básica de conexión
    # HOST: Dirección del servidor PostgreSQL (por defecto: localhost)
    db_host = os.getenv("POSTGRES_HOST", "database-savia.cla22m8co2v1.us-east-1.rds.amazonaws.com")
    # USER: Usuario de PostgreSQL (por defecto: postgres)
    db_user = os.getenv("POSTGRES_USER", "postgres")
    # PASSWORD: Contraseña del usuario PostgreSQL (por defecto: postgres)
    db_password = os.getenv("POSTGRES_PASSWORD", "89.J(GIidcx2^P9G")
    # DB: Nombre de la base de datos a utilizar (por defecto: savia_salud)
    db_name = os.getenv("POSTGRES_DB", "postgres")
    # Puerto de conexión PostgreSQL (por defecto: 5432)
    db_port = os.getenv("POSTGRES_PORT", "5432")

    # Construcción de la URI de conexión para SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    # Desactivar el seguimiento de modificaciones para mejorar el rendimiento
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Clave secreta para sesiones y tokens CSRF (por defecto: 1234567890)
    app.secret_key = os.getenv("SECRET_KEY", "1234567890")

    # Inicialización de la extensión SQLAlchemy con la configuración establecida
    db.init_app(app)