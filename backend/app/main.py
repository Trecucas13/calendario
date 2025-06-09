from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from app.routers import registro_base, gestion, tipificacion

# Docstring a nivel de módulo
"""
Archivo principal de la aplicación FastAPI.

Este módulo configura y arranca la aplicación FastAPI, incluyendo:
- Creación de la instancia principal de la aplicación FastAPI.
- Configuración de plantillas Jinja2 (aunque no se usan activamente en este snippet).
- Inclusión de los routers para los diferentes endpoints de la API.
- Definición de una ruta raíz simple.

No se incluye configuración explícita de CORS en este snippet, pero sería
un lugar común para agregarla si fuera necesario.
"""

app = FastAPI(
    title="API Agendamiento Savia Salud", # Título de la API, visible en la documentación autogenerada
    version="1.0.0" # Versión de la API
)

# Configuración de plantillas Jinja2 (actualmente no parece ser utilizada activamente por los endpoints de API)
templates = Jinja2Templates(directory="templates")

# --- Inclusión de Routers ---
# Los routers definen los diferentes grupos de endpoints de la API.
# Cada router se importa desde el paquete app.routers y se incluye con un prefijo y etiquetas.
# El prefijo define la ruta base para todos los endpoints en ese router (ej: /registros).
# Las etiquetas ayudan a agrupar los endpoints en la documentación de la API (ej: Swagger UI).

app.include_router(registro_base.router, prefix="/registros", tags=["Registros"]) # Router para operaciones relacionadas con registros base
app.include_router(gestion.router, prefix="/gestiones", tags=["Gestiones"]) # Router para operaciones de gestión
app.include_router(tipificacion.router, prefix="/tipificaciones", tags=["Tipificaciones"]) # Router para operaciones de tipificación

@app.get("/")
def root():
    """
    Endpoint raíz de la API.

    Proporciona un mensaje de bienvenida simple para indicar que la API está funcionando.

    Returns:
        dict: Un diccionario con un mensaje de bienvenida.
    """
    return {"message": "API Agendamiento Savia Salud"} # Mensaje que se muestra al acceder a la raíz de la API
