from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# IMPORTANTE: Reemplaza con tus datos reales
DB_USER = "root"
DB_PASSWORD = "tu_contraseña"
DB_HOST = "localhost"
DB_NAME = "nombre_de_tu_bd"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
