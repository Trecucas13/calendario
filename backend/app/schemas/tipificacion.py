from pydantic import BaseModel

class TipificacionBase(BaseModel):
    nombre: str
    ranking: int
    tipo_contacto: str

class TipificacionResponse(TipificacionBase):
    id: str

    class Config:
        from_attributes = True
