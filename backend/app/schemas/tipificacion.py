from pydantic import BaseModel

class TipificacionBase(BaseModel):
    nombre: str
    ranking: int
    tipo_contacto: str

class TipificacionResponse(TipificacionBase):
    id: int

    class Config:
        from_attributes = True
