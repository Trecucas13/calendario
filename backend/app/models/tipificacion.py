from sqlalchemy import Column, String, Integer
from app.core.database import Base
import uuid

class Tipificacion(Base):
    __tablename__ = "tipificacion"

    id = Column(Integer, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), unique=True)
    ranking = Column(Integer)  # 1,2,3,4,5,6,7,8,9,10 DONDE 0 ES LA MEJOR GESTION
    tipo_contacto = Column(String(50))  # "EFECTIVO", "NO EFECTIVO", "NO CONTACTADO"


#RANKING 