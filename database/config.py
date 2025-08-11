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
    db_host = os.getenv("POSTGRES_HOST")
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")
    db_port = os.getenv("POSTGRES_PORT")

    db_host = 'database-savia.cla22m8co2v1.us-east-1.rds.amazonaws.com'
    db_user = 'postgres'
    db_password = '89.J(GIidcx2^P9G'
    db_name = 'postgres'
    db_port = '5432'


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