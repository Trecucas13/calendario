from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from app.routers import registro_base, gestion, tipificacion

app = FastAPI(
    title="API Agendamiento Savia Salud",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")

# Incluir routers
app.include_router(registro_base.router, prefix="/registros", tags=["Registros"])
app.include_router(gestion.router, prefix="/gestiones", tags=["Gestiones"])
app.include_router(tipificacion.router, prefix="/tipificaciones", tags=["Tipificaciones"])

@app.get("/")
def root():
    return {"message": "API Agendamiento Savia Salud"}
