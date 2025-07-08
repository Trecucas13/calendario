from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# IMPORTANTE: Reemplaza con tus datos reales
DB_USER = "postgres"  # Usuario de la base de datos
DB_PASSWORD = "89.J(GIidcx2^P9G"
DB_PORT = "5432"  # Puerto por defecto de MySQL
DB_HOST = "database-savia.cla22m8co2v1.us-east-1.rds.amazonaws.com"
DB_NAME = "postgres"  # Asegúrate que el nombre coincide exactamente

DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
