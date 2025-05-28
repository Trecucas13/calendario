from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

# ✅ Schema para creación individual
class RegistroBaseCreate(BaseModel):
    tipo_id: str
    num_id: int
    primer_nombre: str
    segundo_nombre: Optional[str] = None
    primer_apellido: str
    segundo_apellido: Optional[str] = None
    fecha: date
    edad: int
    estado_afiliacion: str
    regimen_afiliacion: str
    telefonos: str
    direccion: str
    municipio: str
    subregion: str
    proceso: str

# ✅ Schema para respuesta individual
class RegistroBaseResponse(RegistroBaseCreate):
    id: int
    fecha_carga: datetime

    class Config:
        from_attributes = True

# ✅ Schema extendido con mejor gestión
class MejorGestion(BaseModel):
    tipificacion: str
    tipo_contacto: str
    usuario: str
    fecha_gestion: str
    mes: str
    cantidad: int

class RegistroConGestion(BaseModel):
    id: int
    tipo_id: int
    num_id: str
    primer_nombre: str
    segundo_nombre: Optional[str]
    primer_apellido: str
    segundo_apellido: Optional[str]
    fecha: date
    edad: int
    estado_afiliacion: str
    regimen_afiliacion: str
    telefonos: str
    direccion: str
    municipio: str
    subregion: str
    proceso: str
    mejor_gestion: MejorGestion

    class Config:
        from_attributes = True
