from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GestionCreate(BaseModel):
    registro_id: str
    tipificacion: str
    comentario: Optional[str] = None
    id_llamada: Optional[str] = None
    usuario: str

class GestionResponse(GestionCreate):
    id: str
    fecha_gestion: datetime

    class Config:
        from_attributes = True

class GestionHistorico(BaseModel):
    tipo_id: str
    num_id: str
    primer_nombre: str
    segundo_nombre: Optional[str]
    primer_apellido: str
    segundo_apellido: Optional[str]
    proceso: str
    tipificacion: str
    tipo_contacto: str
    comentario: Optional[str]
    id_llamada: Optional[str]
    fecha_gestion: datetime
    usuario: str
    

    class Config:
        from_attributes = True