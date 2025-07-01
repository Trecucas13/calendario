from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# IMPORTANTE: Reemplaza con tus datos reales
DB_USER = "root"
DB_PASSWORD = "rootpass"
DB_PORT = 3306
DB_HOST = "mysql"
DB_NAME = "savia_salud"  # Asegúrate que el nombre coincide exactamente

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
